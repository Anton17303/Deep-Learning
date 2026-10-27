# Experimentos

## Diseño registrado el 25 de octubre de 2026

Se utiliza Qwen2.5-Coder-0.5B-Instruct, uno de los modelos permitidos, con semilla 2026. Se conserva el mismo prompt en el baseline y en los adapters. La validación de hotel y fútbol no se utiliza para calcular gradientes ni para ajustar la pérdida de entrenamiento.

Se comparan los rangos LoRA 8 y 16 sobre la misma base cuantizada a 4 bits NF4 con doble cuantización y cómputo FP16 (QLoRA). El rango es el único hiperparámetro que cambia: se mantienen alpha 16, dropout 0.05, módulos q_proj y v_proj, tasa de aprendizaje 0.0002, 0.1 épocas y acumulación de cuatro ejemplos. El aumento de rango también cambia la escala efectiva alpha/r; esta relación forma parte del efecto del rango bajo alpha fijo.

**Hipótesis previa:** el rango 16 permite representar más relaciones entre las tablas y podría mejorar la EX en consultas con JOIN y subconsultas. El rango 8 utiliza menos parámetros y puede generalizar mejor frente a las plantillas repetidas. La comparación se realiza mediante EX ponderada; las curvas de loss describen el ajuste, pero no sustituyen la evaluación por ejecución.

Las activaciones guardadas para backward se transfieren a CPU en ambas configuraciones para reducir el consumo de VRAM. Se conservan el mismo modelo base NF4 y el mismo presupuesto de entrenamiento.

## Presupuesto de entrenamiento

Se fija un presupuesto de 76 pasos por configuración, equivalente a 0.1 épocas y 304 ejemplos procesados del corpus de 3,023 pares. Se utiliza el mismo orden aleatorio con semilla 2026 en ambas corridas. Esta cobertura limitada puede producir subajuste. La prueba inicial de un paso en CPU se conserva aparte y no se utiliza para comparar los rangos.

## Experimento de inferencia

Se compara el adapter seleccionado sin reparación y con reparación de errores de ejecución. Se mantiene el modelo, el esquema, la pregunta y la generación determinista. La reparación puede usar como máximo dos llamadas a ejecutar y conserva un presupuesto conjunto de 25 segundos. No se entrega la consulta de referencia al modelo.

La reparación contrasta primero los identificadores contra el DDL. Se corrigen nombres inexistentes solo con similitud de al menos 0.88 y una ventaja de al menos 0.10 frente al segundo candidato. Los literales y los nombres válidos se conservan. Cuando no existe una corrección única, se utiliza el mensaje de error para regenerar SQL.

**Hipótesis previa:** el mensaje de error de MySQL puede corregir columnas inexistentes y sintaxis. No garantiza corregir consultas ejecutables que responden otra pregunta. Se comparan EX, errores por categoría y tiempo por consulta.

## Criterios de selección

Se selecciona el adapter con mayor EX ponderada sobre las 40 preguntas. En empate, se prefiere el menor rango. La reparación se activa únicamente si mejora EX sin exceder el límite de tiempo. Los resultados se obtienen de los CSV de evaluación y de los registros de entrenamiento, sin asignar valores a experimentos no ejecutados.

## Ampliación de cobertura registrada el 26 de octubre de 2026

Se comparan continuaciones de los rangos 8 y 16 durante una época adicional completa: 756 pasos y 3,023 ejemplos por configuración. Se parte de los adapters de cada rango que procesaron 304 ejemplos. Se reinicia el optimizador con tasa 0.0001; el resto de condiciones se mantiene igual entre ambos rangos. Los checkpoints se guardan cada diez pasos y al finalizar.

**Hipótesis previa:** recorrer el corpus completo puede mejorar la correspondencia con los identificadores, las agregaciones y las subconsultas frente al presupuesto de 304 ejemplos. El rango 16 podría aprovechar la mayor cobertura, aunque la pérdida de entrenamiento no garantiza una mejora de EX. Se conservan los adapters iniciales y se selecciona por EX ponderada, sin reemplazar la entrega con un candidato que empeore el resultado.

La validación de hotel y fútbol continúa excluida del cálculo de gradientes. La ejecución en T4 se acredita únicamente mediante registros obtenidos en ese dispositivo.

En la ampliación se usa offload automático: las activaciones se transfieren a CPU cuando la GPU tiene menos de 6 GiB; en una T4 permanecen en GPU. Esta decisión se aplica igual a ambos rangos y se registra junto con el dispositivo utilizado.

## Resultados de la ampliación

Se completaron ambas continuaciones en Tesla T4, con 756 pasos y 3,023 ejemplos por rango. Los tiempos fueron 27.06 minutos para rango 8 y 26.99 para rango 16. La EX fue 0.415 y 0.402, respectivamente. La pérdida disminuyó, pero no se observó una mejora de generalización frente al rango 8 inicial, cuya EX fue 0.439.

Se reevaluaron el baseline y los cuatro adapters en la misma T4. Se conservó el rango 8 inicial y se activó la reparación, que elevó los aciertos de 21 a 22 y la EX de 0.439 a 0.451. El tiempo medio aumentó de 3.18 a 4.93 segundos; el máximo final fue de 25.15 segundos. Los casos y las métricas se conservan en los CSV de `resultados/`.
