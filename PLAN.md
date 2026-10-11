# Plan de trabajo — Proyecto 2 (GAN de personajes)
Entrega: **domingo 11 oct 2026, 23:59** (Canvas). Hoy es viernes 9: quedan ~2 días, hay que ir en paralelo.

## Ya está hecho (código base)
- `prepare_data.py` — recorte/resize/dedupe del dataset y reporte (`data_report.json`).
- `train.py` — DCGAN 64x64, rejilla de ruido fijo, curvas, métrica de diversidad, checkpoints, reanudación.
- `gan/losses.py` — `bce` (no saturante, **base**), `bce_sat` (original), `hinge`, `wgan_gp`, suavizado de etiquetas.
- `gan/models.py` — D con `--spectral`, `--d_dropout`, `--d_norm`.
- `analysis.py` — curvas, evolución de muestras, comparación entre corridas.
- `generate_gallery.py` — candidatos numerados por semilla, galería final con `z` y tasa de selección.
- `nn_test.py` — vecinos más cercanos (CNN + píxeles) con calibración contra imágenes reales.
- `run_experiments.sh` — base + experimento de pérdida + experimento de estabilización, mismas condiciones.

## Reparto propuesto (ajustable)
| Persona A (código/entrenamiento) | Persona B (universo/datos/evidencias) |
|---|---|
| Correr la DCGAN base en Colab y vigilar colapso | **Definir el universo** (estilo, ambiente, rasgos; 1 párrafo) |
| **Experimento de pérdida** (hipótesis → corrida → análisis) | **Conseguir y documentar el dataset** (origen, licencia, tamaño) y correr `prepare_data.py` |
| README, semillas, versiones, declaración de IA | **Experimento de estabilización** (hipótesis → corrida → análisis) |
| Curvas interpretadas del base y del experimento de pérdida | **Galería final + prueba NN** y la reflexión final (caso más difícil de defender) |
| Diapositivas: arquitectura, pérdida, problemas | Diapositivas: universo, datos, estabilización, galería, NN, **bonificación (nombre y clase de cada personaje)** |
| Ambos | Matriz de evidencias (1 diapositiva) y revisión cruzada del PDF |

El trabajo de B es el que más pesa en rúbrica (datos 8, estabilización 10, galería 12, NN 8, universo 10).

## Cronograma
- **Vie 9**: B define universo + consigue datos (mínimo ~2–5 mil imágenes de estilo consistente). A sube el repo a Drive y prueba `train.py` con un dataset pequeño.
- **Sáb 10 mañana**: `prepare_data.py` → `train.py --name base` (100 épocas ≈ minutos en T4). Revisar rejilla de ruido fijo.
- **Sáb 10 tarde**: `./run_experiments.sh` (escribir antes las hipótesis en `experimentos.md`). Elegir mejor modelo.
- **Dom 11 mañana**: `generate_gallery.py` (200 candidatos → elegir 10), `nn_test.py`, figuras con `analysis.py`.
- **Dom 11 tarde**: PDF (≤12 diapositivas + matriz), README, empaquetar. **Dejar margen: subir a Canvas antes de las 22:00.**

## Mapa de la rúbrica → dónde sale la evidencia
| Evidencia | Archivo que la produce |
|---|---|
| Rejilla de ruido fijo | `runs/<exp>/grids/*.png`, `python analysis.py evolution ...` |
| Curvas de pérdida | `python analysis.py curves runs/<exp>` |
| Vecinos más cercanos | `python nn_test.py` → `nn_resultados/vecinos.png` |
| Tasa de selección | `galeria/seleccion.json` |
| Comparación de experimentos | `python analysis.py compare ...` → `comparacion.png` |
| Galería regenerable | `generate_gallery.py` + `G_final.pt` + semillas |
