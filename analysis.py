"""Figuras para el PDF.
  python analysis.py curves   runs/base
  python analysis.py evolution runs/base --epochs 0 5 25 50 100
  python analysis.py compare  runs/base runs/exp_loss_hinge runs/exp_stab_sn
"""
import argparse, csv
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def smooth(x, k=50):
    x = np.asarray(x, float)
    if len(x) < k: return x
    return np.convolve(x, np.ones(k) / k, mode="valid")


def curves(run):
    r = read(Path(run) / "losses.csv")
    ld = [float(x["loss_d"]) for x in r]; lg = [float(x["loss_g"]) if x["loss_g"] else np.nan for x in r]
    dr = [float(x["d_real"]) for x in r]; df = [float(x["d_fake"]) for x in r]
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    ax[0].plot(smooth(ld), label="pérdida D"); ax[0].plot(smooth(lg), label="pérdida G")
    ax[0].set_title("Pérdidas (media móvil)"); ax[0].set_xlabel("iteración"); ax[0].legend()
    ax[1].plot(smooth(dr), label="D(x) real"); ax[1].plot(smooth(df), label="D(G(z)) falso")
    ax[1].set_title("Salida de D"); ax[1].set_xlabel("iteración"); ax[1].legend()
    plt.tight_layout(); out = Path(run) / "curvas.png"; plt.savefig(out, dpi=150); print(out)


def evolution(run, epochs):
    imgs = [(e, Image.open(Path(run) / "grids" / f"epoch_{e:03d}.png")) for e in epochs]
    fig, ax = plt.subplots(1, len(imgs), figsize=(3.2 * len(imgs), 3.4))
    for a_, (e, im) in zip(np.atleast_1d(ax), imgs):
        a_.imshow(im); a_.set_title(f"época {e}"); a_.axis("off")
    plt.tight_layout(); out = Path(run) / "evolucion.png"; plt.savefig(out, dpi=150); print(out)


def compare(runs):
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    for run in runs:
        m = read(Path(run) / "metrics.csv")
        e = [int(x["epoch"]) for x in m if x["diversity"] != ""]
        d = [float(x["diversity"]) for x in m if x["diversity"] != ""]
        ax[0].plot(e, d, marker="o", label=Path(run).name)
        e2 = [int(x["epoch"]) for x in m if x["loss_d"] != ""]
        ax[1].plot(e2, [float(x["loss_d"]) for x in m if x["loss_d"] != ""], label=Path(run).name)
    ax[0].set_title("Diversidad (ruido fijo; baja = posible colapso)"); ax[0].set_xlabel("época"); ax[0].legend()
    ax[1].set_title("Pérdida de D: escalas distintas según la función"); ax[1].set_xlabel("época"); ax[1].legend()
    plt.tight_layout(); plt.savefig("comparacion.png", dpi=150); print("comparacion.png")


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("cmd"); p.add_argument("runs", nargs="+")
    p.add_argument("--epochs", type=int, nargs="+", default=[0, 5, 25, 50, 100])
    a = p.parse_args()
    if a.cmd == "curves": curves(a.runs[0])
    elif a.cmd == "evolution": evolution(a.runs[0], a.epochs)
    elif a.cmd == "compare": compare(a.runs)
