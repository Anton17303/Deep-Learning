# Proyecto 2: Luminarios del arrecife astral

Se entren? una GAN para generar criaturas de un universo propio a partir de un conjunto de dibujos param?tricos originales. La resoluci?n es de 64 ? 64 p?xeles. El origen de los datos y las reglas del universo se describen en [dataset.md](dataset.md).

## Archivos principales

| Archivo o carpeta | Contenido |
|---|---|
| `build_dataset.py` | Construcci?n reproducible de los dibujos originales |
| `prepare_data.py` | Conversi?n, recorte, reducci?n y eliminaci?n de duplicados |
| `gan/models.py` | Generador y discriminador |
| `gan/losses.py` | BCE no saturante, minimax, hinge y WGAN-GP |
| `train.py` | Entrenamiento, registros, ruido fijo y checkpoints |
| `run_experiments.py` | Base y dos experimentos controlados |
| `experimentos.md` | Hip?tesis y criterios previos |
| `resultados.md` | Resultados e interpretaci?n posterior |
| `generate_gallery.py` | Candidatos, selecci?n y regeneraci?n de la galer?a |
| `nn_test.py` | Vecinos de entrenamiento y calibraci?n en p?xeles |
| `verify_project.py` | Comprobaci?n de experimentos y reproducci?n exacta |
| `presentacion.md` | Informe organizado en 12 diapositivas |
| `colab_runner.ipynb` | Ejecuci?n en Google Colab |
| `package_project.py` | Archivo ZIP con c?digo, datos y evidencias |

## Entorno

Se utiliz? Python 3.13. Las versiones medidas se conservan en `requirements-lock.txt` y en `runs/<corrida>/environment.json`. La ejecuci?n local se realiz? en CPU con cuatro hilos. El c?digo utiliza CUDA cuando est? disponible. No se requiere torchvision.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

`requirements.txt` permite instalar las dependencias disponibles. `requirements-lock.txt` registra las versiones exactas del entorno empleado; la disponibilidad de esas versiones depende del sistema y del ?ndice de paquetes.

## Preparaci?n desde un repositorio sin datos

```bash
python build_dataset.py --n 1536 --seed 20261011
python prepare_data.py --raw data/raw/luminarios --out data/processed --size 64
```

Los programas conservan los conjuntos existentes y rechazan sobrescribir carpetas que ya contienen im?genes. El ZIP de entrega incluye las im?genes procesadas y su reporte; en ese caso la preparaci?n ya est? completa.

## Entrenamiento controlado

```bash
python run_experiments.py --data data/processed --epochs 60
python collect_results.py
python analysis.py compare runs/base runs/exp_loss_hinge runs/exp_stab_sn
```

La configuraci?n com?n utiliza lote de 64, vector latente de 64 componentes, 16 canales iniciales en ambas redes y Adam con tasa 0.0002 y betas (0.5, 0.999). La p?rdida base es BCE no saturante. El experimento de p?rdida cambia ?nicamente a hinge. El experimento de estabilizaci?n activa ?nicamente la normalizaci?n espectral en el discriminador.

Una corrida existente se reanuda desde `last.pt`; el programa rechaza cambios en las condiciones experimentales. Los estados aleatorios y de los optimizadores tambi?n se conservan. Al recuperar una interrupci?n se eliminan del registro las filas posteriores al ?ltimo checkpoint confirmado.

```bash
python train.py --data data/processed --name base --epochs 60 --resume
```

El archivo `last.pt` no forma parte de la entrega, por su tama?o y porque se utiliza para reanudar, no para regenerar la galer?a. Los pesos finales s? se incluyen.

## Semillas y evidencia

- Datos originales: 20261011.
- Inicializaci?n de entrenamiento: 42.
- Orden de lotes: 1042.
- Ruido de entrenamiento: 2042.
- Ruido fijo de evaluaci?n: 1234.
- Vectores auxiliares de normalizaci?n espectral: 314159, sin modificar el estado aleatorio del experimento.
- Calibraci?n de vecinos: 0.
- Personajes finales: semillas y vectores completos en `galeria/seleccion.json`.

Las rejillas conservan los mismos 16 vectores en todas las corridas. `fixed_noise.pt` guarda los vectores utilizados. La huella SHA-256 del conjunto permite detectar un cambio en las im?genes de entrenamiento.

## Galer?a y vecinos

La selecci?n documentada se regenera desde los pesos y las semillas, sin utilizar el programa de dibujo de los datos.

```bash
python generate_gallery.py --from_selection galeria/seleccion.json
python nn_test.py --data data/processed --galeria galeria
python verify_project.py
```

La verificaci?n compara las huellas de los PNG originales y regenerados. Tambi?n comprueba las condiciones fijas, las iteraciones, las ?pocas y el ruido de evaluaci?n. La tasa de selecci?n y el criterio se conservan en el manifiesto de la galer?a.

La prueba de vecinos utiliza distancia RMS en p?xeles RGB. Se informa el archivo real m?s cercano para cada personaje, la distancia sobre el primer plano y la semejanza entre personajes de la propia galer?a. No se interpreta una distancia alta como una prueba absoluta de novedad.

## Entrega

```bash
python package_project.py
```

Se genera `entrega/proyecto_2_luminarios.zip` con datos procesados, c?digo, notebook, pesos finales, galer?a y evidencias. Se excluyen el conjunto de transacciones de otro proyecto, archivos temporales, cach?s y checkpoints de reanudaci?n.

La presentaci?n se conserva como Markdown en `presentacion.md`. El documento contiene el texto, las especificaciones, las figuras y la matriz necesarios para organizar el PDF solicitado por el curso.

## Referencias

- Goodfellow et al. (2014), [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661).
- Radford et al. (2015), [Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks](https://arxiv.org/abs/1511.06434).
- Miyato et al. (2018), [Spectral Normalization for Generative Adversarial Networks](https://arxiv.org/abs/1802.05957).
