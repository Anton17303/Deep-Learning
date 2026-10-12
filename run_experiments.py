"""Ejecuta tres corridas controladas sin repetir una base terminada."""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

from gan.images import ImageDataset


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/processed")
    p.add_argument("--epochs", type=int, default=60)
    p.add_argument("--threads", type=int, default=4)
    a = p.parse_args()
    dataset_hash = ImageDataset(a.data).fingerprint()
    for name, changes in [("base", []), ("exp_loss_hinge", ["--loss", "hinge"]),
                          ("exp_stab_sn", ["--spectral"])]:
        run = Path("runs") / name
        command = [sys.executable, "train.py", "--data", a.data, "--name", name,
                   "--epochs", str(a.epochs), "--threads", str(a.threads), *changes]
        if (run / "config.json").exists():
            config = json.loads((run / "config.json").read_text(encoding="utf-8"))
            if config["epochs"] != a.epochs:
                raise ValueError(f"{name}: el número de épocas no coincide.")
            if config["dataset_sha256"] != dataset_hash:
                raise ValueError(f"{name}: el conjunto de datos cambió.")
            expected_loss = "hinge" if name == "exp_loss_hinge" else "bce"
            if config["loss"] != expected_loss or config["spectral"] != (name == "exp_stab_sn"):
                raise ValueError(f"{name}: el cambio experimental no coincide.")
            if (run / "ckpt/G_final.pt").exists():
                with (run / "metrics.csv").open(newline="", encoding="utf-8") as stream:
                    rows = list(csv.DictReader(stream))
                if [int(row["epoch"]) for row in rows] == list(range(a.epochs + 1)):
                    print(f"Corrida completa: {name}", flush=True)
                    continue
            command.append("--resume")
        subprocess.run(command, check=True)
    subprocess.run([sys.executable, "analysis.py", "compare", "runs/base",
                    "runs/exp_loss_hinge", "runs/exp_stab_sn"], check=True)


if __name__ == "__main__":
    main()
