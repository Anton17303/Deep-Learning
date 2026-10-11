"""Prueba de vecinos más cercanos (evidencia 3) con rasgos de ResNet18 y píxeles.
  python nn_test.py --data data/processed --galeria galeria
Incluye una CALIBRACIÓN: qué tan parecida es una imagen real a su vecina más cercana
dentro del propio entrenamiento. Sirve para interpretar los números con honestidad.
"""
import argparse, csv
from pathlib import Path
import numpy as np, torch
import torch.nn.functional as F
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import datasets, models, transforms

p = argparse.ArgumentParser()
p.add_argument("--data", required=True)
p.add_argument("--galeria", default="galeria")
p.add_argument("--out", default="nn_resultados")
p.add_argument("--no_pretrained", action="store_true", help="solo para pruebas sin internet")
a = p.parse_args()
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
Path(a.out).mkdir(exist_ok=True)

ds = datasets.ImageFolder(a.data, transform=transforms.Compose([transforms.Resize(64), transforms.CenterCrop(64), transforms.ToTensor()]))
train = torch.stack([ds[i][0] for i in range(len(ds))])                      # [N,3,64,64] en [0,1]
files = sorted(Path(a.galeria).glob("personaje_*_seed*.png"))
gen = torch.stack([transforms.ToTensor()(Image.open(f).convert("RGB").resize((64, 64))) for f in files])

net = models.resnet18(weights=None if a.no_pretrained else models.ResNet18_Weights.DEFAULT)
net.fc = torch.nn.Identity(); net = net.to(dev).eval()
mean = torch.tensor([0.485, 0.456, 0.406], device=dev).view(1, 3, 1, 1)
std = torch.tensor([0.229, 0.224, 0.225], device=dev).view(1, 3, 1, 1)

@torch.no_grad()
def feats(x, bs=256):
    out = []
    for i in range(0, len(x), bs):
        b = F.interpolate(x[i:i + bs].to(dev), size=224, mode="bilinear", align_corners=False)
        out.append(F.normalize(net((b - mean) / std), dim=1).cpu())
    return torch.cat(out)

Ft, Fg = feats(train), feats(gen)
sim = Fg @ Ft.T
best_sim, best_idx = sim.max(1)
pix = torch.cdist(gen.flatten(1), train.flatten(1)) / (3 * 64 * 64) ** 0.5   # RMS por píxel
pix_best = pix[torch.arange(len(gen)), best_idx]

# Calibración: vecino más cercano de imágenes reales dentro del entrenamiento (sin sí misma)
rng = np.random.default_rng(0); sub = rng.choice(len(train), size=min(500, len(train)), replace=False)
S = Ft[sub] @ Ft.T
S[torch.arange(len(sub)), torch.tensor(sub)] = -1
real_nn = S.max(1).values
print(f"Calibración (real vs. su vecino en train): mediana {real_nn.median():.3f}, p90 {real_nn.quantile(0.9):.3f}, p99 {real_nn.quantile(0.99):.3f}")
print(f"Generadas vs. train: mín {best_sim.min():.3f}, mediana {best_sim.median():.3f}, máx {best_sim.max():.3f}")

n = len(gen); cols = 5; rows = (n + cols - 1) // cols
fig, ax = plt.subplots(rows, cols * 2, figsize=(cols * 2.6, rows * 1.5))
ax = np.atleast_2d(ax)
for a_ in ax.flat: a_.axis("off")
with open(Path(a.out) / "vecinos.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["archivo", "vecino_idx", "coseno_cnn", "rms_pixel"])
    for i in range(n):
        r, c = divmod(i, cols)
        ax[r, 2 * c].imshow(gen[i].permute(1, 2, 0)); ax[r, 2 * c].set_title("generada", fontsize=6, pad=1)
        ax[r, 2 * c + 1].imshow(train[best_idx[i]].permute(1, 2, 0))
        ax[r, 2 * c + 1].set_title(f"cos {best_sim[i]:.2f}", fontsize=6, pad=1)
        w.writerow([files[i].name, int(best_idx[i]), f"{best_sim[i]:.4f}", f"{pix_best[i]:.4f}"])
plt.tight_layout(); plt.savefig(Path(a.out) / "vecinos.png", dpi=170)
print("->", Path(a.out) / "vecinos.png", "y vecinos.csv")
