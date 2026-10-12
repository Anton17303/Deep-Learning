"""Codificación de atributos visuales y vectores de entrada reproducibles."""
import torch

from gan.utils import z_from_seed

COLORS = [(61, 204, 181), (103, 157, 237), (197, 116, 218),
          (237, 163, 91), (135, 211, 111), (230, 127, 158)]
COLOR_NAMES = ["turquesa", "azul", "violeta", "naranja", "verde", "rosa"]
SHAPES = ["oval", "round", "bell"]
ANTENNAS = ["single", "double", "horns", "none"]
DIM = 16


def encode(color, eyes, shape, antenna):
    vector = torch.zeros(DIM)
    vector[color] = 1
    vector[6 + eyes - 1] = 1
    vector[9 + shape] = 1
    vector[12 + antenna] = 1
    return vector


def condition_from_record(record):
    color = min(range(6), key=lambda i: sum((a - b) ** 2 for a, b in zip(record["color"], COLORS[i])))
    return encode(color, record["eyes"], SHAPES.index(record["shape"]), ANTENNAS.index(record["antenna"]))


def attributes_from_seed(seed):
    index = int(seed) % 216
    return {"color": COLOR_NAMES[index % 6], "ojos": (index // 6) % 3 + 1,
            "cuerpo": SHAPES[(index // 18) % 3], "antenas": ANTENNAS[(index // 54) % 4]}


def condition_from_seed(seed):
    index = int(seed) % 216
    return encode(index % 6, (index // 6) % 3 + 1, (index // 18) % 3, (index // 54) % 4)


def input_from_seed(seed, config):
    noise = z_from_seed(seed, config["nz"])
    if config.get("conditional", False):
        return torch.cat([noise, condition_from_seed(seed).view(1, -1)], dim=1)
    return noise


def model_noise_size(config):
    return config["nz"] + (DIM if config.get("conditional", False) else 0)


def critic_input(image, condition):
    channels = condition[:, :, None, None].expand(-1, -1, image.shape[-2], image.shape[-1])
    return torch.cat([image, channels], dim=1)
