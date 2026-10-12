"""Vecinos exactos en píxeles con calibración y comparación de primer plano."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from gan.images import ImageDataset, image_tensor
from gan.utils import save_json


def distances(query, reference, batch_size=32):
    q, r = query.flatten(1), reference.flatten(1)
    return torch.cat([torch.cdist(q[i:i + batch_size], r) / q.shape[1] ** 0.5
                      for i in range(0, len(q), batch_size)])


def foreground_rms(a, b):
    background = torch.tensor([13, 20, 35]).view(3, 1, 1) / 255
    mask = ((a - background).abs().mean(0) > 0.12) | ((b - background).abs().mean(0) > 0.12)
    if not mask.any():
        return 0.0
    return ((a - b)[:, mask].square().mean().sqrt()).item()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--galeria", default="galeria")
    p.add_argument("--out", default="nn_resultados")
    a = p.parse_args()
    torch.set_num_threads(4)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ds = ImageDataset(a.data)
    if len(ds) < 2:
        raise ValueError("La calibración requiere al menos dos imágenes reales.")
    train = ds.images
    files = sorted(Path(a.galeria).glob("personaje_*_seed*.png"))
    if len(files) < 10:
        raise ValueError("Se requieren al menos 10 personajes finales.")
    generated = torch.stack([image_tensor(path) for path in files])
    matrix = distances(generated, train)
    best, indices = matrix.min(1)
    sub = torch.randperm(len(train), generator=torch.Generator().manual_seed(0))[:256]
    real_distances = distances(train[sub], train)
    real_distances[torch.arange(len(sub)), sub] = float("inf")
    real_nn = real_distances.min(1).values
    pairwise = distances(generated, generated)
    pairwise.fill_diagonal_(float("inf"))
    pair_min, pair_indices = pairwise.min(1)
    records = []
    fig, axes = plt.subplots(len(files), 2, figsize=(6.5, 2.05 * len(files)), squeeze=False)
    for i, (path, nearest) in enumerate(zip(files, indices)):
        neighbor_path = ds.files[int(nearest)]
        row = {"archivo": path.name, "vecino_archivo": neighbor_path.as_posix(),
               "rms_pixel": float(best[i]), "rms_primer_plano": foreground_rms(generated[i], train[nearest]),
               "personaje_mas_parecido": files[int(pair_indices[i])].name,
               "rms_entre_personajes": float(pair_min[i])}
        records.append(row)
        for image, ax in zip([generated[i], train[nearest]], axes[i]):
            ax.imshow(image.permute(1, 2, 0))
            ax.axis("off")
        axes[i, 0].set_title(f"Personaje {i + 1:02d}", fontsize=10)
        axes[i, 1].set_title(f"Vecino {neighbor_path.stem}\nRMS {best[i]:.4f}", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "vecinos.png", dpi=140)
    plt.close(fig)
    fig, axes = plt.subplots((len(files) + 4) // 5, 10,
                              figsize=(16, 2.3 * ((len(files) + 4) // 5)), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for i, nearest in enumerate(indices):
        row, pair = divmod(i, 5)
        axes[row, 2 * pair].imshow(generated[i].permute(1, 2, 0))
        axes[row, 2 * pair].set_title(f"P{i + 1:02d}", fontsize=9)
        axes[row, 2 * pair + 1].imshow(train[nearest].permute(1, 2, 0))
        axes[row, 2 * pair + 1].set_title(f"RMS {best[i]:.3f}", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "vecinos_presentacion.png", dpi=160)
    plt.close(fig)
    with (out / "vecinos.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    summary = {"metric": "Distancia RMS RGB en [0,1]; menor significa mayor parecido.",
               "training_count": len(train), "gallery_count": len(files), "calibration_count": len(sub),
               "real_nn_p10": float(real_nn.quantile(0.1)), "real_nn_median": float(real_nn.median()),
               "real_nn_p90": float(real_nn.quantile(0.9)),
               "generated_nn_min": float(best.min()), "generated_nn_median": float(best.median()),
               "generated_nn_max": float(best.max()), "gallery_pair_min": float(pair_min.min()),
               "exact_training_copies": sum(torch.equal(generated[i], train[indices[i]]) for i in range(len(files))),
               "limitation": "Píxeles y fondo uniforme no representan parecido semántico; una distancia alta puede deberse a defectos.",
               "characters": records}
    save_json(summary, out / "resumen.json")
    fig, ax = plt.subplots(figsize=(8, 3.7))
    ax.hist(real_nn.numpy(), bins=25, alpha=0.7, label="Reales frente a otra real")
    for i, value in enumerate(best):
        ax.axvline(float(value), color="#b43b55", alpha=0.6, label="Personajes generados" if i == 0 else None)
    ax.set_xlabel("Distancia RMS al vecino de entrenamiento")
    ax.set_ylabel("Cantidad de imágenes reales")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "calibracion.png", dpi=160)
    plt.close(fig)
    print({key: value for key, value in summary.items() if key != "characters"})


if __name__ == "__main__":
    main()
