"""Resume mediciones reales de las corridas y genera figuras comparables."""
import csv
from pathlib import Path

import numpy as np

from analysis import curves, evolution, regularization
from gan.utils import save_json


def main():
    summaries = []
    configs = []
    import json
    for name in ["base", "exp_loss_hinge", "exp_stab_sn"]:
        run = Path("runs") / name
        config = json.loads((run / "config.json").read_text(encoding="utf-8"))
        configs.append(config)
        with (run / "metrics.csv").open(newline="", encoding="utf-8") as stream:
            all_rows = list(csv.DictReader(stream))
        rows = [row for row in all_rows if row["loss_d"]]
        if len(rows) != config["epochs"]:
            raise ValueError(f"{name}: corrida incompleta.")
        evaluated = [row for row in rows if row["diversity"]]
        tail = rows[-20:]
        entry = {"run": name, "epochs": len(rows), "loss": config["loss"], "spectral": config["spectral"],
                 "final_loss_d": float(rows[-1]["loss_d"]), "final_loss_g": float(rows[-1]["loss_g"]),
                 "final_d_real": float(rows[-1]["d_real"]), "final_d_fake": float(rows[-1]["d_fake"]),
                 "final_diversity": float(evaluated[-1]["diversity"]),
                 "tail_diversity_mean": float(np.mean([float(row["diversity"]) for row in evaluated[-3:]])),
                 "tail_loss_d_std": float(np.std([float(row["loss_d"]) for row in tail])),
                 "tail_loss_d_mean": float(np.mean([float(row["loss_d"]) for row in tail])),
                 "seconds": float(rows[-1]["seconds"])}
        summaries.append(entry)
        curves(run)
        evolution(run, [0, 5, 20, 40, config["epochs"]])
    base, hinge, spectral = summaries
    for entry in [hinge, spectral]:
        entry["diversity_ratio_vs_base"] = entry["tail_diversity_mean"] / base["tail_diversity_mean"]
    hinge["quantitative_diversity_condition"] = hinge["diversity_ratio_vs_base"] >= 0.9
    spectral["quantitative_stability_condition"] = (spectral["tail_loss_d_std"] < base["tail_loss_d_std"]
                                                      and spectral["diversity_ratio_vs_base"] >= 0.9)
    out = Path("evidencias")
    out.mkdir(exist_ok=True)
    save_json({"runs": summaries, "visual_review_required": True,
               "note": "Las condiciones cuantitativas no sustituyen el criterio visual registrado en la hipótesis."},
              out / "resumen_experimentos.json")
    for name in ["refined", "moment_refined", "conditional", "conditional_refined"]:
        refined = Path("runs") / name
        if (refined / "ckpt/G_final.pt").exists():
            curves(refined)
            config = json.loads((refined / "config.json").read_text(encoding="utf-8"))
            epochs = list(dict.fromkeys([0, 5, 20, config["epochs"] // 2, config["epochs"]]))
            evolution(refined, epochs)
            if (refined / "regularization.csv").exists():
                regularization(refined)
    print(summaries)


if __name__ == "__main__":
    main()
