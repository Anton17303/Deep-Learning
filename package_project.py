"""Empaqueta únicamente los archivos y resultados del proyecto GAN."""
import argparse
import json
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="entrega/proyecto_2_luminarios.zip")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = root / args.out
    required = ["README.md", "dataset.md", "experimentos.md", "resultados.md", "presentacion.md",
                "colab_runner.ipynb", "galeria/seleccion.json", "nn_resultados/resumen.json"]
    missing = [path for path in required if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError(f"Faltan archivos de entrega: {missing}")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = set()
    for pattern in ["*.py", "*.md", "requirements.txt", "requirements-lock.txt", "colab_runner.ipynb", "run_experiments.sh"]:
        files.update(root.glob(pattern))
    files.discard(root / "PLAN.md")
    for folder in ["gan", "tests", "evidencias", "galeria", "nn_resultados", "runs/base", "runs/exp_loss_hinge", "runs/exp_stab_sn", "runs/refined", "runs/moment_refined", "data/processed"]:
        files.update(path for path in (root / folder).rglob("*") if path.is_file()
                     and "__pycache__" not in path.parts and path.name not in ["last.pt", "last.tmp"]
                     and not path.name.startswith("G_ep"))
    files.add(root / "data/raw/manifest.json")
    files.add(root / "comparacion.png")
    selection = json.loads((root / "galeria/seleccion.json").read_text(encoding="utf-8"))
    files.add(root / selection["checkpoint"])
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(root).as_posix())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError("El archivo de entrega no pasó la comprobación de integridad.")
    print(f"{output.name}: {len(files)} archivos, {output.stat().st_size / 1024 ** 2:.2f} MiB")


if __name__ == "__main__":
    main()
