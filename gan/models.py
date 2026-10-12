"""Generador y discriminador estilo DCGAN para imágenes de 64x64.

Opciones del discriminador (sirven para los experimentos de estabilización):
  norm      : 'bn' (BatchNorm), 'ln' (GroupNorm(1,C), recomendado con WGAN-GP) o 'none'
  spectral  : normalización espectral en todas las convoluciones de D
  dropout   : Dropout2d en D (0 = apagado)
"""
import torch
import torch.nn as nn
from torch.nn.utils import spectral_norm


def init_weights(m):
    # Con spectral_norm el parámetro real se llama weight_orig.
    w = getattr(m, "weight_orig", getattr(m, "weight", None))
    if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
        nn.init.normal_(w.data, 0.0, 0.02)
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.zeros_(m.bias.data)


class Generator(nn.Module):
    def __init__(self, nz=100, ngf=64, nc=3):
        super().__init__()
        self.nz = nz
        self.net = nn.Sequential(
            nn.ConvTranspose2d(nz, ngf * 8, 4, 1, 0, bias=False),       # 4x4
            nn.BatchNorm2d(ngf * 8), nn.ReLU(True),
            nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),  # 8x8
            nn.BatchNorm2d(ngf * 4), nn.ReLU(True),
            nn.ConvTranspose2d(ngf * 4, ngf * 2, 4, 2, 1, bias=False),  # 16x16
            nn.BatchNorm2d(ngf * 2), nn.ReLU(True),
            nn.ConvTranspose2d(ngf * 2, ngf, 4, 2, 1, bias=False),      # 32x32
            nn.BatchNorm2d(ngf), nn.ReLU(True),
            nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),           # 64x64
            nn.Tanh(),
        )
        self.apply(init_weights)

    def forward(self, z):
        return self.net(z.view(z.size(0), self.nz, 1, 1))


def _norm(kind, c):
    if kind == "bn":
        return nn.BatchNorm2d(c)
    if kind == "ln":
        return nn.GroupNorm(1, c)
    return nn.Identity()


class Discriminator(nn.Module):
    def __init__(self, ndf=64, nc=3, norm="bn", spectral=False, dropout=0.0):
        super().__init__()
        wrap = lambda m: m
        layers = [wrap(nn.Conv2d(nc, ndf, 4, 2, 1, bias=False)), nn.LeakyReLU(0.2, True)]  # 32
        c = ndf
        for mult in (2, 4, 8):                                                              # 16, 8, 4
            layers += [wrap(nn.Conv2d(c, ndf * mult, 4, 2, 1, bias=False)),
                       _norm(norm, ndf * mult), nn.LeakyReLU(0.2, True)]
            if dropout > 0:
                layers.append(nn.Dropout2d(dropout))
            c = ndf * mult
        layers.append(wrap(nn.Conv2d(c, 1, 4, 1, 0, bias=False)))                           # logit
        self.net = nn.Sequential(*layers)
        self.apply(init_weights)

        if spectral:
            with torch.random.fork_rng():
                torch.manual_seed(314159)
                for module in self.net:
                    if isinstance(module, nn.Conv2d):
                        spectral_norm(module)

    def forward(self, x):
        return self.net(x).view(-1)  # logits (sin sigmoide)
