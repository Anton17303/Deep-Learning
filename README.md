# Proyecto 1 — Monitoreo transaccional: detectar lo que el orden revela

Banco del Altiplano · Comité de Riesgos · Deep Learning 2026, Universidad del Valle de Guatemala

Equipo: *(completar con nombres y carnés)*

## Contenido de la entrega

| Archivo | Descripción |
|---|---|
| `proyecto1_<apellidos>.ipynb` (aquí: `Proyecto1_MonitoreoTransaccional.ipynb`) | Notebook ejecutado con A, B, la apuesta C, las dos pruebas de falsificación y el análisis económico |
| `informe.pdf` | Informe para el comité de riesgos (6 páginas, sin código) |
| `artefactos/` | Pesos de los modelos y parámetros de preparación |
| `data_gen.py`, `build_dataset.py`, `train_models.py`, `falsification_tests.py`, `apuesta_c.py`, `economics.py`, `figures.py` | Scripts fuente equivalentes a las celdas del notebook, por si se prefiere ejecutar por partes |
| `README.md` | Este archivo |

`presentacion.pdf` (máx. 8 diapositivas) queda pendiente de generar para la entrega final.

## Ruta de datos elegida

**Ruta A — datos sintéticos con generador propio** (`data_gen.py`), con semilla fija
(`SEED = 20260904`). Se verifica reproducibilidad: dos llamadas a `generate()` con la misma
semilla producen exactamente el mismo DataFrame.

## Cómo reproducir

```bash
pip install torch scikit-learn pandas numpy matplotlib reportlab joblib --break-system-packages
python3 data_gen.py          # genera data/transacciones_raw.csv
python3 build_dataset.py     # construye ventanas/agregados/secuencias + partición temporal
python3 train_models.py      # entrena Modelo A (Gradient Boosting) y Modelo B (LSTM)
python3 falsification_tests.py   # Prueba 1 (permutación) y Prueba 2 (por mecanismo)
python3 apuesta_c.py         # Apuesta C: híbrido A+B con hipótesis pre-registrada
python3 economics.py         # umbral óptimo y análisis de costo
python3 figures.py           # genera las figuras del informe
python3 make_informe.py      # genera informe.pdf
```

O, de forma equivalente, ejecutar `Proyecto1_MonitoreoTransaccional.ipynb` de principio a fin
(todas las celdas ya están ejecutadas en la entrega).

**Versiones clave:** Python 3, `torch==2.13.0+cu130` (CPU), `scikit-learn==1.8.0`, `pandas`,
`numpy`, `matplotlib`, `reportlab`.

## Declaración de uso de IA

Usamos Claude (Anthropic) como asistente de programación para:
1. Redactar el andamiaje de los scripts (generador de datos, construcción de ventanas con
   punteros deslizantes, arquitectura del LSTM en PyTorch, curvas de costo por umbral).
2. Redactar el texto narrativo del notebook y del informe.
3. Generar las figuras con matplotlib.

Lo que verificamos nosotros mismos: que el generador es reproducible con la misma semilla; que
la partición es estrictamente temporal (sin mezclar fechas futuras en train); que los
escaladores/normalizaciones se ajustan solo con datos de entrenamiento; que las métricas
reportadas (AUC-PR, costos) corresponden a una ejecución real y no a valores inventados; y que
el veredicto de la apuesta C se declaró antes de tocar el conjunto de prueba y no se cambió al
ver el resultado del test.

### Tres decisiones técnicas importantes

1. **Diseño del two-pointer para agregados causales, en vez de recalcular con pandas por cada
   fila.** Alternativa considerada: filtrar el DataFrame con `df[df.timestamp >= ...]` dentro de
   un loop por transacción (como en un primer borrador de `build_dataset.py`). Evidencia que
   inclinó la decisión: esa versión no terminaba de ejecutarse en un tiempo razonable sobre
   ~100,000 transacciones; el rediseño con punteros deslizantes (`p24`, `p1h`, `day_start`)
   corre en segundos porque cada puntero solo avanza, nunca retrocede, dado que los datos están
   ordenados por tiempo dentro de cada cliente.

