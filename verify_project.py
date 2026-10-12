"""Verifica condiciones experimentales y regeneración exacta de los personajes."""
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import torch

from gan.images import ImageDataset, save_grid
from gan.conditioning import input_from_seed, model_noise_size
from gan.models import Generator


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    torch.set_num_threads(4)
    root = Path(__file__).resolve().parent
    configs = []
    for name in ["base", "exp_loss_hinge", "exp_stab_sn"]:
        run = root / "runs" / name
        config = json.loads((run / "config.json").read_text(encoding="utf-8"))
        configs.append(config)
        with (run / "metrics.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        require([int(row["epoch"]) for row in rows] == list(range(config["epochs"] + 1)),
                f"{name}: épocas incompletas o duplicadas.")
        with (run / "losses.csv").open(newline="", encoding="utf-8") as stream:
            losses = list(csv.DictReader(stream))
        expected = config["epochs"] * (config["image_count"] // config["bs"])
        require([int(row["iter"]) for row in losses] == list(range(1, expected + 1)),
                f"{name}: iteraciones incompletas o duplicadas.")
        require((run / "ckpt" / "G_final.pt").is_file(), f"{name}: faltan pesos.")
    ignored = {"name", "loss", "spectral"}
    for config in configs[1:]:
        require({k: v for k, v in configs[0].items() if k not in ignored}
                == {k: v for k, v in config.items() if k not in ignored},
                "Las condiciones fijas difieren entre corridas.")
    require(configs[0]["loss"] == "bce" and not configs[0]["spectral"], "Base inválida.")
    require(configs[1]["loss"] == "hinge" and not configs[1]["spectral"], "Experimento de pérdida inválido.")
    require(configs[2]["loss"] == "bce" and configs[2]["spectral"], "Experimento de estabilización inválido.")
    fixed = torch.load(root / "runs/base/fixed_noise.pt", weights_only=True)
    for name in ["exp_loss_hinge", "exp_stab_sn"]:
        require(torch.equal(fixed, torch.load(root / "runs" / name / "fixed_noise.pt", weights_only=True)),
                "El ruido fijo no coincide.")
    dataset = ImageDataset(root / "data/processed")
    require(dataset.fingerprint() == configs[0]["dataset_sha256"], "El conjunto cambió después del entrenamiento.")
    for name in ["refined", "moment_refined", "conditional", "conditional_refined"]:
        run = root / "runs" / name
        config = json.loads((run / "config.json").read_text(encoding="utf-8"))
        with (run / "metrics.csv").open(newline="", encoding="utf-8") as stream:
            epochs = [int(row["epoch"]) for row in csv.DictReader(stream)]
        require(epochs == list(range(config["epochs"] + 1)), f"{name}: fases incompletas.")
        require(config["dataset_sha256"] == configs[0]["dataset_sha256"], f"{name}: conjunto distinto.")
    selection = json.loads((root / "galeria/seleccion.json").read_text(encoding="utf-8"))
    require(len(selection["personajes"]) >= 10, "La galería contiene menos de 10 personajes.")
    checkpoint = root / selection["checkpoint"]
    require(hashlib.sha256(checkpoint.read_bytes()).hexdigest() == selection["checkpoint_sha256"],
            "El checkpoint de la galería cambió.")
    config = torch.load(checkpoint, map_location="cpu", weights_only=True)["config"]
    require(config["dataset_sha256"] == dataset.fingerprint(), "El modelo de la galería utilizó otro conjunto.")
    if config.get("conditional", False):
        manifest_bytes = (root / "data/raw/manifest.json").read_bytes()
        normalized = manifest_bytes.replace(b"\r\n", b"\n")
        signatures = {hashlib.sha256(value).hexdigest() for value in
                      [manifest_bytes, normalized, normalized.replace(b"\n", b"\r\n")]}
        require(config["condition_manifest_sha256"] in signatures, "El manifiesto de atributos cambió.")
    if config.get("initialize_from"):
        initial_path = root / config["initialize_from"].replace("\\", "/")
        require(hashlib.sha256(initial_path.read_bytes()).hexdigest() == config["initialize_from_sha256"],
                "Los pesos utilizados para iniciar el ajuste cambiaron.")
    png_hashes = []
    for item in selection["personajes"]:
        path = root / "galeria" / item["archivo"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == item["sha256_png"], "Una imagen fue modificada después de la selección.")
        png_hashes.append(digest)
        vector = torch.load(root / "galeria" / f"personaje_{item['personaje']:02d}_z.pt", weights_only=True)
        require(torch.equal(vector, input_from_seed(item["seed"], config)), "El vector no coincide con su semilla.")
        require(vector.flatten().tolist() == item["z"], "El vector del manifiesto no coincide.")
    require(len(set(png_hashes)) == len(png_hashes), "La galería contiene copias exactas.")
    (root / "tmp").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root / "tmp", prefix="gallery_replay_") as directory:
        subprocess.run([sys.executable, str(root / "generate_gallery.py"), "--from_selection",
                        str(root / "galeria/seleccion.json"), "--galeria", directory], cwd=root, check=True)
        if config.get("initialize_from"):
            source = torch.load(initial_path, map_location="cpu", weights_only=True)
            original_config = source["config"]
            generator = Generator(model_noise_size(original_config), original_config["ngf"],
                                  architecture=original_config.get("g_arch", "dcgan"))
            generator.load_state_dict(source["G"])
            generator.eval()
            training_run = checkpoint.parents[1]
            fixed_noise = torch.load(training_run / "fixed_noise.pt", weights_only=True)
            with torch.no_grad():
                initial_images = generator(fixed_noise)
            rendered = Path(directory) / "initial.png"
            save_grid(initial_images, rendered)
            require(rendered.read_bytes() == (training_run / "grids/epoch_000.png").read_bytes(),
                    "La etapa cero no corresponde a los pesos de origen declarados.")
    with (root / "nn_resultados/vecinos.csv").open(newline="", encoding="utf-8") as stream:
        neighbors = list(csv.DictReader(stream))
    require({row["archivo"] for row in neighbors} == {item["archivo"] for item in selection["personajes"]},
            "La prueba de vecinos no corresponde a la galería.")
    print("Verificación completa: tres corridas controladas, ruido fijo idéntico y galería regenerada sin cambios.")


if __name__ == "__main__":
    main()
