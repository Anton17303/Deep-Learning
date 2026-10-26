# Resultados de Text-to-SQL

La exactitud se calcula mediante ejecución en MySQL 8.4.10. Los niveles fácil, medio y difícil tienen pesos 1, 2 y 3. El oráculo utiliza las respuestas de referencia y solo comprueba el evaluador.

| Evaluación | Aciertos | EX ponderada | Tiempo medio (s) | Tiempo máximo (s) |
|---|---:|---:|---:|---:|
| baseline | 15/40 | 0.280 | 15.67 | 25.44 |
| lora_r8 | 21/40 | 0.439 | 11.49 | 25.27 |
| lora_r16 | 20/40 | 0.402 | 11.83 | 25.31 |
| reparacion | 21/40 | 0.427 | 13.20 | 27.22 |
| validacion_propia | 21/40 | 0.439 | 11.49 | 25.27 |

## Entrenamiento

| Rango | Parámetros entrenables | Pasos | Ejemplos procesados | Tiempo (min) |
|---|---:|---:|---:|---:|
| 8 | 540,672 | 76/76 | 304/3023 | 37.11 |
| 16 | 1,081,344 | 76/76 | 304/3023 | 41.04 |

Se utiliza la misma base NF4, semilla, orden de ejemplos, tasa de aprendizaje y presupuesto. El rango es el único factor de comparación. La cobertura de 304 ejemplos no equivale a recorrer el corpus completo.

Las curvas se conservan en lora_r8/loss.png y lora_r16/loss.png, junto con sus CSV por paso.

En rango 8, la pérdida media de los primeros diez pasos fue 0.520 y la de los últimos diez fue 0.266.

En rango 16, la pérdida media de los primeros diez pasos fue 0.520 y la de los últimos diez fue 0.268.

Estos promedios describen el ajuste sobre ejemplos de entrenamiento distintos. Una pérdida menor no garantiza una EX mayor en esquemas nuevos; la selección se apoya en la evaluación por ejecución.

El rango 16 obtuvo una diferencia de EX de -0.037 frente al rango 8. No se observó una mejora de EX al aumentar el rango bajo este presupuesto. La comparación se limita a 40 preguntas y dos esquemas; no demuestra una ventaja general sobre bases desconocidas.

## Efecto de la reparación

La reparación convirtió 1 errores en aciertos y perdió 1 aciertos. La diferencia de EX fue -0.012; el tiempo medio pasó de 11.49 a 13.20 segundos.

La corrección de nombres puede resolver identificadores cercanos. La regeneración tiene un presupuesto limitado y puede terminar con una consulta incompleta. Los filtros o las agregaciones incorrectos que sí se ejecutan no producen un error de MySQL para activar otra generación.

## Errores: baseline

| Categoría | Cantidad |
|---|---:|
| JOIN | 1 |
| agregación | 6 |
| columna o tabla inexistente | 13 |
| filtro | 2 |
| resultado distinto | 1 |
| sintaxis | 2 |

| Nivel | Aciertos |
|---|---:|
| 1 | 9/12 |
| 2 | 4/14 |
| 3 | 2/14 |

## Errores: lora_r8

| Categoría | Cantidad |
|---|---:|
| JOIN | 2 |
| agregación | 5 |
| columna o tabla inexistente | 8 |
| filtro | 3 |
| sintaxis | 1 |

| Nivel | Aciertos |
|---|---:|
| 1 | 10/12 |
| 2 | 7/14 |
| 3 | 4/14 |

## Errores: lora_r16

| Categoría | Cantidad |
|---|---:|
| JOIN | 2 |
| agregación | 3 |
| columna o tabla inexistente | 10 |
| filtro | 4 |
| resultado distinto | 1 |

| Nivel | Aciertos |
|---|---:|
| 1 | 10/12 |
| 2 | 7/14 |
| 3 | 3/14 |

## Errores: reparacion

| Categoría | Cantidad |
|---|---:|
| JOIN | 2 |
| agregación | 5 |
| columna o tabla inexistente | 6 |
| filtro | 3 |
| sintaxis | 3 |

| Nivel | Aciertos |
|---|---:|
| 1 | 11/12 |
| 2 | 6/14 |
| 3 | 4/14 |

## Errores: validacion_propia

| Categoría | Cantidad |
|---|---:|
| JOIN | 2 |
| agregación | 5 |
| columna o tabla inexistente | 8 |
| filtro | 3 |
| sintaxis | 1 |

| Nivel | Aciertos |
|---|---:|
| 1 | 10/12 |
| 2 | 7/14 |
| 3 | 4/14 |

## Predicción de evaluación oculta

Se estima una EX oculta de **0.35**, frente a 0.439 en la validación propia. Se aplica un descuento relativo del 20% por la generación con plantillas, el uso de solo dos dominios de validación y la selección del adapter sobre ese mismo conjunto. El descuento es una hipótesis conservadora, no una medición ni un intervalo de confianza.

El intervalo bootstrap jerárquico de EX propia es [0.275, 0.605]. Se remuestrean esquemas y preguntas con semilla 2026. Con dos esquemas, este intervalo no representa toda la variación esperable entre bases desconocidas.

Los errores de tablas o columnas indican problemas de correspondencia con el esquema; los de JOIN y agregación requieren revisar relaciones y nivel de agrupación. Una consulta ejecutable puede seguir teniendo filtros o resultados incorrectos. La clasificación automática es heurística; los casos particulares se registran en revision_errores.csv.

La mejora atribuible al adapter, medida sin reparación en ambas versiones, es +0.159. La reparación se evalúa como un experimento separado sobre ese adapter.

Si la EX final se repitiera en la evaluación oculta, correspondería a 18.8/30 en el componente de exactitud. El aporte del entrenamiento en la configuración final se determinará al evaluar las dos versiones con la misma estrategia de inferencia.
