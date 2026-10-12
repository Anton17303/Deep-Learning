# Luminarios del arrecife astral

## Universo visual

El arrecife astral es un mundo oscuro habitado por criaturas pequeñas que producen luz. Los personajes tienen cuerpos redondos, ojos claros, antenas y patas cortas. Se usan tonos turquesa, azul, violeta, naranja, verde y rosa sobre un fondo azul oscuro. La galería se evalúa por la presencia de un cuerpo reconocible, rasgos visibles y diferencias de color y forma entre personajes.

## Origen y permiso de uso

Se construyó un conjunto original mediante `build_dataset.py`, con dibujos de figuras geométricas realizadas con Pillow. No se descargaron personajes, fotografías ni imágenes de terceros. El conjunto se creó dentro del proyecto para su uso en entrenamiento y evaluación. No se atribuye una licencia externa a estas imágenes ni se afirma una cesión de derechos de terceros.

El dibujo paramétrico se utiliza únicamente para preparar los datos de entrenamiento. La galería final se produce con el generador de la GAN y sus pesos guardados; no se obtiene del programa de dibujo.

## Composición

- 1,536 imágenes RGB distintas, de 64 × 64 píxeles.
- Semilla del conjunto: 20261011.
- Tres formas de cuerpo: ovalado, redondeado y campana.
- Uno, dos o tres ojos; dos, tres o cuatro patas.
- Antena simple, doble, cuernos o ausencia de antenas.
- Seis colores principales con pequeñas variaciones.
- Variaciones de posición, tamaño, boca y puntos luminosos.

Cada dibujo se realiza a 128 × 128 y se reduce a 64 × 64 mediante Lanczos. El manifiesto registra los rasgos y la huella de los píxeles de cada imagen. No se utilizan rostros de personas reales ni personajes comerciales.

## Preparación

`prepare_data.py` convierte las imágenes a RGB, aplica recorte cuadrado centrado, ajusta la resolución y elimina duplicados exactos después de la transformación. El archivo `data_report.json` registra entradas, imágenes conservadas y descartes.

Durante el entrenamiento se transforma cada canal desde [0, 1] a [-1, 1]. No se aplica aumento de datos en las tres corridas controladas. El fondo y el encuadre son constantes para reducir la dificultad del aprendizaje en CPU.

## Limitaciones

El conjunto representa una familia de dibujos simples, no la variedad de un universo artístico completo. Las combinaciones de rasgos se originan en reglas conocidas. Aprender esta distribución no demuestra que el modelo comprenda historias, roles o anatomía. El fondo uniforme puede dominar las distancias en píxeles; por ello también se informa una distancia sobre la unión de las regiones de primer plano.

La evaluación busca novedad respecto a este conjunto. Una distancia alta no basta para concluir que una imagen es un personaje útil: también puede indicar ruido o defectos.
