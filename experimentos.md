# Experimentos

## Diseño registrado el 25 de octubre de 2026

Se utiliza Qwen2.5-Coder-0.5B-Instruct, uno de los modelos permitidos, con semilla 2026. Se conserva el mismo prompt en el baseline y en los adapters. La validación de hotel y fútbol no se utiliza para calcular gradientes ni para ajustar la pérdida de entrenamiento.

Se comparan los rangos LoRA 8 y 16. El rango es el único hiperparámetro que cambia: se mantienen alpha 16, dropout 0.05, módulos q_proj y v_proj, tasa de aprendizaje 0.0002, 0.1 épocas y acumulación de cuatro ejemplos. El aumento de rango también cambia la escala efectiva alpha/r; esta relación forma parte del efecto del rango bajo alpha fijo.

**Hipótesis previa:** el rango 16 permite representar más relaciones entre las tablas y podría mejorar la EX en consultas con JOIN y subconsultas. El rango 8 utiliza menos parámetros y puede generalizar mejor frente a las plantillas repetidas. La comparación se realiza mediante EX ponderada; las curvas de loss describen el ajuste, pero no sustituyen la evaluación por ejecución.

## Presupuesto de entrenamiento

Se fija un presupuesto de 76 pasos por configuración, equivalente a 0.1 épocas y 304 ejemplos procesados del corpus de 3,023 pares. Se utiliza el mismo orden aleatorio con semilla 2026 en ambas corridas. Esta cobertura limitada puede producir subajuste. La prueba inicial de un paso en CPU se conserva aparte y no se utiliza para comparar los rangos.

## Experimento de inferencia

Se compara el adapter seleccionado sin reparación y con reparación de errores de ejecución. Se mantiene el modelo, el esquema, la pregunta y la generación determinista. La reparación puede usar como máximo dos llamadas a ejecutar y conserva un presupuesto conjunto de 25 segundos. No se entrega la consulta de referencia al modelo.

**Hipótesis previa:** el mensaje de error de MySQL puede corregir columnas inexistentes y sintaxis. No garantiza corregir consultas ejecutables que responden otra pregunta. Se comparan EX, errores por categoría y tiempo por consulta.

## Criterios de selección

Se selecciona el adapter con mayor EX ponderada sobre las 40 preguntas. En empate, se prefiere el menor rango. La reparación se activa únicamente si mejora EX sin exceder el límite de tiempo. Los resultados se obtienen de los CSV de evaluación y de los registros de entrenamiento, sin asignar valores a experimentos no ejecutados.
