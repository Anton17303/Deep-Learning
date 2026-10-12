# Resultados: Luminarios del arrecife astral

## Ejecución real

Se prepararon 1,536 dibujos originales. Se ejecutaron tres corridas controladas, tres variantes adicionales y una fase de ajuste de rasgos. Los valores de este informe se obtienen de los registros CSV y de la prueba de vecinos. Se conserva la separación entre hipótesis previa, medición posterior e inspección visual.

## Arquitectura

Se utiliza un vector gaussiano de 64 componentes y una salida RGB de 64 × 64. La base usa convoluciones transpuestas con tamaños 4, 8, 16, 32 y 64. Los canales de G son 128, 64, 32, 16 y 3; los de D son 16, 32, 64, 128 y 1. G utiliza BatchNorm y ReLU, con Tanh en la salida. D utiliza LeakyReLU, BatchNorm y logits sin sigmoide.

La base tiene 304,352 parámetros en G y 175,296 en D. Se eligió una arquitectura pequeña para permitir entrenamiento real en CPU. La variante final usa ampliación bilineal seguida de convoluciones 3 × 3, normalización espectral y ausencia de BatchNorm en D. Sus parámetros son 261,520 en G y 178,944 en D.

La variante final cambia varias condiciones y se analiza como una configuración completa. No sustituye las comparaciones controladas. La entrada final de G combina 64 componentes de ruido y 16 indicadores de color, ojos, cuerpo y antenas. D recibe tres canales RGB y 16 canales constantes de atributos. Los atributos se verifican contra las huellas de los dibujos originales. No se entrenan etiquetas de nombre o rol.

## Control experimental

Se mantienen los mismos datos, 60 épocas, lote de 64, semilla 42, ruido fijo con semilla 1234 y 16 vectores de evaluación. Adam utiliza tasas 0.0002 para ambas redes y betas (0.5, 0.999). No se aplica aumento de datos. El orden de los lotes y el ruido de entrenamiento usan secuencias independientes con semillas 1042 y 2042.

El experimento hinge cambia únicamente la pérdida. El experimento espectral cambia únicamente la normalización espectral de D. Las hipótesis se conservan en el notebook y en `experimentos.md` desde antes de la ejecución. Se verifica que los conjuntos, los vectores fijos y las condiciones comunes coinciden.

## Mediciones

| Corrida | D final | G final | Diversidad final | Diversidad últimas 3 rejillas | Desviación D últimas 20 épocas | Tiempo |
|---|---:|---:|---:|---:|---:|---:|
| base | 0.4487 | 4.1227 | 0.0142 | 0.0108 | 0.5585 | 4.6 min |
| exp_loss_hinge | 0.3516 | 3.8868 | 0.0251 | 0.0182 | 0.1100 | 5.2 min |
| exp_stab_sn | 0.1840 | 3.5407 | 0.1010 | 0.0936 | 0.1174 | 5.1 min |


La diversidad se calcula en [-1, 1]. Los valores de BCE y hinge tienen escalas distintas. La desviación de D mide oscilación y no calidad. Ninguna de estas cifras sustituye la inspección visual.

## Base

La base produjo patrones de ruido y muestras muy parecidas. La pérdida de D permaneció cerca de cero durante muchas épocas y la de G aumentó. La diversidad cayó desde 0.0387 en la época 5 hasta 0.0089 en la época 50. En las épocas 59 y 60 ocurrió un salto en la pérdida de D, pero las imágenes finales siguieron siendo deficientes. La configuración no se utilizó para la galería.

## Experimento de pérdida

Hipótesis previa: Se espera que la pérdida hinge mejorará la diversidad de los personajes porque utiliza un margen para el discriminador y una señal lineal para el generador. Se considerará útil si la diversidad RMS media de las últimas tres rejillas no cae más de 10 % frente a la base y la inspección del mismo ruido fijo muestra cuerpos y rasgos al menos igual de reconocibles, sin repetición dominante de una sola forma.

