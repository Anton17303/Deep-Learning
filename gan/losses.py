"""Funciones de pérdida intercambiables. D devuelve logits.

kind:
  bce      -> GAN con pérdida NO saturante (G maximiza log D(G(z)))   [base]
  bce_sat  -> GAN original minimax (G minimiza log(1 - D(G(z))))
  hinge    -> pérdida hinge (SAGAN/BigGAN)
  wgan_gp  -> Wasserstein con penalización de gradiente
"""
import torch
import torch.nn.functional as F

KINDS = ("bce", "bce_sat", "hinge", "wgan_gp")


def gradient_penalty(D, real, fake, lam=10.0):
    b = real.size(0)
    eps = torch.rand(b, 1, 1, 1, device=real.device)
    x = (eps * real + (1 - eps) * fake).requires_grad_(True)
    grads = torch.autograd.grad(D(x).sum(), x, create_graph=True)[0]
    return lam * ((grads.view(b, -1).norm(2, dim=1) - 1) ** 2).mean()


def d_loss_fn(kind, D, real, fake, label_real=1.0, gp_lambda=10.0):
    """label_real<1 => suavizado de etiquetas (p. ej. 0.9) solo en las reales."""
    r, f = D(real), D(fake.detach())
    if kind in ("bce", "bce_sat"):
        loss = (F.binary_cross_entropy_with_logits(r, torch.full_like(r, label_real))
                + F.binary_cross_entropy_with_logits(f, torch.zeros_like(f)))
    elif kind == "hinge":
        loss = F.relu(1 - r).mean() + F.relu(1 + f).mean()
    elif kind == "wgan_gp":
        loss = f.mean() - r.mean() + gradient_penalty(D, real, fake.detach(), gp_lambda)
    else:
        raise ValueError(kind)
    return loss, r.detach(), f.detach()


def g_loss_fn(kind, D, fake):
    out = D(fake)
    if kind == "bce":
        return F.binary_cross_entropy_with_logits(out, torch.ones_like(out))
    if kind == "bce_sat":
        return -F.binary_cross_entropy_with_logits(out, torch.zeros_like(out))
    if kind in ("hinge", "wgan_gp"):
        return -out.mean()
    raise ValueError(kind)


def moment_loss(real, fake):
    """Compara medias y variación espacial de lotes a baja resolución."""
    real_low = F.adaptive_avg_pool2d(real, (8, 8))
    fake_low = F.adaptive_avg_pool2d(fake, (8, 8))
    mean_error = (real_low.mean(0) - fake_low.mean(0)).abs().mean()
    real_std = (real_low.var(0, unbiased=False) + 1e-6).sqrt()
    fake_std = (fake_low.var(0, unbiased=False) + 1e-6).sqrt()
    return mean_error + (real_std - fake_std).abs().mean()
