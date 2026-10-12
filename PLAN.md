# Organización del Proyecto 2

El universo y los datos se documentan en `dataset.md`. El protocolo previo se conserva en `experimentos.md` y `colab_runner.ipynb`. Los resultados y su interpretación se registran en `resultados.md`. El informe se organiza en `presentacion.md`.

## Secuencia

1. Construcción de dibujos originales y preparación a 64 × 64.
2. Registro de hipótesis y criterios.
3. Ejecución de la base y dos experimentos controlados.
4. Comparación de curvas, diversidad y ruido fijo.
5. Selección de personajes y prueba de vecinos.
6. Regeneración de la galería y comprobación de integridad.
7. Organización de la presentación y empaquetado de la entrega.

## Evidencia

| Evidencia | Ubicación |
|---|---|
| Conjunto y preparación | `dataset.md`, `data/processed/data_report.json` |
| Hipótesis previas | `experimentos.md`, `colab_runner.ipynb` |
| Curvas y evolución | `runs/<corrida>/` |
| Comparación de corridas | `evidencias/resumen_experimentos.json`, `comparacion.png` |
| Galería reproducible | `galeria/`, pesos finales de la corrida seleccionada |
| Vecinos y calibración | `nn_resultados/` |
| Informe | `presentacion.md`, `resultados.md` |
