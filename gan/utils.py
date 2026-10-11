import json, random
import numpy as np
import torch


def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def make_fixed_noise(n, nz, seed=1234):
    """Mismo ruido de evaluación en TODOS los experimentos (requisito 2.1)."""
    g = torch.Generator().manual_seed(seed)
    return torch.randn(n, nz, generator=g)


def z_from_seed(seed, nz):
    """Un personaje = una semilla = un vector z reproducible."""
    return torch.randn(1, nz, generator=torch.Generator().manual_seed(int(seed)))


@torch.no_grad()
def diversity_score(imgs):
    """Distancia RMS media por pares entre imágenes (rango [-1,1]).
    Si baja mucho a lo largo del entrenamiento => señal de mode collapse."""
    x = imgs.flatten(1).float()
    d = torch.cdist(x, x)
    n = x.size(0)
    return (d.sum() / (n * (n - 1)) / x.size(1) ** 0.5).item()


def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
