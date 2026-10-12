# Variante condicional para aumentar la variedad de rasgos

## Motivo

Se generaron 200 candidatos del modelo con estadísticas. Se observaron diferencias de color y antenas, pero predominó un ojo central y una familia limitada de cuerpos. Ese resultado no permite defender la variedad únicamente por cambios de color.

## Hipótesis previa

Se espera que una GAN condicional mejore la variedad de personajes porque recibe atributos explícitos de color, cuerpo, ojos y antenas, y el discriminador evalúa la coherencia entre los atributos y la imagen. Se considerará útil si la hoja de 200 candidatos contiene cuerpos con uno, dos y tres ojos, varias siluetas y diferencias de antenas, y se pueden seleccionar diez muestras sin depender únicamente del color.

## Condiciones y arquitectura

Se utilizan los atributos del manifiesto original: seis colores, tres cantidades de ojos, tres cuerpos y cuatro tipos de antena. Cada grupo se codifica con un vector de indicadores. La condición contiene 16 componentes y se combina con 64 componentes gaussianos: la entrada de G tiene 80 componentes.

D recibe RGB y 16 canales constantes que representan los mismos atributos. Se conservan el generador bilineal, 16 canales iniciales, hinge, normalización espectral y ausencia de BatchNorm en D. La variante utiliza 80 épocas, lote 64, tasas 0.0002 para G y 0.0001 para D, semilla 42 y ruido fijo con semilla 1234.

## Pérdida auxiliar

Se agrega un término L1 con peso 10 entre la muestra generada y una imagen real con la misma condición. El ruido cambia en cada actualización y no representa el identificador de una imagen. Por eso este término favorece un prototipo por condición y no una correspondencia fija entre semilla e imagen real. Se mantiene también la regularización de estadísticas con peso 2.

`L_G = -mean(D(G(z, y), y)) + 10 × L1(G(z, y), real) + 2 × error de estadísticas`

El objetivo auxiliar puede reducir la variedad dentro de cada condición y producir imágenes suaves. Esa limitación se evalúa con candidatos y vecinos. La presencia de condiciones no garantiza que todos los atributos se cumplan.

Esta corrida modifica varias condiciones y se analiza como una variante completa. No reemplaza los experimentos controlados de pérdida y estabilización. Los 200 candidatos anteriores se conservan y se incluyen en la cantidad total de muestras generadas para la selección.

## Ejecución

```bash
python train.py --data data/processed --name conditional --epochs 80 --g_arch resize --loss hinge --spectral --d_norm none --lr_d 0.0001 --moment_weight 2 --conditional --reconstruction_weight 10 --threads 4
```

Las semillas de generación determinan tanto el ruido como los atributos. `galeria/seleccion.json` conserva el vector completo y los atributos de cada personaje. La etapa de generación utiliza únicamente G y sus pesos, sin dibujar ni corregir imágenes.

## Referencia

Mirza y Osindero (2014), [Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784). La pérdida L1 y la regularización de estadísticas son elecciones adicionales del proyecto; no se presentan como una reproducción exacta de ese artículo.
