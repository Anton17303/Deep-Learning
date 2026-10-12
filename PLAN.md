# Organizaci?n del Proyecto 2

El universo y los datos se documentan en `dataset.md`. El protocolo previo se conserva en `experimentos.md` y `colab_runner.ipynb`. Los resultados y su interpretaci?n se registran en `resultados.md`. El informe se organiza en `presentacion.md`.

## Secuencia

1. Construcci?n de dibujos originales y preparaci?n a 64 ? 64.
2. Registro de hip?tesis y criterios.
3. Ejecuci?n de la base y dos experimentos controlados.
4. Comparaci?n de curvas, diversidad y ruido fijo.
5. Selecci?n de personajes y prueba de vecinos.
6. Regeneraci?n de la galer?a y comprobaci?n de integridad.
7. Organizaci?n de la presentaci?n y empaquetado de la entrega.

## Evidencia

| Evidencia | Ubicaci?n |
|---|---|
| Conjunto y preparaci?n | `dataset.md`, `data/processed/data_report.json` |
| Hip?tesis previas | `experimentos.md`, `colab_runner.ipynb` |
| Curvas y evoluci?n | `runs/<corrida>/` |
| Comparaci?n de corridas | `evidencias/resumen_experimentos.json`, `comparacion.png` |
| Galer?a reproducible | `galeria/`, pesos finales de la corrida seleccionada |
| Vecinos y calibraci?n | `nn_resultados/` |
| Informe | `presentacion.md`, `resultados.md` |
