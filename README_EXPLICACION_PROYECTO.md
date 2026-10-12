# Explicaci?n del proyecto GAN

## Objetivo

Se busca generar personajes de un universo visual propio y comprobar si son distintos de las im?genes de entrenamiento. El universo se describe en `dataset.md`; el proceso y los resultados se presentan en `resultados.md` y `presentacion.md`.

## Datos

Se construyeron dibujos originales mediante reglas geom?tricas. Los colores, el cuerpo, los ojos, las antenas y las patas var?an entre im?genes. El programa de dibujo produce ?nicamente el conjunto de entrenamiento. La GAN produce la galer?a final.

## Modelo

El generador recibe un vector aleatorio y lo transforma en una imagen. El discriminador recibe im?genes reales y generadas e intenta distinguirlas. Ambas redes se entrenan de forma alternada: el discriminador mejora su capacidad de detectar im?genes falsas y el generador busca producir im?genes que lo confundan.

## P?rdida y estabilizaci?n

Se utiliza BCE no saturante como referencia. Se compara con hinge manteniendo las dem?s condiciones. En una tercera corrida se mantiene BCE y se aplica normalizaci?n espectral al discriminador. Las hip?tesis se registran antes del entrenamiento en `experimentos.md` y en el notebook.

## Evidencias

La rejilla de ruido fijo permite seguir la evoluci?n del mismo grupo de personajes potenciales. Las curvas muestran la relaci?n entre las dos redes. Los vecinos m?s cercanos permiten observar si una imagen generada reproduce una imagen del conjunto. La tasa de selecci?n informa cu?ntos candidatos se revisaron antes de elegir la galer?a.

## L?mites

Las p?rdidas no son calificaciones de calidad. Una distancia alta al vecino puede deberse a un defecto visual. El conjunto tiene un estilo limitado y una composici?n uniforme. La valoraci?n final tambi?n requiere revisar los personajes y explicar los fallos observados.

## Reproducci?n

`README.md` contiene los comandos. `verify_project.py` comprueba que los archivos y las condiciones experimentales coinciden y que la galer?a se regenera sin modificar los PNG.
