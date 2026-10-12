"""Redacta el informe a partir de mediciones y observaciones visuales registradas."""
import csv
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    experiments = load("evidencias/resumen_experimentos.json")["runs"]
    visual = load("evidencias/revision_visual.json")
    selection = load("galeria/seleccion.json")
    neighbors = load("nn_resultados/resumen.json")
    data = load("data/processed/data_report.json")
    selected_run = Path(selection["checkpoint"]).parents[1]
    selected_config = load(selected_run / "config.json")
    selected_environment = load(selected_run / "environment.json")
    with (selected_run / "metrics.csv").open(newline="", encoding="utf-8") as stream:
        refined_rows = list(csv.DictReader(stream))
    final = refined_rows[-1]
    table = "| Corrida | D final | G final | Diversidad final | Diversidad últimas 3 rejillas | Desviación D últimas 20 épocas | Tiempo |\n|---|---:|---:|---:|---:|---:|---:|\n"
    for row in experiments:
        table += (f"| {row['run']} | {row['final_loss_d']:.4f} | {row['final_loss_g']:.4f} | "
                  f"{row['final_diversity']:.4f} | {row['tail_diversity_mean']:.4f} | "
                  f"{row['tail_loss_d_std']:.4f} | {row['seconds'] / 60:.1f} min |\n")
    gallery_table = "| Personaje | Nombre | Rol | Semilla | Rasgos observados |\n|---|---|---|---:|---|\n"
    for item in selection["personajes"]:
        gallery_table += f"| {item['personaje']:02d} | {item.get('nombre', '')} | {item.get('rol', '')} | {item['seed']} | {item.get('rasgos', '')} |\n"
    neighbor_table = "| Personaje | Vecino de entrenamiento | RMS RGB | RMS primer plano |\n|---|---|---:|---:|\n"
    for index, row in enumerate(neighbors["characters"], 1):
        neighbor_table += (f"| {index:02d} | {Path(row['vecino_archivo']).name} | "
                           f"{row['rms_pixel']:.4f} | {row['rms_primer_plano']:.4f} |\n")
    hypothesis_hinge = ("Se espera que la pérdida hinge mejorará la diversidad de los personajes porque utiliza un margen para el discriminador "
                        "y una señal lineal para el generador. Lo consideraremos útil si la diversidad RMS media de las últimas tres rejillas "
                        "no cae más de 10 % frente a la base y la inspección del mismo ruido fijo muestra cuerpos y rasgos al menos igual "
                        "de reconocibles, sin repetición dominante de una sola forma.")
    hypothesis_spectral = ("Se espera que la normalización espectral mejorará la estabilidad porque limita la amplificación de las convoluciones "
                           "del discriminador. Lo consideraremos útil si la desviación de la pérdida de D durante las últimas 20 épocas es menor "
                           "que en la base, la diversidad media de las últimas tres rejillas no cae más de 10 % y la inspección visual no muestra "
                           "una pérdida clara de rasgos reconocibles.")
    architecture = f"""Se utiliza un vector gaussiano de 64 componentes y una salida RGB de 64 × 64. La base usa convoluciones transpuestas con tamaños 4, 8, 16, 32 y 64. Los canales de G son 128, 64, 32, 16 y 3; los de D son 16, 32, 64, 128 y 1. G utiliza BatchNorm y ReLU, con Tanh en la salida. D utiliza LeakyReLU, BatchNorm y logits sin sigmoide.

La base tiene 304,352 parámetros en G y 175,296 en D. Se eligió una arquitectura pequeña para permitir entrenamiento real en CPU. La variante final usa ampliación bilineal seguida de convoluciones 3 × 3, normalización espectral y ausencia de BatchNorm en D. Sus parámetros son {selected_environment['parameters_g']:,} en G y {selected_environment['parameters_d']:,} en D.

La variante final cambia varias condiciones y se analiza como una configuración completa. No sustituye las comparaciones controladas."""
    protocol = """Se mantienen los mismos datos, 60 épocas, lote de 64, semilla 42, ruido fijo con semilla 1234 y 16 vectores de evaluación. Adam utiliza tasas 0.0002 para ambas redes y betas (0.5, 0.999). No se aplica aumento de datos. El orden de los lotes y el ruido de entrenamiento usan secuencias independientes con semillas 1042 y 2042.

El experimento hinge cambia únicamente la pérdida. El experimento espectral cambia únicamente la normalización espectral de D. Las hipótesis se conservan en el notebook y en `experimentos.md` desde antes de la ejecución. Se verifica que los conjuntos, los vectores fijos y las condiciones comunes coinciden."""
    refinement = (f"La variante `{selected_run.name}` se entrenó durante {selected_config['epochs']} épocas, con pérdida {selected_config['loss']}, "
                  f"tasa G {selected_config['lr_g']}, tasa D {selected_config['lr_d']}, generador {selected_config.get('g_arch', 'dcgan')} "
                  f"y normalización de D {selected_config['d_norm']}. Su pérdida final fue D {float(final['loss_d']):.4f}, "
                  f"G {float(final['loss_g']):.4f} y su diversidad RMS final fue {float(final['diversity']):.4f}. "
                  f"El tiempo registrado fue {float(final['seconds']) / 60:.1f} minutos. {visual['final_model']}")
    if selected_config.get("moment_weight", 0):
        refinement += (f" Se agregó una regularización propia con peso {selected_config['moment_weight']:g} para comparar "
                       "las medias y desviaciones de los lotes a 8 × 8. La pérdida total de G incluye ese término; "
                       "la pérdida adversarial y la penalización se registran por separado en regularization.csv.")
    regularization_figure = (f"![Componentes de la pérdida de G]({selected_run.as_posix()}/regularizacion.png)"
                             if selected_config.get("moment_weight", 0) else "")
    nn_interpretation = (f"Se buscó el vecino exacto en píxeles entre las {neighbors['training_count']:,} imágenes de entrenamiento para cada personaje. "
                         f"La distancia RMS se calcula sobre RGB en [0, 1]. Una distancia menor indica mayor parecido. "
                         f"La mediana real frente a otra imagen real fue {neighbors['real_nn_median']:.4f}; "
                         f"la mediana de los personajes frente al entrenamiento fue {neighbors['generated_nn_median']:.4f}. "
                         f"La distancia mínima al entrenamiento fue {neighbors['generated_nn_min']:.4f}. "
                         f"Se encontraron {neighbors['exact_training_copies']} copias exactas. "
                         f"La distancia mínima entre personajes seleccionados fue {neighbors['gallery_pair_min']:.4f}. "
                         "Estos valores no demuestran novedad semántica por sí solos. El fondo, el desenfoque y los defectos afectan la distancia.")
    references = """- Goodfellow et al. (2014), [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661).
- Radford et al. (2015), [Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks](https://arxiv.org/abs/1511.06434).
- Miyato et al. (2018), [Spectral Normalization for Generative Adversarial Networks](https://arxiv.org/abs/1802.05957)."""
    results = f"""# Resultados: Luminarios del arrecife astral

## Ejecución real

Se prepararon {data['kept']:,} dibujos originales. Se ejecutaron tres corridas controladas y dos variantes adicionales. Los valores de este informe se obtienen de los registros CSV y de la prueba de vecinos. Se conserva la separación entre hipótesis previa, medición posterior e inspección visual.

## Arquitectura

{architecture}

## Control experimental

{protocol}

## Mediciones

{table}

La diversidad se calcula en [-1, 1]. Los valores de BCE y hinge tienen escalas distintas. La desviación de D mide oscilación y no calidad. Ninguna de estas cifras sustituye la inspección visual.

## Base

{visual['base']}

## Experimento de pérdida

Hipótesis previa: {hypothesis_hinge}

Resultado: {visual['hinge']}

La relación de diversidad media frente a la base fue {experiments[1]['diversity_ratio_vs_base']:.2f}. El criterio completo también exige rasgos reconocibles y variedad visual.

## Experimento de estabilización

Hipótesis previa: {hypothesis_spectral}

Resultado: {visual['spectral']}

La relación de diversidad media frente a la base fue {experiments[2]['diversity_ratio_vs_base']:.2f}. El criterio completo incluye la oscilación de D y la inspección visual.

## Variante final

{refinement}

## Galería y tasa de selección

Se seleccionaron {selection['tasa_seleccion']} candidatos de la variante final. Las semillas de los candidatos fueron de 0 a {selection['candidatos_generados'] - 1}. Criterio: {selection['criterio']}.

La selección corresponde a una hoja de candidatos de un solo checkpoint. Las rejillas de las corridas anteriores se utilizaron para seguir el entrenamiento y elegir la configuración, y no se incorporaron como imágenes finales.

{gallery_table}

Los nombres y roles se asignan como descripción del universo. La GAN no se entrenó con etiquetas de nombre o rol. Los PNG se guardan directamente desde el generador, sin redibujo ni corrección visual posterior.

## Vecinos más cercanos

{nn_interpretation}

{neighbor_table}

{visual['neighbors']}

## Fallos y decisiones

{visual['failures']}

## Limitaciones

{visual['limitations']}

Se utiliza una sola semilla de entrenamiento por configuración. No se presentan intervalos de confianza ni se afirma que el orden observado sea universal. El conjunto completo se utiliza para entrenar; la prueba de vecinos busca copias respecto a ese conjunto y no mide generalización sobre un conjunto de prueba independiente.

## Reflexión final

{visual['reflection']}

## Reproducción

Los pesos utilizados son `{selection['checkpoint']}`. El manifiesto guarda la huella del checkpoint, las semillas, los vectores completos y las huellas de los PNG. `verify_project.py` regenera las imágenes y comprueba su igualdad con los archivos entregados.

## Referencias

{references}
"""
    Path("resultados.md").write_text(results, encoding="utf-8")
    matrix = """| Evidencia | Diapositiva | Conclusión | Limitación |
|---|---:|---|---|
| Universo y datos | 1–2 | Estilo propio y origen documentado | Dibujos de reglas simples |
| Arquitectura y control | 3–4 | GAN ejecutable; condiciones comunes verificables | Una sola semilla |
| Comparación de pérdida | 5 | El cambio se evalúa con curvas y muestras | BCE y hinge tienen escalas distintas |
| Estabilización | 6 | Se analiza la técnica de forma aislada | Curvas suaves no garantizan calidad |
| Ruido fijo | 7 | Evolución de los mismos 16 vectores | Muestra limitada de latentes |
| Curvas y fallos | 8, 11 | Se detectan desbalance y pérdida de variedad | Las pérdidas no miden utilidad visual |
| Galería y selección | 9 | Diez PNG regenerables; selección declarada | Calidad limitada y selección manual |
| Vecinos y reflexión | 10–11 | Se muestran los diez vecinos reales | Píxeles no prueban novedad semántica |"""
    presentation = f"""# Presentación: Luminarios del arrecife astral

Informe organizado en 12 diapositivas. Formato propuesto: 16:9, títulos de 32 puntos y texto principal de 18 puntos o más. Las figuras conservan la proporción original. Las tablas completas y el detalle de cada vecino se conservan en `resultados.md` y `nn_resultados/vecinos.csv` como material de apoyo.

## Diapositiva 1: Universo y objetivo

**Luminarios del arrecife astral**

Proyecto 2 · Deep Learning · Universidad del Valle de Guatemala · 11 de octubre de 2026

Se busca generar diez personajes distintos mediante una GAN y evaluar si reproducen imágenes de entrenamiento. El mundo está habitado por criaturas pequeñas y luminosas, con cuerpos redondos, ojos claros, antenas y patas cortas sobre un fondo oscuro. Se esperan diferencias visibles de forma y color.

## Diapositiva 2: Datos originales y preparación

Se construyeron {data['raw_files']:,} dibujos propios mediante figuras geométricas en Pillow. No se utilizaron fotografías ni personajes de terceros. Los dibujos de entrenamiento se producen con `build_dataset.py`; la galería se produce exclusivamente con la GAN.

- RGB, 64 × 64 píxeles; dibujo inicial a 128 × 128 y reducción Lanczos.
- Seis colores, tres cuerpos, uno a tres ojos y dos a cuatro patas.
- Semilla 20261011; recorte centrado y normalización a [-1, 1].
- Se conservaron {data['kept']:,} imágenes: {data['duplicates']} duplicados, {data['too_small']} pequeñas y {data['unreadable']} ilegibles.
- Sin aumento de datos en las corridas controladas. El material se creó dentro del proyecto para entrenamiento y evaluación.

![Muestra del conjunto original](evidencias/dataset.png)

## Diapositiva 3: Arquitectura de la GAN

{architecture}

| Red base | Secuencia espacial | Función |
|---|---|---|
| G | z → 4 → 8 → 16 → 32 → 64 | Produce la imagen |
| D | 64 → 32 → 16 → 8 → 4 → 1 | Evalúa real frente a generada |

Fuente: Radford et al. (2015), https://arxiv.org/abs/1511.06434.

## Diapositiva 4: Protocolo de comparación

{protocol}

| Corrida | Único cambio frente a la base |
|---|---|
| Base | BCE no saturante |
| Pérdida | BCE → hinge |
| Estabilización | Normalización espectral en D |

La variante final de 120 épocas se analiza aparte, porque cambia arquitectura, pérdida, normalización y tasa de D.

## Diapositiva 5: Experimento de pérdida

**Hipótesis previa:** {hypothesis_hinge}

En BCE se utiliza `BCEWithLogits` para las etiquetas reales y falsas. G recibe la etiqueta real. En hinge, D utiliza márgenes alrededor de +1 y -1, y G minimiza `-mean(D(fake))`.

**Resultado:** {visual['hinge']}

Diversidad media final: base {experiments[0]['tail_diversity_mean']:.4f}; hinge {experiments[1]['tail_diversity_mean']:.4f}. Relación: {experiments[1]['diversity_ratio_vs_base']:.2f}.

![Comparación de diversidad y pérdidas](comparacion.png)

Fuente: Goodfellow et al. (2014), https://arxiv.org/abs/1406.2661.

## Diapositiva 6: Experimento de estabilización

**Hipótesis previa:** {hypothesis_spectral}

La normalización espectral controla la amplificación de las convoluciones de D. Se mantienen BCE, BatchNorm y las demás condiciones. La presencia de BatchNorm impide interpretar la técnica como una garantía global sobre toda la red.

**Resultado:** {visual['spectral']}

Desviación de D en las últimas 20 épocas: base {experiments[0]['tail_loss_d_std']:.4f}; espectral {experiments[2]['tail_loss_d_std']:.4f}. Diversidad media final: espectral {experiments[2]['tail_diversity_mean']:.4f}.

![Curvas de la corrida espectral](runs/exp_stab_sn/curvas.png)

Fuente: Miyato et al. (2018), https://arxiv.org/abs/1802.05957.

## Diapositiva 7: Evolución con ruido fijo

Se guardaron los mismos 16 vectores de evaluación, con semilla 1234, y se generaron imágenes en diferentes épocas. Las rejillas permiten seguir cambios de forma y detectar repetición.

![Evolución de la base](runs/base/evolucion.png)

![Evolución de la variante final]({selected_run.as_posix()}/evolucion.png)

{visual['base']} {visual['final_model']}

## Diapositiva 8: Curvas, desbalance y variante final

{visual['failures']}

{refinement}

![Curvas de la variante final]({selected_run.as_posix()}/curvas.png)

{regularization_figure}

La pérdida de D cercana a cero durante muchas épocas se interpreta como una señal de desbalance. La diversidad RMS también puede aumentar por ruido. Las curvas se leen junto con las imágenes; no se comparan pérdidas absolutas entre BCE y hinge.

## Diapositiva 9: Galería y tasa de selección

Se seleccionaron **{selection['tasa_seleccion']}** candidatos. Criterio: {selection['criterio']}.

![Diez personajes generados por la GAN](galeria/galeria.png)

{gallery_table}

Las semillas y los vectores completos se conservan en `galeria/seleccion.json`. Los roles se asignan después de generar las imágenes; no son etiquetas que la GAN haya aprendido.

## Diapositiva 10: Vecinos más cercanos

![Diez personajes y sus vecinos de entrenamiento](nn_resultados/vecinos_presentacion.png)

{nn_interpretation}

{visual['neighbors']}

Los archivos reales y las distancias por personaje se conservan en `nn_resultados/vecinos.csv`. La comparación de primer plano reduce la influencia del fondo, pero tampoco equivale a una evaluación semántica.

## Diapositiva 11: Conclusiones, límites y reflexión

{visual['conclusion']}

{visual['limitations']}

**Reflexión final:** {visual['reflection']}

Se utiliza una sola semilla por configuración y un conjunto de dibujos simples. No se afirma comprensión de roles, anatomía o narrativa. Una distancia alta puede deberse a desenfoque o defectos.

## Diapositiva 12: Matriz de evidencias

{matrix}

Las configuraciones, semillas, pesos, imágenes y registros se conservan para reproducir la galería y contrastar estas conclusiones.
"""
    Path("presentacion.md").write_text(presentation, encoding="utf-8")
    print("resultados.md y presentacion.md generados desde las evidencias.")


if __name__ == "__main__":
    main()
