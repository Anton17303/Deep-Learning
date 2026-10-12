"""Genera candidatos y una galería reproducible desde un checkpoint y semillas."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from gan.images import save_image
from gan.models import Generator
from gan.conditioning import attributes_from_seed, input_from_seed, model_noise_size
from gan.utils import save_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt")
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--select", type=int, nargs="+")
    p.add_argument("--criterio")
    p.add_argument("--galeria", default="galeria")
    p.add_argument("--candidates", default="evidencias/candidatos.png")
    p.add_argument("--from_selection", help="Regenera la galería usando seleccion.json")
    p.add_argument("--previous_candidates", type=int, default=0)
    a = p.parse_args()
    recorded = None
    if a.from_selection:
        recorded = json.loads(Path(a.from_selection).read_text(encoding="utf-8"))
        a.ckpt = a.ckpt or recorded["checkpoint"]
        a.n = recorded["candidatos_generados"]
        a.select = [item["seed"] for item in recorded["personajes"]]
        a.criterio = recorded["criterio"]
        a.previous_candidates = recorded.get("candidatos_previos", 0)
    if not a.ckpt or a.n < 1 or a.previous_candidates < 0:
        p.error("Se requiere un checkpoint y una cantidad positiva de candidatos.")
    if a.select and (len(a.select) < 10 or len(set(a.select)) != len(a.select)
                     or any(seed < 0 or seed >= a.n for seed in a.select) or not a.criterio):
        p.error("Se requieren al menos 10 semillas distintas dentro del conjunto de candidatos y un criterio.")
    torch.set_num_threads(4)
    ck = torch.load(a.ckpt, map_location="cpu", weights_only=True)
    config = ck["config"]
    nz = config["nz"]
    G = Generator(model_noise_size(config), config.get("ngf", 64), architecture=config.get("g_arch", "dcgan"))
    G.load_state_dict(ck["G"])
    G.eval()
    digest = hashlib.sha256(Path(a.ckpt).read_bytes()).hexdigest()
    if recorded and digest != recorded["checkpoint_sha256"]:
        raise ValueError("El checkpoint no coincide con el de la selección.")
    seeds = a.select if a.select else list(range(a.n))
    with torch.no_grad():
        batches = [G(torch.cat([input_from_seed(seed, config) for seed in seeds[i:i + 32]]))
                   for i in range(0, len(seeds), 32)]
        images = torch.cat(batches)
    if not a.select:
        cols, rows = 10, (a.n + 9) // 10
        fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 1.5), squeeze=False)
        for i, ax in enumerate(axes.flat):
            ax.axis("off")
            if i < a.n:
                ax.imshow(((images[i] + 1) / 2).clamp(0, 1).permute(1, 2, 0).numpy())
                ax.set_title(f"semilla {i}", fontsize=8)
        out = Path(a.candidates)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(out, dpi=110)
        plt.close(fig)
        save_json({"checkpoint": a.ckpt, "checkpoint_sha256": digest,
                   "candidatos_generados": a.n, "seeds": seeds}, out.with_suffix(".json"))
        if a.n > 50:
            for start in range(0, a.n, 50):
                end = min(start + 50, a.n)
                fig, axes = plt.subplots(5, 10, figsize=(15, 7.5), squeeze=False)
                for index, ax in enumerate(axes.flat, start):
                    ax.axis("off")
                    if index < end:
                        ax.imshow(((images[index] + 1) / 2).clamp(0, 1).permute(1, 2, 0).numpy())
                        ax.set_title(f"semilla {index}", fontsize=9)
                fig.tight_layout()
                page = out.with_name(f"{out.stem}_{start:03d}_{end - 1:03d}.png")
                fig.savefig(page, dpi=130)
                plt.close(fig)
        print(out)
        return
    out = Path(a.galeria)
    out.mkdir(parents=True, exist_ok=True)
    expected = {f"personaje_{i:02d}_seed{seed}.png" for i, seed in enumerate(seeds, 1)}
    if any(path.name not in expected for path in out.glob("personaje_*_seed*.png")):
        raise FileExistsError("La carpeta contiene una selección distinta.")
    info = []
    for index, (seed, image) in enumerate(zip(seeds, images), 1):
        filename = f"personaje_{index:02d}_seed{seed}.png"
        save_image(image, out / filename)
        vector = input_from_seed(seed, config)
        torch.save(vector, out / f"personaje_{index:02d}_z.pt")
        info.append({"personaje": index, "seed": seed, "archivo": filename,
                     "sha256_png": hashlib.sha256((out / filename).read_bytes()).hexdigest(),
                     "z": vector.flatten().tolist()})
        if config.get("conditional", False):
            info[-1]["condicion"] = attributes_from_seed(seed)
    if recorded:
        for item, original in zip(info, recorded["personajes"]):
            if item["sha256_png"] != original["sha256_png"]:
                raise ValueError("La regeneración produjo píxeles distintos.")
            for key in ["nombre", "rol", "rasgos"]:
                if key in original:
                    item[key] = original[key]
    total = a.n + a.previous_candidates
    save_json({"tasa_seleccion": f"{len(seeds)} de {total}", "candidatos_generados": a.n,
               "candidatos_previos": a.previous_candidates, "candidatos_totales": total,
               "criterio": a.criterio, "checkpoint": a.ckpt, "checkpoint_sha256": digest,
               "personajes": info}, out / "seleccion.json")
    rows = (len(info) + 4) // 5
    fig, axes = plt.subplots(rows, 5, figsize=(12, 2.7 * rows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for item, image, ax in zip(info, images, axes.flat):
        ax.imshow(((image + 1) / 2).clamp(0, 1).permute(1, 2, 0).numpy())
        ax.set_title(f"{item['personaje']:02d} · semilla {item['seed']}")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out / "galeria.png", dpi=160)
    plt.close(fig)
    print(f"{len(seeds)} de {a.n} -> {out}")


if __name__ == "__main__":
    main()
