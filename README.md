# Proyecto 1 - Monitoreo transaccional

Universidad del Valle de Guatemala  
Deep Learning 2026

Equipo:

- Nina Najera - 231088
- José Antón - 221041

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `proyecto1_najera_anton.ipynb` | Notebook ejecutado con los modelos A, B y C, las dos pruebas de falsificación y el análisis económico |
| `informe.pdf` | Informe para el Comité de Riesgos |
| `artefactos/` | Modelos, parámetros de preparación y resultados de la ejecución final |
| `figs/` | Figuras generadas por el notebook y utilizadas en el informe |
| `requirements.txt` | Versiones usadas para reproducir la ejecución |

## Ruta de datos

Se utiliza la Ruta A con datos sintéticos y un generador propio. La semilla confirmatoria es `20260905`.

El generador produce 102,087 transacciones de 700 clientes durante 120 días. La tasa de fraude es 1.14 por ciento. Se comprueba dentro del notebook que dos ejecuciones con la misma semilla producen exactamente el mismo conjunto.

Cada muestra contiene siete transacciones históricas y la transacción actual. La muestra intenta predecir si la transacción actual es fraudulenta.

## Reproducción

Se recomienda crear un entorno virtual con Python 3.13.

```bash
python -m pip install -r requirements.txt
python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1200 proyecto1_najera_anton.ipynb
```

También se puede abrir el notebook y ejecutar todas las celdas en orden.

El notebook crea automáticamente las carpetas `data`, `figs` y `artefactos`. La ejecución completa tarda cerca de dos minutos en CPU.

## Protocolo experimental

La partición es temporal. Los datos más antiguos forman entrenamiento, el siguiente bloque forma validación y las fechas finales forman prueba. Los escaladores y las estadísticas de normalización se ajustan solamente con entrenamiento.

Las decisiones de arquitectura, la regla de éxito de C y los umbrales económicos quedan cerrados antes de la sección final de prueba. Todas las métricas de prueba se calculan durante una única fase final.

La permutación controlada mantiene fija la transacción actual y baraja únicamente las siete transacciones históricas. De esta forma la identidad del evento evaluado no cambia.

## Declaración de uso de IA

Usamos Claude de Anthropic como asistente de programación para:

1. Redactar el andamiaje del generador, la construcción de ventanas, la arquitectura LSTM y las curvas de costo.
2. Redactar el texto narrativo del notebook y del informe.
3. Generar las figuras con matplotlib.

Verificamos que el generador es reproducible con la misma semilla, que la partición es estrictamente temporal, que las normalizaciones se ajustan solamente con entrenamiento y que las métricas corresponden a una ejecución completa.

### Tres decisiones técnicas importantes

1. Construcción causal con punteros deslizantes. Se consideró filtrar el DataFrame para cada transacción. Esa alternativa era demasiado lenta para más de cien mil transacciones. Los punteros avanzan una sola vez y reducen el costo del cálculo.

2. Separación de entradas entre A y B. Se consideró entregar variables agregadas al modelo secuencial. Se descartó para mantener una comparación clara. A recibe agregados y B recibe eventos ordenados.

3. Regla previa para la apuesta C. El éxito exige un margen medio mínimo de 0.01 de AUC-PR frente al mejor modelo individual dentro de cada partición. El margen observado en validación fue 0.0136, por lo que la apuesta cumple la regla establecida.

## Candidato al Proyecto Final

El modelo candidato principal es B. Sus pesos están en `artefactos/modelo_B_state.pt` y sus parámetros de preparación están en `artefactos/norm_stats.pkl`. El Modelo A está en `artefactos/modelo_A.joblib`. La extensión híbrida C está en `artefactos/modelo_C_meta.joblib`.

El equipo de riesgos usaría el puntaje durante la autorización de transacciones. Un puntaje por encima del umbral activaría una revisión adicional. No produciría un bloqueo definitivo sin intervención del sistema de reglas.

La entrada de B contiene ocho eventos. Son siete transacciones históricas y la transacción actual. Cada evento incluye monto, categoría, canal, hora y minutos desde el evento anterior. La salida es un puntaje continuo entre cero y uno.

Los límites principales son el uso de datos sintéticos, la tasa de fraude elevada, la ventana fija de ocho eventos y la cantidad pequeña de casos de `escalada` y `canal_raro`. Antes de producción se necesitan datos reales, calibración, costos operativos, variables de dispositivo y geolocalización, seguimiento de deriva y una estrategia para clientes con poco historial.
