"""Entrenamiento reproducible con checkpoints, ruido fijo y registro de pérdidas."""
import argparse
import csv
import json
import hashlib
import platform
import random
import time
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from gan.images import ImageDataset, save_grid
from gan.conditioning import DIM, condition_from_seed, critic_input, model_noise_size
from gan.losses import KINDS, d_loss_fn, g_loss_fn, moment_loss
from gan.models import Discriminator, Generator
from gan.utils import diversity_score, make_fixed_noise, save_json, set_seed


def arguments():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--out", default="runs")
    p.add_argument("--loss", default="bce", choices=KINDS)
    p.add_argument("--g_arch", choices=["dcgan", "resize"], default=argparse.SUPPRESS)
    p.add_argument("--moment_weight", type=float, default=argparse.SUPPRESS)
    p.add_argument("--conditional", action="store_true", default=argparse.SUPPRESS)
    p.add_argument("--reconstruction_weight", type=float, default=argparse.SUPPRESS)
    p.add_argument("--eye_weight", type=float, default=argparse.SUPPRESS)
    p.add_argument("--initialize_from", default=argparse.SUPPRESS)
    for name, default in {"epochs": 60, "bs": 64, "nz": 64, "ngf": 16, "ndf": 16,
                          "n_critic": 1, "n_eval": 16, "sample_every": 5, "ckpt_every": 20,
                          "workers": 0, "threads": 4, "seed": 42, "eval_seed": 1234}.items():
        p.add_argument(f"--{name}", type=int, default=default)
    for name, default in {"lr_g": 2e-4, "lr_d": 2e-4, "beta1": 0.5, "beta2": 0.999,
                          "label_real": 1.0, "gp_lambda": 10.0, "d_dropout": 0.0}.items():
        p.add_argument(f"--{name}", type=float, default=default)
    p.add_argument("--d_norm", default="bn", choices=["bn", "ln", "none"])
    for flag in ["spectral", "flip", "resume"]:
        p.add_argument(f"--{flag}", action="store_true")
    a = p.parse_args()
    for key in ["epochs", "bs", "nz", "ngf", "ndf", "n_critic", "sample_every", "ckpt_every", "threads"]:
        if getattr(a, key) < 1:
            p.error(f"{key} debe ser positivo.")
    if a.n_eval < 2 or not 0 <= a.d_dropout < 1 or not 0 < a.label_real <= 1:
        p.error("Configuración inválida de evaluación, dropout o etiquetas.")
    return a


