"""Entrenamiento GAN con rejilla de ruido fijo, curvas, diversidad y checkpoints.

Ejemplos:
  python train.py --data data/processed --name base
  python train.py --data data/processed --name exp_loss_hinge --loss hinge
  python train.py --data data/processed --name exp_stab_sn --spectral
Cambie UNA sola cosa por experimento; seed, epochs y eval_seed se mantienen.
"""
import argparse, csv, time
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, utils as vutils

from gan.models import Generator, Discriminator
from gan.losses import d_loss_fn, g_loss_fn, KINDS
from gan.utils import set_seed, make_fixed_noise, diversity_score, save_json

p = argparse.ArgumentParser()
p.add_argument("--data", required=True, help="carpeta con subcarpeta(s) de imágenes (ImageFolder)")
p.add_argument("--name", required=True)
p.add_argument("--out", default="runs")
p.add_argument("--loss", default="bce", choices=KINDS)
p.add_argument("--epochs", type=int, default=100)
p.add_argument("--bs", type=int, default=64)
p.add_argument("--nz", type=int, default=100)
p.add_argument("--lr_g", type=float, default=2e-4)
p.add_argument("--lr_d", type=float, default=2e-4)
p.add_argument("--beta1", type=float, default=0.5)
p.add_argument("--beta2", type=float, default=0.999)
p.add_argument("--n_critic", type=int, default=1)
p.add_argument("--label_real", type=float, default=1.0, help="0.9 = suavizado de etiquetas")
p.add_argument("--gp_lambda", type=float, default=10.0)
p.add_argument("--d_norm", default="bn", choices=["bn", "ln", "none"])
p.add_argument("--spectral", action="store_true", help="normalización espectral en D")
p.add_argument("--d_dropout", type=float, default=0.0)
p.add_argument("--flip", action="store_true", help="aumento: volteo horizontal")
p.add_argument("--seed", type=int, default=42)
p.add_argument("--eval_seed", type=int, default=1234)
p.add_argument("--n_eval", type=int, default=16)
p.add_argument("--sample_every", type=int, default=5)
p.add_argument("--ckpt_every", type=int, default=25)
p.add_argument("--workers", type=int, default=2)
p.add_argument("--resume", action="store_true")
a = p.parse_args()

set_seed(a.seed)
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
run = Path(a.out) / a.name
(run / "grids").mkdir(parents=True, exist_ok=True)
(run / "ckpt").mkdir(exist_ok=True)
save_json(vars(a), run / "config.json")

tf = [transforms.Resize(64), transforms.CenterCrop(64)]
if a.flip:
    tf.append(transforms.RandomHorizontalFlip())
tf += [transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)]
ds = datasets.ImageFolder(a.data, transform=transforms.Compose(tf))
dl = DataLoader(ds, batch_size=a.bs, shuffle=True, drop_last=True,
                num_workers=a.workers, pin_memory=dev.type == "cuda")
print(f"[{a.name}] {len(ds)} imágenes, dispositivo {dev}")

G = Generator(a.nz).to(dev)
D = Discriminator(norm=a.d_norm, spectral=a.spectral, dropout=a.d_dropout).to(dev)
oG = torch.optim.Adam(G.parameters(), a.lr_g, betas=(a.beta1, a.beta2))
oD = torch.optim.Adam(D.parameters(), a.lr_d, betas=(a.beta1, a.beta2))
fixed = make_fixed_noise(a.n_eval, a.nz, a.eval_seed).to(dev)
start = 1

if a.resume and (run / "ckpt" / "last.pt").exists():
    ck = torch.load(run / "ckpt" / "last.pt", map_location=dev)
    G.load_state_dict(ck["G"]); D.load_state_dict(ck["D"])
    oG.load_state_dict(ck["oG"]); oD.load_state_dict(ck["oD"]); start = ck["epoch"] + 1
    print("reanudando desde época", start)

def save_grid(ep):
    G.eval()
    with torch.no_grad():
        x = G(fixed)
    G.train()
    vutils.save_image(x, run / "grids" / f"epoch_{ep:03d}.png", nrow=4, normalize=True, value_range=(-1, 1), padding=2)
    return diversity_score(x.cpu())

new_files = start == 1
fi = open(run / "losses.csv", "a", newline=""); wi = csv.writer(fi)
fm = open(run / "metrics.csv", "a", newline=""); wm = csv.writer(fm)
if new_files:
    wi.writerow(["iter", "epoch", "loss_d", "loss_g", "d_real", "d_fake"])
    wm.writerow(["epoch", "loss_d", "loss_g", "d_real", "d_fake", "diversity", "seconds"])
    div0 = save_grid(0); wm.writerow([0, "", "", "", "", f"{div0:.5f}", 0])

it = (start - 1) * len(dl); t0 = time.time()
for ep in range(start, a.epochs + 1):
    acc = dict(ld=0., lg=0., dr=0., df=0., n=0)
    for i, (real, _) in enumerate(dl):
        real = real.to(dev); b = real.size(0)
        z = torch.randn(b, a.nz, device=dev)
        fake = G(z)
        ld, r, f = d_loss_fn(a.loss, D, real, fake, a.label_real, a.gp_lambda)
        oD.zero_grad(set_to_none=True); ld.backward(); oD.step()
        lg = torch.zeros(())
        if (i + 1) % a.n_critic == 0:
            lg = g_loss_fn(a.loss, D, G(torch.randn(b, a.nz, device=dev)) if a.n_critic > 1 else fake)
            oG.zero_grad(set_to_none=True); lg.backward(); oG.step()
        # Para BCE se reporta D(x) como probabilidad; para el resto, salida cruda.
        dr, df = (r.sigmoid().mean(), f.sigmoid().mean()) if a.loss in ("bce", "bce_sat") else (r.mean(), f.mean())
        it += 1
        wi.writerow([it, ep, f"{ld.item():.5f}", f"{lg.item():.5f}", f"{dr.item():.5f}", f"{df.item():.5f}"])
        acc["ld"] += ld.item(); acc["lg"] += lg.item(); acc["dr"] += dr.item(); acc["df"] += df.item(); acc["n"] += 1
    n = acc["n"]
    div = save_grid(ep) if (ep % a.sample_every == 0 or ep == a.epochs) else ""
    wm.writerow([ep, f"{acc['ld']/n:.5f}", f"{acc['lg']/n:.5f}", f"{acc['dr']/n:.5f}", f"{acc['df']/n:.5f}",
                 f"{div:.5f}" if div != "" else "", f"{time.time()-t0:.0f}"])
    fi.flush(); fm.flush()
    print(f"ep {ep:3d} | D {acc['ld']/n:.3f} G {acc['lg']/n:.3f} | D(x) {acc['dr']/n:.3f} D(G(z)) {acc['df']/n:.3f} | div {div}")
    torch.save(dict(G=G.state_dict(), D=D.state_dict(), oG=oG.state_dict(), oD=oD.state_dict(), epoch=ep), run / "ckpt" / "last.pt")
    if ep % a.ckpt_every == 0 or ep == a.epochs:
        torch.save(dict(G=G.state_dict(), config=vars(a)), run / "ckpt" / f"G_ep{ep:03d}.pt")
torch.save(dict(G=G.state_dict(), config=vars(a)), run / "ckpt" / "G_final.pt")
print("listo ->", run)
