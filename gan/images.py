"""Carga de imágenes RGB y exportación sin dependencia de torchvision."""
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps
from torch.utils.data import Dataset


def image_tensor(path, size=64):
    with Image.open(path) as source:
        image = ImageOps.fit(source.convert("RGB"), (size, size), method=Image.Resampling.LANCZOS)
        return torch.from_numpy(np.asarray(image).copy()).permute(2, 0, 1).float() / 255


class ImageDataset(Dataset):
    def __init__(self, root, size=64, flip=False, conditional=False):
        self.root = Path(root)
        extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        self.files = sorted(p for p in Path(root).rglob("*") if p.suffix.lower() in extensions)
        if not self.files:
            raise ValueError("El conjunto no contiene imágenes.")
        self.images = torch.stack([image_tensor(p, size) for p in self.files])
        self.flip = flip
        self.conditions = None
        if conditional:
            from gan.conditioning import condition_from_record
            manifest_path = self.root.parent / "raw" / "manifest.json"
            records = json.loads(manifest_path.read_text(encoding="utf-8"))["images"]
            if len(records) != len(self.files):
                raise ValueError("El manifiesto de condiciones no coincide con el conjunto.")
            for tensor, record in zip(self.images, records):
                pixels = (tensor * 255).round().byte().permute(1, 2, 0).numpy().tobytes()
                if hashlib.sha256(pixels).hexdigest() != record["sha256_pixels"]:
                    raise ValueError("Los atributos no corresponden a las imágenes procesadas.")
            self.conditions = torch.stack([condition_from_record(record) for record in records])
            self.condition_manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        image = self.images[index]
        if self.flip and torch.rand(()) < 0.5:
            image = image.flip(-1)
        normalized = image * 2 - 1
        return (normalized, self.conditions[index]) if self.conditions is not None else normalized

    def fingerprint(self):
        digest = hashlib.sha256()
        for path in self.files:
            digest.update(path.relative_to(self.root).as_posix().encode())
            digest.update(path.read_bytes())
        return digest.hexdigest()


def save_image(tensor, path):
    array = ((tensor.detach().cpu().clamp(-1, 1) + 1) * 127.5).round().byte()
    Image.fromarray(array.permute(1, 2, 0).numpy()).save(path)


def save_grid(tensors, path, columns=4, padding=3):
    rows = (len(tensors) + columns - 1) // columns
    height, width = tensors.shape[-2:]
    canvas = Image.new("RGB", (columns * (width + padding) + padding,
                               rows * (height + padding) + padding), (15, 20, 32))
    for i, tensor in enumerate(tensors):
        array = ((tensor.detach().cpu().clamp(-1, 1) + 1) * 127.5).round().byte()
        image = Image.fromarray(array.permute(1, 2, 0).numpy())
        canvas.paste(image, (padding + i % columns * (width + padding),
                             padding + i // columns * (height + padding)))
    canvas.save(path)
