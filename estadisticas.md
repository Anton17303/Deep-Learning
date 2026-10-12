# Regularización adicional por estadísticas de los lotes

## Observación previa

Las tres corridas controladas de 60 épocas terminaron. La base y hinge mantienen ruido visible. La variante espectral mejora la variedad, pero conserva defectos. Durante las primeras 30 épocas de la variante bilineal se observaron cuerpos suaves con poco contraste y una pérdida de variedad.

## Hipótesis previa

Se espera que comparar la media y la variación de los lotes mejorará el fondo, el color y la diversidad porque obliga al generador a aproximar estadísticas del conjunto real, además de responder al discriminador. Se considerará útil si el fondo oscuro se recupera, aparecen cuerpos y rasgos reconocibles y se pueden seleccionar diez muestras con diferencias visibles entre 200 candidatos.

## Método

Se reduce cada lote real y generado a 8 × 8 mediante promedio. Se calcula la diferencia absoluta media entre las medias de ambos lotes y entre sus desviaciones por canal y posición. Se agrega diez veces esa suma a la pérdida adversarial hinge de G.

`L_G = -mean(D(G(z))) + 10 × (error de medias + error de desviaciones)`

No se empareja cada muestra generada con una imagen real. Se comparan estadísticas del lote completo. La galería sigue siendo una salida del generador entrenado; no se dibujan ni corrigen personajes en la etapa de generación.

Se conservan los datos, las semillas y la configuración de la variante bilineal: 120 épocas, lote 64, canales 16, tasa G 0.0002, tasa D 0.0001, normalización espectral y ausencia de BatchNorm en D. Se utiliza un nuevo entrenamiento desde la inicialización, sin cargar pesos de las corridas anteriores.

## Alcance

Es una regularización propia sobre estadísticas de píxeles a baja resolución. La idea general de comparar estadísticas se relaciona con las técnicas de estabilización de Salimans et al. (2016), pero no reproduce su método de características aprendidas ni garantiza calidad semántica. Las medias y desviaciones pueden producir imágenes suaves y no aseguran ojos, patas o anatomía correcta.

La corrida se evalúa aparte de los tres experimentos obligatorios. La pérdida total de G incluye dos términos y no se compara directamente con el valor hinge de las otras corridas. `regularization.csv` conserva ambos términos por separado.

## Ejecución

```bash
python train.py --data data/processed --name moment_refined --epochs 120 --g_arch resize --loss hinge --spectral --d_norm none --lr_d 0.0001 --moment_weight 10 --threads 2
```

## Referencia

Salimans et al. (2016), [Improved Techniques for Training GANs](https://arxiv.org/abs/1606.03498).
