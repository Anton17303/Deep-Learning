"""Construye dibujos paramétricos originales para el conjunto de entrenamiento."""
import argparse
import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

PALETTE = [(61, 204, 181), (103, 157, 237), (197, 116, 218),
           (237, 163, 91), (135, 211, 111), (230, 127, 158)]
BACKGROUND = (13, 20, 35)


def draw_creature(rng):
    image = Image.new("RGB", (128, 128), BACKGROUND)
    draw = ImageDraw.Draw(image)
    color = rng.choice(PALETTE)
    color = tuple(max(0, min(255, c + rng.randint(-12, 12))) for c in color)
    light = tuple(min(255, int(c * 0.45 + 140)) for c in color)
    dark = tuple(int(c * 0.55) for c in color)
    cx, cy = 64 + rng.randint(-5, 5), 66 + rng.randint(-4, 4)
    rx, ry = rng.randint(24, 36), rng.randint(26, 35)
    shape = rng.choice(["oval", "round", "bell"])
    antenna = rng.choice(["single", "double", "horns", "none"])
    legs = rng.choice([2, 3, 4])
    for i in range(legs):
        x = int(cx - rx * 0.65 + i * (1.3 * rx) / (legs - 1))
        tip = x + rng.randint(-8, 8)
        end = cy + ry + rng.randint(8, 16)
        draw.line([(x, cy + ry - 8), (tip, end)], fill=dark, width=8)
        draw.ellipse((tip - 5, end - 3, tip + 5, end + 3), fill=color)
    if antenna != "none":
        xs = [cx] if antenna == "single" else [cx - rx // 2, cx + rx // 2]
        for x in xs:
            end_x = x + (rng.randint(-10, 10) if antenna != "horns" else (-8 if x < cx else 8))
            end_y = max(8, cy - ry - rng.randint(10, 20))
            draw.line([(x, cy - ry + 8), (end_x, end_y)], fill=color, width=5)
            draw.ellipse((end_x - 4, end_y - 4, end_x + 4, end_y + 4), fill=light)
    draw.line([(cx - rx + 3, cy + 3), (cx - rx - 9, cy + 14)], fill=dark, width=7)
    draw.line([(cx + rx - 3, cy + 3), (cx + rx + 9, cy + 14)], fill=dark, width=7)
    bounds = (cx - rx, cy - ry, cx + rx, cy + ry)
    if shape == "oval":
        draw.ellipse(bounds, fill=color)
    elif shape == "round":
        draw.rounded_rectangle(bounds, radius=18, fill=color)
    else:
        draw.polygon([(cx - rx, cy + ry), (cx - rx + 4, cy - 12),
                      (cx - rx // 2, cy - ry), (cx + rx // 2, cy - ry),
                      (cx + rx - 4, cy - 12), (cx + rx, cy + ry)], fill=color)
    eye_count = rng.choice([1, 2, 3])
    eye_y = cy - rng.randint(4, 12)
    spacing = 15 if eye_count == 3 else 24
    for i in range(eye_count):
        x = int(cx + (i - (eye_count - 1) / 2) * spacing)
        eye_radius = 7 if eye_count != 1 else 10
        draw.ellipse((x - eye_radius, eye_y - eye_radius, x + eye_radius, eye_y + eye_radius), fill=(232, 245, 231))
        draw.ellipse((x - 3, eye_y - 4, x + 3, eye_y + 4), fill=(17, 29, 44))
        draw.point((x - 1, eye_y - 2), fill=(255, 255, 255))
    mouth = rng.choice(["smile", "small", "flat"])
    if mouth == "smile":
        draw.arc((cx - 9, cy + 1, cx + 9, cy + 17), 0, 180, fill=dark, width=3)
    elif mouth == "small":
        draw.ellipse((cx - 3, cy + 7, cx + 3, cy + 12), fill=dark)
    else:
        draw.line((cx - 7, cy + 10, cx + 7, cy + 10), fill=dark, width=3)
    for _ in range(rng.randint(2, 5)):
        x, y = cx + rng.randint(-rx + 8, rx - 8), cy + rng.randint(17, ry - 2)
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=light)
    return image.resize((64, 64), Image.Resampling.LANCZOS), {
        "shape": shape, "antenna": antenna, "legs": legs, "eyes": eye_count,
        "color": color, "mouth": mouth, "center": [cx, cy], "radii": [rx, ry]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/raw/luminarios")
    parser.add_argument("--n", type=int, default=1536)
    parser.add_argument("--seed", type=int, default=20261011)
    args = parser.parse_args()
    if args.n < 64:
        parser.error("Se requieren al menos 64 imágenes.")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.glob("*.png")):
        raise FileExistsError("La carpeta ya contiene imágenes; se conserva el conjunto existente.")
    rng, seen, records = random.Random(args.seed), set(), []
    while len(records) < args.n:
        image, traits = draw_creature(rng)
        digest = hashlib.sha256(image.tobytes()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        filename = f"luminario_{len(records):05d}.png"
        image.save(out / filename)
        records.append({"file": filename, "sha256_pixels": digest, **traits})
    manifest = {"universe": "Luminarios del arrecife astral", "source": "build_dataset.py",
                "method": "Dibujos geométricos paramétricos; no se utiliza un modelo generativo externo.",
                "permission": "Material original generado dentro del proyecto; sin imágenes de terceros.",
                "seed": args.seed, "count": args.n, "size": [64, 64], "images": records}
    (out.parent / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{args.n} imágenes originales -> {out}")


if __name__ == "__main__":
    main()
