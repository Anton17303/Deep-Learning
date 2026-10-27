# Resultados de Text-to-SQL

La exactitud se calcula mediante ejecución en MySQL 8.4.10. Los niveles fácil, medio y difícil tienen pesos 1, 2 y 3. El oráculo utiliza las respuestas de referencia y solo comprueba el evaluador.

| Evaluación | Aciertos | EX ponderada | Tiempo medio (s) | Tiempo máximo (s) |
|---|---:|---:|---:|---:|
| baseline | 15/40 | 0.280 | 3.37 | 20.20 |
| lora_r8 | 21/40 | 0.439 | 3.18 | 25.07 |
| lora_r16 | 20/40 | 0.402 | 2.66 | 6.50 |
| lora_r8_completo | 20/40 | 0.415 | 3.15 | 7.36 |
| lora_r16_completo | 20/40 | 0.402 | 3.17 | 10.79 |
| reparacion | 22/40 | 0.451 | 4.93 | 25.15 |
| validacion_propia | 22/40 | 0.451 | 4.93 | 25.15 |

## Entrenamiento

| Configuración | GPU | Parámetros entrenables | Pasos | Ejemplos procesados | Tiempo (min) |
|---|---|---:|---:|---:|---:|
| lora_r8 | CUDA (registro inicial) | 540,672 | 76/76 | 304/3023 | 37.11 |
| lora_r16 | CUDA (registro inicial) | 1,081,344 | 76/76 | 304/3023 | 41.04 |
| lora_r8_completo | Tesla T4 | 540,672 | 756/756 | 3023/3023 | 27.06 |
| lora_r16_completo | Tesla T4 | 1,081,344 | 756/756 | 3023/3023 | 26.99 |

Cada comparación entre rangos comparte base NF4, semilla, orden de ejemplos, tasa de aprendizaje y presupuesto. Los entrenamientos iniciales procesaron 304 ejemplos. Las continuaciones parten del adapter del rango correspondiente y recorren una época adicional del corpus completo.

Las curvas se conservan en loss.png dentro del directorio de cada configuración, junto con sus CSV por paso. La validación final, la comparación de reparación y el contrato de inferencia se ejecutaron en Tesla T4.

En lora_r8, la pérdida media de los primeros diez pasos fue 0.520 y la de los últimos diez fue 0.266.

En lora_r16, la pérdida media de los primeros diez pasos fue 0.520 y la de los últimos diez fue 0.268.

En lora_r8_completo, la pérdida media de los primeros diez pasos fue 0.171 y la de los últimos diez fue 0.033.

En lora_r16_completo, la pérdida media de los primeros diez pasos fue 0.172 y la de los últimos diez fue 0.032.

Estos promedios describen el ajuste sobre ejemplos de entrenamiento distintos. Una pérdida menor no garantiza una EX mayor en esquemas nuevos; la selección se apoya en la evaluación por ejecución.

Con el presupuesto inicial, el rango 16 obtuvo una diferencia de EX de -0.037 frente al rango 8. No se observó una mejora de EX al aumentar el rango bajo este presupuesto. La comparación se limita a 40 preguntas y dos esquemas; no demuestra una ventaja general sobre bases desconocidas.

Con la época adicional, el rango 16 obtuvo una diferencia de EX de -0.012 frente al rango 8. No se observó una mejora de EX al aumentar el rango bajo este presupuesto. La comparación se limita a 40 preguntas y dos esquemas; no demuestra una ventaja general sobre bases desconocidas.

## Efecto de la reparación

La reparación corrigió 1 error y perdió 0 aciertos. La diferencia de EX fue +0.012; el tiempo medio pasó de 3.18 a 4.93 segundos.

La corrección de nombres puede resolver identificadores cercanos. La regeneración tiene un presupuesto limitado y puede terminar con una consulta incompleta. Los filtros o las agregaciones incorrectos que sí se ejecutan no producen un error de MySQL para activar otra generación.

## Errores: baseline

| Categoría | Cantidad |
|---|---:|
| JOIN | 1 |
| agregación | 6 |
| columna o tabla inexistente | 14 |
| filtro | 2 |
| resultado distinto | 1 |
| sintaxis | 1 |

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
| columna o tabla inexistente | 9 |
| filtro | 3 |

| Nivel | Aciertos |
|---|---:|
| 1 | 10/12 |
| 2 | 7/14 |
| 3 | 4/14 |

## Errores: lora_r16

| Categoría | Cantidad |
|---|---:|
| JOIN | 2 |
| agregación | 4 |
| columna o tabla inexistente | 9 |
| filtro | 4 |
| resultado distinto | 1 |

| Nivel | Aciertos |
|---|---:|
| 1 | 10/12 |
| 2 | 7/14 |
| 3 | 3/14 |

## Errores: lora_r8_completo

| Categoría | Cantidad |
|---|---:|
| JOIN | 3 |
| agregación | 1 |
| columna o tabla inexistente | 12 |
| filtro | 2 |
| resultado distinto | 1 |
| sintaxis | 1 |

| Nivel | Aciertos |
|---|---:|
| 1 | 10/12 |
| 2 | 6/14 |
| 3 | 4/14 |

## Errores: lora_r16_completo

| Categoría | Cantidad |
|---|---:|
| JOIN | 1 |
| agregación | 2 |
| columna o tabla inexistente | 10 |
| filtro | 4 |
| resultado distinto | 1 |
| sintaxis | 2 |

| Nivel | Aciertos |
|---|---:|
| 1 | 10/12 |
| 2 | 7/14 |
| 3 | 3/14 |

## Errores: reparacion

| Categoría | Cantidad |
|---|---:|
| JOIN | 1 |
| agregación | 5 |
| columna o tabla inexistente | 9 |
| filtro | 3 |

| Nivel | Aciertos |
|---|---:|
| 1 | 11/12 |
| 2 | 7/14 |
| 3 | 4/14 |

## Errores: validacion_propia

| Categoría | Cantidad |
|---|---:|
| JOIN | 1 |
| agregación | 5 |
| columna o tabla inexistente | 9 |
| filtro | 3 |

| Nivel | Aciertos |
|---|---:|
| 1 | 11/12 |
| 2 | 7/14 |
| 3 | 4/14 |

## Predicción de evaluación oculta

Se estima una EX oculta de **0.36**, frente a 0.451 en la validación propia. Se aplica un descuento relativo del 20% por la generación con plantillas, el uso de solo dos dominios de validación y la selección del adapter sobre ese mismo conjunto. El descuento es una hipótesis conservadora, no una medición ni un intervalo de confianza.

El intervalo bootstrap jerárquico de EX propia es [0.286, 0.627]. Se remuestrean esquemas y preguntas con semilla 2026. Con dos esquemas, este intervalo no representa toda la variación esperable entre bases desconocidas.

Los errores de tablas o columnas indican problemas de correspondencia con el esquema; los de JOIN y agregación requieren revisar relaciones y nivel de agrupación. Una consulta ejecutable puede seguir teniendo filtros o resultados incorrectos. La clasificación automática es heurística; los casos particulares se registran en revision_errores.csv.

La mejora atribuible al adapter, medida sin reparación en ambas versiones, es +0.159. La reparación se evalúa como un experimento separado sobre ese adapter.

Si la EX final se repitiera en la evaluación oculta, correspondería a 19.3/30 en el componente de exactitud. El aporte del entrenamiento en la configuración final se determinará al evaluar las dos versiones con la misma estrategia de inferencia.
