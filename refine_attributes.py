"""Inicia una fase de ajuste desde los pesos completos de la GAN condicional."""
import subprocess
import sys
from pathlib import Path

import torch


def main():
    source = Path("runs/conditional/ckpt/last.pt")
    initial = source.with_name("GD_final.pt")
    if not initial.exists():
        checkpoint = torch.load(source, map_location="cpu", weights_only=False)
        if checkpoint["epoch"] != checkpoint["config"]["epochs"]:
            raise ValueError("La corrida condicional todavía no termina.")
        torch.save({"G": checkpoint["G"], "D": checkpoint["D"], "config": checkpoint["config"],
                    "source_epoch": checkpoint["epoch"]}, initial)
    command = [sys.executable, "train.py", "--data", "data/processed", "--name", "conditional_refined",
               "--epochs", "40", "--g_arch", "resize", "--loss", "hinge", "--spectral", "--d_norm", "none",
               "--lr_g", "0.0001", "--lr_d", "0.0001", "--moment_weight", "2", "--conditional",
               "--reconstruction_weight", "10", "--eye_weight", "15", "--threads", "4",
               "--initialize_from", str(initial)]
    if Path("runs/conditional_refined/config.json").exists():
        command.append("--resume")
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
