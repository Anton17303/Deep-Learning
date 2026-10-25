# Proyecto 3 — Text-to-SQL con LoRA (Deep Learning 2026)

Fine-tuning con LoRA de `Qwen/Qwen2.5-Coder-1.5B-Instruct` para generar MySQL a partir de un
esquema (`SHOW CREATE TABLE`) y una pregunta en español.

## Estructura
| Ruta | Contenido |
|---|---|
| `solucion.py`, `config.json`, `requirements.txt`, `adapter/` | Contrato de la entrega (`generar_sql`) |
| `prompt.py` | Prompt y post-proceso **compartidos** por entrenamiento e inferencia |
| `evaluador.py` | EX ponderada por ejecución, categorías de error, simulación de `ejecutar` |
| `generador/` | Esquemas, plantillas de pares, construcción de bases, validación en MySQL |
| `datos/` | `entrenamiento.jsonl`, `descartes.jsonl`, `reporte_datos.json`, `esquemas/`, `validacion/` |
| `resultados/` | `validacion_propia.csv` y demás resultados (pendiente: entrenamiento) |
| `notebooks/` | `01_datos.ipynb` (hecho); `02_entrenamiento`, `03_evaluacion` (pendientes) |
| `tests/` | Pruebas del evaluador y del post-proceso |

## Datos (estado actual)
- 10 esquemas propios de entrenamiento (tienda, universidad, clínica, biblioteca, aerolínea, banco,
  restaurante, RR. HH., cine, logística), cada uno en 2 variantes de nombres: completos (`full`) y
  abreviados (`abr`: `cli`, `fec_ped`, ...) con los COMMENT en español completo.
- 3,102 candidatos generados por plantillas → **3,023 aceptados**, 79 descartados
  (75 con resultado vacío, 4 con más de 500 filas). Ninguno falló por sintaxis. Detalle en
  `datos/reporte_datos.json` y `datos/descartes.jsonl`.
- Aceptados por nivel: fácil 1,085 · media 892 · difícil 981.
- Validación propia: 2 esquemas **fuera del entrenamiento** (`hotel`, 7 tablas; `futbol`, 6 tablas con
  nombres abreviados), 40 preguntas: 12 fáciles, 14 medias, 14 difíciles. La partición es por esquema.

### Reproducir
```bash
export MYSQL_SOCKET=/tmp/my8run/mysql.sock     # o MYSQL_HOST/MYSQL_PORT/MYSQL_USER/MYSQL_PASSWORD
python -m generador.construir_bases            # crea y puebla las bases, guarda datos/esquemas/*.sql
python -m generador.validar_pares              # ejecuta candidatos, escribe entrenamiento/descartes/reporte
python -m generador.crear_validacion           # comprueba las 40 consultas de referencia
python evaluador.py --oraculo                  # debe dar EX = 1.000
python -m unittest discover -s tests
```

## Motor (importante)
Todo lo anterior se pre-validó en **MySQL 8.0.46** (misma regla `ONLY_FULL_GROUP_BY`, mismas ventanas y
CTE). El enunciado exige **8.4.10**: hay que **repetir `validar_pares` y `crear_validacion` en 8.4.10**
(`scripts/colab_mysql.sh`, sin probar) y actualizar el reporte antes de entregar.

## Limitaciones conocidas
- Los pares vienen de plantillas con ~40 patrones: el modelo puede sobreajustarse a su redacción. La
  evaluación oculta tiene lenguaje más libre. Mejora posible: parafrasear preguntas con un LLM y/o
  añadir Spider/BIRD traducidos (ver `REPARTO.md`).
- Gramática: algunas frases tienen errores de concordancia ("los mesas").
- Los datos de las bases son sintéticos y aleatorios (no hay semántica real en los valores).
- `solucion.py` **no se ha ejecutado con el modelo real** (el entorno donde se escribió no tiene GPU ni
  acceso a Hugging Face). Probarlo en Colab T4 es el primer paso pendiente.

## Uso de IA
Este material se elaboró con ayuda de Claude (Anthropic): esquemas, plantillas de generación, código
del evaluador, borrador de `solucion.py` y borrador de las 40 preguntas de validación. Las
preguntas de validación y las plantillas deben ser revisadas y ajustadas por la pareja antes de
reportarlas como propias; declarar aquí el alcance exacto de ese uso.

## Licencias
Datos: sintéticos, generados por este repositorio. Modelo base: verificar la licencia en la ficha de
Hugging Face del modelo elegido y citarla aquí.