def main():
    a = arguments()
    torch.set_num_threads(a.threads)
    set_seed(a.seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    run = Path(a.out) / a.name
    if (run / "config.json").exists() and not a.resume:
        raise FileExistsError("La corrida ya existe. Se requiere --resume o un nombre distinto.")
    conditional = getattr(a, "conditional", False)
    ds = ImageDataset(a.data, flip=a.flip, conditional=conditional)
    if len(ds) < a.bs:
        raise ValueError("El conjunto debe contener al menos un lote completo.")
    data_rng = torch.Generator().manual_seed(a.seed + 1000)
    dl = DataLoader(ds, batch_size=a.bs, shuffle=True, drop_last=True,
                    num_workers=a.workers, generator=data_rng)
    config = vars(a).copy()
    config.update(dataset_sha256=ds.fingerprint(), image_count=len(ds), resolution=64)
    if conditional:
        config.update(condition_dim=DIM, condition_manifest_sha256=ds.condition_manifest_sha256)
    initial = None
    if hasattr(a, "initialize_from"):
        source = Path(a.initialize_from)
        config["initialize_from_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
        initial = torch.load(source, map_location="cpu", weights_only=True)
        if initial["config"]["dataset_sha256"] != config["dataset_sha256"]:
            raise ValueError("Los pesos iniciales pertenecen a otro conjunto.")
    last = run / "ckpt" / "last.pt"
    if a.resume:
        if not last.exists():
            raise FileNotFoundError("No existe un checkpoint para reanudar.")
        original = json.loads((run / "config.json").read_text(encoding="utf-8"))
        ignored = {"resume", "out", "data", "workers", "threads", "initialize_from"}
        changed = [key for key in config if key not in ignored and config[key] != original.get(key)]
        if changed:
            raise ValueError(f"La reanudación cambia la configuración: {changed}")
    else:
        (run / "grids").mkdir(parents=True)
        (run / "ckpt").mkdir()
        save_json(config, run / "config.json")
    G = Generator(model_noise_size(config), a.ngf, architecture=getattr(a, "g_arch", "dcgan")).to(dev)
    D = Discriminator(a.ndf, nc=3 + (DIM if conditional else 0), norm=a.d_norm, spectral=a.spectral, dropout=a.d_dropout).to(dev)
    if initial and not a.resume:
        G.load_state_dict(initial["G"])
        D.load_state_dict(initial["D"])
    oG = torch.optim.Adam(G.parameters(), a.lr_g, betas=(a.beta1, a.beta2))
    oD = torch.optim.Adam(D.parameters(), a.lr_d, betas=(a.beta1, a.beta2))
    fixed = make_fixed_noise(a.n_eval, a.nz, a.eval_seed).to(dev)
    if conditional:
        fixed_conditions = torch.stack([condition_from_seed(i * 13) for i in range(a.n_eval)]).to(dev)
        fixed = torch.cat([fixed, fixed_conditions], dim=1)
    noise_rng = torch.Generator(device=dev).manual_seed(a.seed + 2000)
    start, iteration, elapsed = 1, 0, 0.0
    if a.resume:
        ck = torch.load(last, map_location="cpu", weights_only=False)
        G.load_state_dict(ck["G"])
        D.load_state_dict(ck["D"])
        oG.load_state_dict(ck["oG"])
        oD.load_state_dict(ck["oD"])
        start, iteration, elapsed = ck["epoch"] + 1, ck["iteration"], ck["elapsed"]
        torch.set_rng_state(ck["torch_rng"])
        random.setstate(ck["python_rng"])
        np.random.set_state(ck["numpy_rng"])
        data_rng.set_state(ck["data_rng"])
        noise_rng.set_state(ck["noise_rng"])
        if dev.type == "cuda":
            torch.cuda.set_rng_state_all(ck["cuda_rng"])
        log_files = ["losses.csv", "metrics.csv"]
        if (run / "regularization.csv").exists():
            log_files.append("regularization.csv")
        for filename in log_files:
            path = run / filename
            with path.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream)
                fields = reader.fieldnames
                rows = [row for row in reader if int(row["epoch"]) <= ck["epoch"]]
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
    else:
        save_json({"python": platform.python_version(), "torch": torch.__version__,
                   "numpy": np.__version__, "device": str(dev), "threads": a.threads,
                   "parameters_g": sum(p.numel() for p in G.parameters()),
                   "parameters_d": sum(p.numel() for p in D.parameters())}, run / "environment.json")
        torch.save(fixed.cpu(), run / "fixed_noise.pt")
        torch.save({"G": G.state_dict(), "config": config}, run / "ckpt" / "G_ep000.pt")

    def snapshot(epoch):
        G.eval()
        with torch.no_grad():
            images = G(fixed)
        G.train()
        save_grid(images, run / "grids" / f"epoch_{epoch:03d}.png")
        return diversity_score(images.cpu())

    if start > a.epochs:
        if not (run / "ckpt" / "G_final.pt").exists():
            torch.save({"G": G.state_dict(), "config": config}, run / "ckpt" / "G_final.pt")
        print(f"Corrida completa: {run}")
        return

    mode = "a" if a.resume else "w"
    moment_weight = getattr(a, "moment_weight", 0)
    reconstruction_weight = getattr(a, "reconstruction_weight", 0)
    eye_weight = getattr(a, "eye_weight", 0)
    if reconstruction_weight < 0 or (reconstruction_weight and not conditional):
        raise ValueError("La reconstrucción requiere condiciones y un peso no negativo.")
    if eye_weight < 0 or (eye_weight and not conditional):
        raise ValueError("El ajuste de ojos requiere condiciones y un peso no negativo.")
    if moment_weight < 0:
        raise ValueError("El peso de regularización debe ser no negativo.")
    has_regularization = moment_weight or reconstruction_weight or eye_weight
    with (run / "losses.csv").open(mode, newline="", encoding="utf-8") as fi, \
         (run / "metrics.csv").open(mode, newline="", encoding="utf-8") as fm, \
         ((run / "regularization.csv").open(mode, newline="", encoding="utf-8")
          if has_regularization else nullcontext(None)) as fr:
        wi, wm = csv.writer(fi), csv.writer(fm)
        wr = csv.writer(fr) if fr else None
        if wr and not a.resume:
            wr.writerow(["iter", "epoch", "g_adversarial", "moment_loss", "g_total"]
                        + (["reconstruction_loss"] if reconstruction_weight else [])
                        + (["eye_loss"] if eye_weight else []))
        if not a.resume:
            wi.writerow(["iter", "epoch", "loss_d", "loss_g", "d_real", "d_fake"])
            wm.writerow(["epoch", "loss_d", "loss_g", "d_real", "d_fake", "diversity", "seconds"])
            wm.writerow([0, "", "", "", "", snapshot(0), 0])
        print(f"[{a.name}] {len(ds)} imágenes, dispositivo {dev}", flush=True)
        t0 = time.perf_counter()
        for ep in range(start, a.epochs + 1):
            sums = np.zeros(4)
            count, g_updates, g_sum = 0, 0, 0.0
            for batch in dl:
                if conditional:
                    real, conditions = batch
                    real, conditions = real.to(dev), conditions.to(dev)
                    critic = lambda image: D(critic_input(image, conditions))
                else:
                    real, critic = batch.to(dev), D
                z = torch.randn(len(real), a.nz, device=dev, generator=noise_rng)
                if conditional:
                    z = torch.cat([z, conditions], dim=1)
                fake = G(z)
                for parameter in D.parameters():
                    parameter.requires_grad_(True)
                ld, r, f = d_loss_fn(a.loss, critic, real, fake, a.label_real, a.gp_lambda)
                oD.zero_grad(set_to_none=True)
                ld.backward()
                oD.step()
                iteration += 1
                lg = None
                if iteration % a.n_critic == 0:
                    for parameter in D.parameters():
                        parameter.requires_grad_(False)
                    lg = g_loss_fn(a.loss, critic, fake)
                    if has_regularization:
                        adversarial = lg
                        penalty = moment_loss(real, fake) if moment_weight else torch.zeros((), device=dev)
                        reconstruction = (fake - real).abs().mean() if reconstruction_weight else torch.zeros((), device=dev)
                        eye = (fake[:, :, 22:36, 20:44] - real[:, :, 22:36, 20:44]).square().mean() if eye_weight else torch.zeros((), device=dev)
                        lg = adversarial + moment_weight * penalty + reconstruction_weight * reconstruction + eye_weight * eye
                        wr.writerow([iteration, ep, adversarial.item(), penalty.item(), lg.item()]
                                    + ([reconstruction.item()] if reconstruction_weight else [])
                                    + ([eye.item()] if eye_weight else []))
                    oG.zero_grad(set_to_none=True)
                    lg.backward()
                    oG.step()
                    g_updates += 1
                    g_sum += lg.item()
                dr, df = ((r.sigmoid().mean(), f.sigmoid().mean()) if a.loss in ("bce", "bce_sat")
                          else (r.mean(), f.mean()))
                values = [ld.item(), 0 if lg is None else lg.item(), dr.item(), df.item()]
                if not np.isfinite(values).all():
                    raise FloatingPointError("Se detectó una pérdida no finita.")
                wi.writerow([iteration, ep, values[0], "" if lg is None else values[1], *values[2:]])
                sums += values
                count += 1
            averages = sums / count
            averages[1] = g_sum / g_updates if g_updates else float("nan")
            div = snapshot(ep) if ep % a.sample_every == 0 or ep == a.epochs else ""
            seconds = elapsed + time.perf_counter() - t0
            wm.writerow([ep, *averages, div, seconds])
            fi.flush()
            fm.flush()
            if fr:
                fr.flush()
            checkpoint = {"G": G.state_dict(), "D": D.state_dict(), "oG": oG.state_dict(),
                          "oD": oD.state_dict(), "epoch": ep, "iteration": iteration, "elapsed": seconds,
                          "config": config, "torch_rng": torch.get_rng_state(),
                          "python_rng": random.getstate(), "numpy_rng": np.random.get_state(),
                          "data_rng": data_rng.get_state(), "noise_rng": noise_rng.get_state(),
                          "cuda_rng": torch.cuda.get_rng_state_all() if dev.type == "cuda" else []}
            temp = run / "ckpt" / "last.tmp"
            torch.save(checkpoint, temp)
            temp.replace(last)
            if ep % a.ckpt_every == 0 or ep == a.epochs:
                torch.save({"G": G.state_dict(), "config": config}, run / "ckpt" / f"G_ep{ep:03d}.pt")
            print(f"ep {ep:3d} | D {averages[0]:.3f} G {averages[1]:.3f} | div {div} | {seconds:.1f}s", flush=True)
    torch.save({"G": G.state_dict(), "config": config}, run / "ckpt" / "G_final.pt")
    print(f"listo -> {run}")


if __name__ == "__main__":
    main()