Resultado: La diversidad media de las últimas tres rejillas fue 0.0182, frente a 0.0108 de la base: una relación de 1.70. Se cumplió la condición numérica. Sin embargo, las muestras conservaron mucho ruido y una forma central repetida. La diversidad volvió a caer después de las primeras épocas. El criterio visual de la hipótesis no se cumplió de forma suficiente; hinge por sí sola no resolvió el problema.

La relación de diversidad media frente a la base fue 1.70. El criterio completo también exige rasgos reconocibles y variedad visual.

## Experimento de estabilización

Hipótesis previa: Se espera que la normalización espectral mejorará la estabilidad porque limita la amplificación de las convoluciones del discriminador. Se considerará útil si la desviación de la pérdida de D durante las últimas 20 épocas es menor que en la base, la diversidad media de las últimas tres rejillas no cae más de 10 % y la inspección visual no muestra una pérdida clara de rasgos reconocibles.

Resultado: La diversidad media final aumentó a 0.0936, una relación de 8.70 frente a la base. La desviación de D en las últimas 20 épocas fue 0.1174, frente a 0.5585 de la base. La diferencia también refleja el salto tardío de la base. Se observaron cuerpos de colores y antenas con más variedad que en las otras corridas controladas. La técnica resultó útil respecto a la base, aunque persistieron ruido y deformaciones y no se obtuvo una galería de calidad suficiente solo con ella.

La relación de diversidad media frente a la base fue 8.70. El criterio completo incluye la oscilación de D y la inspección visual.

## Variante final

| Variante adicional | Épocas | D final | G final | Diversidad final | Tiempo |
|---|---:|---:|---:|---:|---:|
| refined | 120 | 0.9479 | 0.0688 | 0.0225 | 22.7 min |
| moment_refined | 120 | 0.2660 | 1.8903 | 0.3800 | 20.7 min |
| conditional | 80 | 0.4391 | 3.3193 | 0.4202 | 12.6 min |
| conditional_refined | 40 | 0.1244 | 7.3083 | 0.3946 | 6.6 min |


La variante bilineal sin comparación de estadísticas produjo cuerpos de poco contraste sobre un fondo gris. Su diversidad final fue 0.0225. Las curvas relativamente quietas no se tradujeron en imágenes útiles. Se descartó para la galería.

La comparación de estadísticas recuperó el fondo oscuro y produjo cuerpos con colores y antenas. La diversidad final fue 0.3800. Sin embargo, la hoja de 200 candidatos mostró predominio de un ojo central y pocas familias de silueta. La diversidad en píxeles no equivalió a una variedad completa de personajes. Los 200 candidatos se conservaron y se incluyeron en la tasa total de selección.

La variante condicional de 80 épocas respondió al color y a algunos cambios de antenas y silueta. No se distinguieron de forma fiable uno, dos y tres ojos. Su diversidad final fue 0.4202. La hipótesis se cumplió solo parcialmente: las condiciones ayudaron a ordenar el estilo, pero no garantizaron todos los atributos. Se generaron otros 200 candidatos y se conservaron como evidencia.

