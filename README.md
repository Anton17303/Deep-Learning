# Proyecto 2 — Diseño generativo de personajes (Deep Learning 2026)

**Universo:** (completar: 3–5 líneas)
**Datos:** (origen, licencia/permiso, tamaño, preparación)

## Ejecutar (Google Colab / Kaggle con GPU)
```bash
pip install -r requirements.txt
python prepare_data.py --raw data/raw --out data/processed --size 64
python train.py --data data/processed --name base --epochs 100
./run_experiments.sh data/processed 100
python analysis.py curves runs/base
python analysis.py evolution runs/base --epochs 0 5 25 50 100
python generate_gallery.py --ckpt runs/base/ckpt/G_final.pt --n 200
python generate_gallery.py --ckpt runs/base/ckpt/G_final.pt --n 200 --select <10 semillas> --criterio "<criterio>"
python nn_test.py --data data/processed --galeria galeria
```
La galería se regenera con `generate_gallery.py` a partir de `G_final.pt` y las semillas de `galeria/seleccion.json`.
Pesos del modelo final: (enlace si no caben en Canvas).

## Versiones y semillas
- Python / torch / torchvision: (completar con `pip freeze | grep -i torch`)
- Semilla de entrenamiento 42; semilla del ruido de evaluación 1234; cada personaje = una semilla (ver `galeria/seleccion.json`).
