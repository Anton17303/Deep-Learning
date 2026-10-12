# Proyecto 2: Luminarios del arrecife astral

Se entrenó una GAN para generar criaturas de un universo propio a partir de un conjunto de dibujos paramétricos originales. La resolución es de 64 × 64 píxeles. El origen de los datos y las reglas del universo se describen en [dataset.md](dataset.md).

## Archivos principales

| Archivo o carpeta | Contenido |
|---|---|
| `build_dataset.py` | Construcción reproducible de los dibujos originales |
| `prepare_data.py` | Conversión, recorte, reducción y eliminación de duplicados |
| `gan/models.py` | Generador y discriminador |
| `gan/losses.py` | BCE no saturante, minimax, hinge y WGAN-GP |
| `train.py` | Entrenamiento, registros, ruido fijo y checkpoints |
| `run_experiments.py` | Base y dos experimentos controlados |
| `experimentos.md` | Hipótesis y criterios previos |
| `resultados.md` | Resultados e interpretación posterior |
| `generate_gallery.py` | Candidatos, selección y regeneración de la galería |
| `nn_test.py` | Vecinos de entrenamiento y calibración en píxeles |
| `verify_project.py` | Comprobación de experimentos y reproducción exacta |
| `presentacion.md` | Informe organizado en 12 diapositivas |
| `colab_runner.ipynb` | Ejecución en Google Colab |
| `package_project.py` | Archivo ZIP con código, datos y evidencias |

## Entorno

Se utilizó Python 3.13. Las versiones medidas se conservan en `requirements-lock.txt` y en `runs/<corrida>/environment.json`. La ejecución local se realizó en CPU con cuatro hilos en las comparaciones y dos hilos en las variantes adicionales. El código utiliza CUDA cuando está disponible. No se requiere torchvision.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

`requirements.txt` permite instalar las dependencias disponibles. `requirements-lock.txt` registra las versiones exactas del entorno empleado; la disponibilidad de esas versiones depende del sistema y del Índice de paquetes.

## Preparación desde un repositorio sin datos

```bash
python build_dataset.py --n 1536 --seed 20261011
python prepare_data.py --raw data/raw/luminarios --out data/processed --size 64
```

Los programas conservan los conjuntos existentes y rechazan sobrescribir carpetas que ya contienen imágenes. El ZIP de entrega incluye las imágenes procesadas y su reporte; en ese caso la preparación ya está completa.

## Entrenamiento controlado

```bash
python run_experiments.py --data data/processed --epochs 60
python collect_results.py
python analysis.py compare runs/base runs/exp_loss_hinge runs/exp_stab_sn
```

La configuración común utiliza lote de 64, vector latente de 64 componentes, 16 canales iniciales en ambas redes y Adam con tasa 0.0002 y betas (0.5, 0.999). La pérdida base es BCE no saturante. El experimento de pérdida cambia Únicamente a hinge. El experimento de estabilización activa Únicamente la normalización espectral en el discriminador.

Una corrida existente se reanuda desde `last.pt`; el programa rechaza cambios en las condiciones experimentales. Los estados aleatorios y de los optimizadores también se conservan. Al recuperar una interrupción se eliminan del registro las filas posteriores al Último checkpoint confirmado.

```bash
python train.py --data data/processed --name base --epochs 60 --resume
```

El archivo `last.pt` no forma parte de la entrega, por su tamaño y porque se utiliza para reanudar, no para regenerar la galería. Los pesos finales sí se incluyen.

## Variantes adicionales

La base mostró poca variedad y las corridas controladas conservaron ruido visible. Se probaron dos variantes de 120 Épocas con generador bilineal, hinge, normalización espectral y menor tasa para D. La segunda agrega una regularización que compara medias y desviaciones de lotes a 8 × 8. El motivo, las hipótesis y los comandos se conservan en `refinamiento.md` y `estadisticas.md`.

Estos entrenamientos se analizan aparte de las comparaciones obligatorias. La segunda variante agrega una penalización a la pérdida de G y registra ese término por separado. `resultados.md` identifica el checkpoint utilizado en la galería.

## Semillas y evidencia

- Datos originales: 20261011.
- Inicialización de entrenamiento: 42.
- Orden de lotes: 1042.
- Ruido de entrenamiento: 2042.
- Ruido fijo de evaluación: 1234.
- Vectores auxiliares de normalización espectral: 314159, sin modificar el estado aleatorio del experimento.
- Calibración de vecinos: 0.
- Personajes finales: semillas y vectores completos en `galeria/seleccion.json`.

Las rejillas conservan los mismos 16 vectores en todas las corridas. `fixed_noise.pt` guarda los vectores utilizados. La huella SHA-256 del conjunto permite detectar un cambio en las imágenes de entrenamiento.

## Galería y vecinos

La selección documentada se regenera desde los pesos y las semillas, sin utilizar el programa de dibujo de los datos.

```bash
python generate_gallery.py --from_selection galeria/seleccion.json
python nn_test.py --data data/processed --galeria galeria
python verify_project.py
```

La verificación compara las huellas de los PNG originales y regenerados. También comprueba las condiciones fijas, las iteraciones, las Épocas y el ruido de evaluación. La tasa de selección y el criterio se conservan en el manifiesto de la galería.

La prueba de vecinos utiliza distancia RMS en píxeles RGB. Se informa el archivo real más cercano para cada personaje, la distancia sobre el primer plano y la semejanza entre personajes de la propia galería. No se interpreta una distancia alta como una prueba absoluta de novedad.

## Entrega

```bash
python package_project.py
```

Se genera `entrega/proyecto_2_luminarios.zip` con datos procesados, código, notebook, pesos finales, galería y evidencias. Se excluyen el conjunto de transacciones de otro proyecto, archivos temporales, cachés y checkpoints de reanudación.

La presentación se conserva como Markdown en `presentacion.md`. El documento contiene el texto, las especificaciones, las figuras y la matriz necesarios para organizar el PDF solicitado por el curso.

## Referencias

- Goodfellow et al. (2014), [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661).
- Radford et al. (2015), [Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks](https://arxiv.org/abs/1511.06434).
- Miyato et al. (2018), [Spectral Normalization for Generative Adversarial Networks](https://arxiv.org/abs/1802.05957).
- Zhang et al. (2018), [Self-Attention Generative Adversarial Networks](https://arxiv.org/abs/1805.08318), referencia para hinge.
- Salimans et al. (2016), [Improved Techniques for Training GANs](https://arxiv.org/abs/1606.03498), referencia general para comparación de estadísticas.