La variante `conditional_refined` se entrenó durante 40 épocas, con pérdida hinge, tasa G 0.0001, tasa D 0.0001, generador resize y normalización de D none. Su pérdida final fue D 0.1244, G 7.3083 y su diversidad RMS final fue 0.3946. El tiempo registrado fue 6.6 minutos. El ajuste de 40 épocas mejoró el contraste alrededor del ojo y conservó cuerpos, colores y antenas reconocibles. No resolvió de forma fiable la cantidad de ojos. La condición solicitada se registra aparte de los rasgos observados. Se seleccionaron diez conceptos de personaje con diferencias visibles, pero la familia de rostros y varias siluetas siguen siendo parecidas; no se afirma diversidad anatómica completa. Se agregó una regularización propia con peso 2 para comparar las medias y desviaciones de los lotes a 8 × 8. La pérdida total de G incluye ese término; la pérdida adversarial y la penalización se registran por separado en regularization.csv. También se agregó L1 con peso 10 frente a una imagen real de la misma condición. El ruido no identifica una imagen real; el término favorece un prototipo por atributos y puede reducir la variación dentro de cada condición. Ese término también se registra por separado. Se agregó un error cuadrático con peso 15 en la región de los ojos. El modelo parte de 80 épocas condicionales y se ajusta durante 40 más, para un total de 120. La etapa cero de su rejilla corresponde a los pesos de la fase anterior; no es una inicialización aleatoria. Los optimizadores se reinician y la ventana depende del encuadre fijo del conjunto.

## Galería y tasa de selección

Se seleccionaron 10 de 600 candidatos en total. El modelo final produjo 200 candidatos, con semillas de 0 a 199. También se generaron 400 candidatos de variantes anteriores, que se descartaron para la galería. Criterio: Se priorizaron cuerpos reconocibles y una combinación de colores, siluetas y tipos de antena. Se revisaron los vecinos de entrenamiento. La selección mantiene una familia visual similar y predomina un ojo central; no se afirma una variedad anatómica completa..

La selección final corresponde a un solo checkpoint. Las rejillas de seguimiento se utilizaron para revisar el entrenamiento; la tasa declarada incluye todas las hojas de candidatos y no oculta la selección de configuraciones anteriores.

| Personaje | Nombre | Rol | Semilla | Rasgos observados |
|---|---|---|---:|---|
| 01 | Brisa | Mensajero | 0 | Cuerpo turquesa compacto, contorno redondo y antenas cortas. |
| 02 | Neris | Explorador | 61 | Cuerpo azul con base ancha y dos antenas largas. |
| 03 | Vela | Guardián | 116 | Cuerpo violeta ancho, antenas altas y borde inferior claro. |
| 04 | Faro | Guía | 51 | Cuerpo naranja, parte superior redonda y base amplia. |
| 05 | Brote | Cuidador | 82 | Cuerpo verde vertical, antenas largas y contorno ovalado. |
| 06 | Coral | Sanador | 197 | Cuerpo rosa con esquinas suaves y extremidades cortas. |
| 07 | Ascua | Centinela | 129 | Cuerpo naranja con dos antenas altas y silueta alargada. |
| 08 | Nimbo | Cartógrafo | 181 | Cuerpo azul compacto, antenas muy cortas y base casi plana. |
| 09 | Lira | Archivista | 14 | Cuerpo violeta bajo, marca clara superior y contorno redondo. |
| 10 | Musgo | Recolector | 190 | Cuerpo verde ovalado con zona superior lisa y extremidades cortas. |


Los nombres y roles se asignan como descripción del universo. La GAN no se entrenó con etiquetas de nombre o rol. Los PNG se guardan directamente desde el generador, sin redibujo ni corrección visual posterior.

## Vecinos más cercanos

Se buscó el vecino exacto en píxeles entre las 1,536 imágenes de entrenamiento para cada personaje. La distancia RMS se calcula sobre RGB en [0, 1]. Una distancia menor indica mayor parecido. La mediana real frente a otra imagen real fue 0.1374; la mediana de los personajes frente al entrenamiento fue 0.1302. La distancia mínima al entrenamiento fue 0.1134. Se encontraron 0 copias exactas. La distancia mínima entre personajes seleccionados fue 0.1270. Estos valores no demuestran novedad semántica por sí solos. El fondo, el desenfoque y los defectos afectan la distancia.