2. **Qué comparten y qué NO comparten los modelos A y B.** Alternativa considerada: dejar que el
   Modelo B también reciba los 8 agregados como entrada adicional (modelo "enriquecido"). Se
   descartó porque mezclaría la pregunta de investigación: si B ve los agregados, cualquier
   mejora sobre A ya no se puede atribuir limpiamente al orden. Evidencia: el enunciado exige que
   "todas las comparaciones usen los mismos datos" pero también que B reciba "eventos ordenados"
   como su entrada distintiva — se optó por una separación estricta (A solo agregados, B solo
   secuencia cruda) para que la Prueba 1 (permutación) sea una prueba limpia del valor del orden
   y no una mezcla de señales.

3. **Umbral de éxito de la apuesta C fijado en 0.01 de AUC-PR y decidido con 5-fold CV sobre
   validación, no con el desempeño en test.** Alternativa considerada: fijar el umbral después de
   ver cómo se comportaba el híbrido en el conjunto de prueba (lo cual habría maximizado la
   probabilidad de reportar una "apuesta exitosa"). Se descartó explícitamente porque el
   enunciado penaliza con -10 puntos "elegir arquitectura, umbral o apuesta mirando el conjunto
   de prueba", y porque el objetivo del ejercicio es la honestidad del proceso de decisión, no el
   resultado más favorable. Evidencia: con el criterio pre-registrado el margen en validación
   (+0.004) no alcanzó el umbral (0.01), así que el veredicto se reportó como "no concluyente"
   aunque el resultado en test (visto una sola vez, después) hubiera sido más favorable.

## Candidato al Proyecto Final

- **Modelo que conservaríamos:** el Modelo B (LSTM secuencial). Su artefacto está en
  `artefactos/modelo_B_state.pt` (pesos) junto con `artefactos/norm_stats.pkl` (medias/desviaciones
  de normalización de monto y delta de tiempo, y las columnas de agregados usadas por A, para
  referencia). El Modelo A vive en `artefactos/modelo_A.joblib` (incluye el `StandardScaler` ya
  ajustado) y el meta-modelo de la apuesta C en `artefactos/modelo_C_meta.joblib`, por si el
  Proyecto Final decide retomar la línea híbrida en vez de B solo.
- **Quién usaría el puntaje y qué decisión tomaría:** el equipo de riesgos del banco, en el flujo
  de autorización de transacciones. Con el umbral óptimo hallado en validación (0.63 para B), un
  puntaje por encima del umbral dispararía una retención/verificación adicional de la transacción
  antes de autorizarla (no un bloqueo automático definitivo, dado que la precisión no es del
  100%).
- **Contrato preliminar de entrada/salida:** entrada = las últimas 8 transacciones del cliente
  (monto, categoría de comercio, canal, hora, minutos desde la transacción anterior), en el mismo
  formato usado para construir `seq_amt`, `seq_cat`, `seq_chan`, `seq_hour`, `seq_delta` en
  `build_dataset.py`. Salida = un puntaje continuo de riesgo en [0, 1] (`sigmoid` del LSTM), no
  una decisión binaria — la binarización por umbral queda a criterio del sistema que lo consuma.
- **Principales límites, riesgos y datos que faltarían:** (1) el modelo se entrenó con datos
  sintéticos; antes de producción necesitaría reentrenarse con transacciones reales etiquetadas.
  (2) la tasa de fraude sintética (~1.1%) es más alta que la real, así que los umbrales y el
  ahorro económico estimado deberían recalibrarse con la tasa real observada. (3) el mecanismo
  `canal_raro` (transacciones únicas y atípicas) es donde ambos modelos rinden peor — haría falta
  investigar variables adicionales (geolocalización real, huella del dispositivo) para ese caso.
  (4) el modelo asume exactamente 8 transacciones previas disponibles; clientes con menos
  historial no generan predicción con este diseño y necesitarían una regla de respaldo. Todavía
  no se implementa API, monitoreo ni *dashboard* — eso corresponde al Proyecto Final.
