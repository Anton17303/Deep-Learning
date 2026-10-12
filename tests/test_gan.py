"""Comprobaciones de gradientes, control experimental y datos reproducibles."""
import random
import unittest

import torch

from build_dataset import draw_creature
from gan.losses import d_loss_fn, g_loss_fn
from gan.models import Discriminator, Generator
from gan.utils import make_fixed_noise, set_seed


class GANChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def test_loss_gradients_and_image_range(self):
        for loss in ["bce", "bce_sat", "hinge", "wgan_gp"]:
            with self.subTest(loss=loss):
                set_seed(42)
                generator = Generator(8, 4)
                discriminator = Discriminator(4, norm="none")
                fake = generator(make_fixed_noise(2, 8))
                self.assertEqual(tuple(fake.shape), (2, 3, 64, 64))
                self.assertLessEqual(fake.abs().max().item(), 1)
                real = torch.randn_like(fake).clamp(-1, 1)
                d_loss, _, _ = d_loss_fn(loss, discriminator, real, fake)
                d_loss.backward()
                self.assertTrue(all(p.grad is None for p in generator.parameters()))
                self.assertTrue(all(torch.isfinite(p.grad).all() for p in discriminator.parameters()))
                g_loss = g_loss_fn(loss, discriminator, fake)
                g_loss.backward()
                self.assertTrue(all(torch.isfinite(p.grad).all() for p in generator.parameters()))
                self.assertGreater(sum(p.grad.abs().sum().item() for p in generator.parameters()), 0)

    def test_spectral_variant_keeps_original_weights_and_rng(self):
        set_seed(42)
        baseline = Discriminator(4)
        baseline_rng = torch.get_rng_state()
        set_seed(42)
        spectral = Discriminator(4, spectral=True)
        self.assertTrue(torch.equal(baseline_rng, torch.get_rng_state()))
        for key, value in baseline.state_dict().items():
            spectral_key = key[:-6] + "weight_orig" if key.endswith("weight") and value.ndim == 4 else key
            self.assertTrue(torch.equal(value, spectral.state_dict()[spectral_key]), key)

    def test_data_drawing_is_reproducible(self):
        first, traits = draw_creature(random.Random(20261011))
        second, second_traits = draw_creature(random.Random(20261011))
        self.assertEqual(first.tobytes(), second.tobytes())
        self.assertEqual(traits, second_traits)
        self.assertEqual(first.size, (64, 64))


if __name__ == "__main__":
    unittest.main()