| Personaje | Vecino de entrenamiento | RMS RGB | RMS primer plano |
|---|---|---:|---:|
| 01 | 00179.png | 0.1134 | 0.2089 |
| 02 | 00627.png | 0.1434 | 0.2715 |
| 03 | 01361.png | 0.1382 | 0.2641 |
| 04 | 01345.png | 0.1390 | 0.2586 |
| 05 | 00890.png | 0.1354 | 0.2323 |
| 06 | 01033.png | 0.1207 | 0.2226 |
| 07 | 01056.png | 0.1471 | 0.2527 |
| 08 | 00312.png | 0.1302 | 0.2360 |
| 09 | 00204.png | 0.1167 | 0.2222 |
| 10 | 00725.png | 0.1155 | 0.2024 |


La mediana de las distancias generadas fue 0.1302, algo menor que la mediana real de 0.1374. La mínima generada, 0.1134, estuvo por debajo del percentil 10 de la calibración real. El modelo produce variantes próximas a los prototipos del conjunto. No se encontraron copias exactas, pero esa ausencia no demuestra por sí sola que todos los conceptos sean nuevos. La comparación visual muestra diferencias de contorno, antenas y detalles, junto con una semejanza importante de familia.

## Fallos y decisiones

La base mostró un discriminador dominante, pérdidas de G crecientes y pérdida de variedad. Hinge no resolvió el ruido. La normalización espectral ayudó, pero fue insuficiente. La variante bilineal produjo curvas suaves con imágenes deficientes. Las estadísticas recuperaron el fondo y el color, aunque conservaron un ojo dominante. Las condiciones y el ajuste facial mejoraron ciertos rasgos sin garantizar los tres conteos de ojos. Estas observaciones muestran que una pérdida baja o una condición escrita no bastan para asegurar calidad o diversidad.

## Limitaciones

Se mantiene desenfoque, extremidades poco definidas y predominio de un solo tipo de rostro. Algunas muestras pueden considerarse variantes de una misma familia, por lo que el requisito de diez personajes claramente distintos requiere una valoración visual exigente. La novedad semántica no queda demostrada solo con píxeles. El conjunto es pequeño, centrado y de reglas simples; la pérdida de reconstrucción favorece prototipos por condición y el ajuste de ojos depende de una ventana fija.

Se utiliza una sola semilla de entrenamiento por configuración. No se presentan intervalos de confianza ni se afirma que el orden observado sea universal. El conjunto completo se utiliza para entrenar; la prueba de vecinos busca copias respecto a ese conjunto y no mide generalización sobre un conjunto de prueba independiente.

## Reflexión final

Brisa, personaje 01 y semilla 0, fue el caso más difícil de defender como nuevo. Su vecino 00179 comparte el color turquesa, el ojo central y un cuerpo compacto; su RMS fue 0.1134, el menor de la galería. Cambian el contorno, la boca y las extremidades, pero la diferencia de familia es pequeña. El caso indica que la GAN aprendió prototipos visuales del universo y que el ruido no garantiza un concepto nuevo. La evidencia de novedad se considera limitada y este caso se conserva como un límite del resultado.

## Reproducción

Los pesos utilizados son `runs/conditional_refined/ckpt/G_final.pt`. El manifiesto guarda la huella del checkpoint, las semillas, los vectores completos y las huellas de los PNG. `verify_project.py` regenera las imágenes y comprueba su igualdad con los archivos entregados.

## Referencias

- Goodfellow et al. (2014), [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661).
- Radford et al. (2015), [Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks](https://arxiv.org/abs/1511.06434).
- Miyato et al. (2018), [Spectral Normalization for Generative Adversarial Networks](https://arxiv.org/abs/1802.05957).
- Zhang et al. (2018), [Self-Attention Generative Adversarial Networks](https://arxiv.org/abs/1805.08318), referencia para la pérdida hinge; no se implementa atención.
- Salimans et al. (2016), [Improved Techniques for Training GANs](https://arxiv.org/abs/1606.03498), referencia general para comparar estadísticas; la regularización del proyecto utiliza píxeles, no características aprendidas.
- Mirza y Osindero (2014), [Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784).
