"""Genera candidatos y arma la galería final reproducible (semilla -> z -> imagen).

1) Candidatos (hoja de contacto numerada por semilla):
   python generate_gallery.py --ckpt runs/base/ckpt/G_final.pt --n 200
2) Elegir 10 mirando candidatos.png y fijar criterio/tasa de selección:
   python generate_gallery.py --ckpt ... --n 200 --select 3 17 22 41 58 77 90 120 133 188 \
        --criterio "nítidos, distintos entre sí y sin parecido alto en la prueba NN"
"""
import argparse, json
from pathlib import Path
import torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from torchvision import utils as vutils
from gan.models import Generator
from gan.utils import z_from_seed

p = argparse.ArgumentParser()
p.add_argument("--ckpt", required=True)
p.add_argument("--n", type=int, default=200)
p.add_argument("--select", type=int, nargs="*")
p.add_argument("--criterio", default="(describir criterio de selección)")
p.add_argument("--galeria", default="galeria")
a = p.parse_args()

ck = torch.load(a.ckpt, map_location="cpu")
nz = ck["config"]["nz"]
G = Generator(nz); G.load_state_dict(ck["G"]); G.eval()

def gen(seed):
    with torch.no_grad():
        return G(z_from_seed(seed, nz))[0]

if not a.select:
    cols = 20; rows = (a.n + cols - 1) // cols
    fig, ax = plt.subplots(rows, cols, figsize=(cols * 1.1, rows * 1.2))
    for i, a_ in enumerate(ax.flat):
        a_.axis("off")
        if i < a.n:
            a_.imshow(((gen(i) + 1) / 2).clamp(0, 1).permute(1, 2, 0).numpy())
            a_.set_title(str(i), fontsize=6, pad=1)
    plt.tight_layout(); plt.savefig("candidatos.png", dpi=170); print("candidatos.png")
else:
    out = Path(a.galeria); out.mkdir(exist_ok=True)
    info = []
    for k, s in enumerate(a.select, 1):
        img = gen(s)
        fn = f"personaje_{k:02d}_seed{s}.png"
        vutils.save_image(img, out / fn, normalize=True, value_range=(-1, 1))
        torch.save(z_from_seed(s, nz), out / f"personaje_{k:02d}_z.pt")
        info.append(dict(personaje=k, seed=s, archivo=fn))
    meta = dict(tasa_seleccion=f"{len(a.select)} de {a.n}", criterio=a.criterio, checkpoint=a.ckpt, personajes=info)
    json.dump(meta, open(out / "seleccion.json", "w"), indent=2, ensure_ascii=False)
    print(meta["tasa_seleccion"], "->", out)
