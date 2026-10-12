# Experimentos controlados

## Protocolo registrado antes del entrenamiento

Se fijan 1,536 dibujos del mismo conjunto, 60 épocas, lote de 64, semilla 42, ruido de evaluación con semilla 1234 y 16 vectores fijos. El generador y el discriminador usan 16 canales iniciales. El vector latente tiene 64 componentes. Se utiliza Adam con tasa 0.0002 para ambas redes, beta1 0.5 y beta2 0.999. No se aplica aumento de datos.

Cada experimento se compara contra la base. El cambio de pérdida y la normalización espectral no se combinan. El orden de los lotes y el ruido de entrenamiento tienen generadores aleatorios independientes, por lo que la variante espectral no cambia esas secuencias. También se conserva la misma inicialización de los pesos originales antes de aplicar normalización espectral.

## Base: BCE no saturante

Se utiliza BCE sobre logits. El discriminador distingue imágenes reales y generadas. El generador intenta que las imágenes falsas reciban la etiqueta real. Se conserva esta configuración como referencia, sin afirmar que una pérdida baja demuestre buena calidad.

## Experimento de pérdida: hinge

**Hipótesis previa:** Se espera que la pérdida hinge mejorará la diversidad de los personajes porque utiliza un margen para el discriminador y una señal lineal para el generador. Se considerará útil si la diversidad RMS media de las últimas tres rejillas no cae más de 10 % frente a la base y la inspección del mismo ruido fijo muestra cuerpos y rasgos al menos igual de reconocibles, sin repetición dominante de una sola forma.

Único cambio: `--loss hinge`. El discriminador minimiza `mean(relu(1-D(real))) + mean(relu(1+D(fake)))`. El generador minimiza `-mean(D(fake))`. Las pérdidas hinge y BCE tienen escalas distintas; no se comparan sus valores absolutos como una medida de calidad.

## Experimento de estabilización: normalización espectral

**Hipótesis previa:** Se espera que la normalización espectral mejorará la estabilidad porque limita la amplificación de las convoluciones del discriminador. Se considerará útil si la desviación de la pérdida de D durante las últimas 20 épocas es menor que en la base, la diversidad media de las últimas tres rejillas no cae más de 10 % y la inspección visual no muestra una pérdida clara de rasgos reconocibles.

Único cambio: `--spectral`. Se conservan BCE, BatchNorm y el resto de la configuración. La técnica controla los pesos de las convoluciones, pero no impone una cota global a toda la red con BatchNorm.

## Medición e interpretación

La diversidad RMS se calcula entre las 16 imágenes de ruido fijo. Es una señal de diferencias en píxeles, no una medida directa de variedad de personajes. Puede subir por ruido o defectos. Por eso se evalúa junto con las rejillas y la galería.

La desviación de la pérdida se usa como un indicador limitado de oscilación. Una curva suave también puede corresponder a un modelo que aprende poco. Las decisiones finales requieren revisar las figuras.

Los resultados se registran en `resultados.md` una vez finalizadas las corridas. La hipótesis queda separada de las observaciones posteriores.

## Fuentes

- Goodfellow et al. (2014), [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661).
- Radford et al. (2015), [Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks](https://arxiv.org/abs/1511.06434).
- Miyato et al. (2018), [Spectral Normalization for Generative Adversarial Networks](https://arxiv.org/abs/1802.05957).
