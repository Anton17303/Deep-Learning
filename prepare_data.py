"""Prepara el dataset: recorte cuadrado centrado, resize, dedupe, PNG numerados.
Uso: python prepare_data.py --raw data/raw --out data/processed --size 64
Genera out/all/*.png (formato ImageFolder) y out/data_report.json.
"""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument("--raw", required=True)
p.add_argument("--out", default="data/processed")
p.add_argument("--size", type=int, default=64)
p.add_argument("--min_side", type=int, default=48, help="descarta imágenes más pequeñas")
a = p.parse_args()

exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
files = sorted(f for f in Path(a.raw).rglob("*") if f.suffix.lower() in exts)
out = Path(a.out) / "all"; out.mkdir(parents=True, exist_ok=True)
if any(out.glob("*.png")):
    raise FileExistsError("La carpeta de salida ya contiene imágenes.")
if not files:
    raise ValueError("No se encontraron imágenes de entrada.")
seen, kept, small, dup, bad = set(), 0, 0, 0, 0
for f in files:
    try:
        im = Image.open(f)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            bg.alpha_composite(im); im = bg
        im = im.convert("RGB")
    except Exception:
        bad += 1; continue
    w, h = im.size
    if min(w, h) < a.min_side:
        small += 1; continue
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    im = im.resize((a.size, a.size), Image.LANCZOS)
    h_ = hashlib.md5(im.tobytes()).hexdigest()
    if h_ in seen:
        dup += 1; continue
    seen.add(h_)
    im.save(out / f"{kept:05d}.png"); kept += 1
rep = dict(raw_files=len(files), kept=kept, too_small=small, duplicates=dup, unreadable=bad, size=a.size)
with open(Path(a.out) / "data_report.json", "w", encoding="utf-8") as stream:
    json.dump(rep, stream, indent=2)
print(rep)
