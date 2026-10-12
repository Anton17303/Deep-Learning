# Explicación del proyecto GAN

## Objetivo

Se busca generar personajes de un universo visual propio y comprobar si son distintos de las imágenes de entrenamiento. El universo se describe en `dataset.md`; el proceso y los resultados se presentan en `resultados.md` y `presentacion.md`.

## Datos

Se construyeron dibujos originales mediante reglas geométricas. Los colores, el cuerpo, los ojos, las antenas y las patas varían entre imágenes. El programa de dibujo produce únicamente el conjunto de entrenamiento. La GAN produce la galería final.

## Modelo

El generador recibe un vector aleatorio y lo transforma en una imagen. El discriminador recibe imágenes reales y generadas e intenta distinguirlas. Ambas redes se entrenan de forma alternada: el discriminador mejora su capacidad de detectar imágenes falsas y el generador busca producir imágenes que lo confundan.

## Pérdida y estabilización

Se utiliza BCE no saturante como referencia. Se compara con hinge manteniendo las demás condiciones. En una tercera corrida se mantiene BCE y se aplica normalización espectral al discriminador. Las hipótesis se registran antes del entrenamiento en `experimentos.md` y en el notebook.

## Evidencias

La rejilla de ruido fijo permite seguir la evolución del mismo grupo de personajes potenciales. Las curvas muestran la relación entre las dos redes. Los vecinos más cercanos permiten observar si una imagen generada reproduce una imagen del conjunto. La tasa de selección informa cuántos candidatos se revisaron antes de elegir la galería.

## Límites

Las pérdidas no son calificaciones de calidad. Una distancia alta al vecino puede deberse a un defecto visual. El conjunto tiene un estilo limitado y una composición uniforme. La valoración final también requiere revisar los personajes y explicar los fallos observados.

## Reproducción

`README.md` contiene los comandos. `verify_project.py` comprueba que los archivos y las condiciones experimentales coinciden y que la galería se regenera sin modificar los PNG.
