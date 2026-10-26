# Text-to-SQL con LoRA

Se genera una consulta MySQL a partir de un esquema y una pregunta en español. Se utiliza **Qwen/Qwen2.5-Coder-0.5B-Instruct**, con comparación entre el modelo base y adapters LoRA de rango 8 y 16.

**Integrantes:** Nina Nájera y Alejandro Antón.

## Datos

Se validaron 3,023 pares de entrenamiento en **MySQL 8.4.10**, con `ONLY_FULL_GROUP_BY` activo. Se utilizaron 10 dominios propios, cada uno con nombres completos y abreviados. De 3,102 candidatos se descartaron 79: 75 por resultados vacíos y 4 por superar 500 filas.

| Nivel | Entrenamiento | Validación |
|---|---:|---:|
| Fácil | 1,086 | 12 |
| Medio | 891 | 14 |
| Difícil | 1,046 | 14 |
| Total | 3,023 | 40 |

Hotel (7 tablas) y fútbol (6 tablas) se reservan para validación. Sus esquemas no aparecen en entrenamiento. El reporte de datos contiene la versión del motor, su configuración y el detalle de descartes.

## Ejecución

Se requiere Python 3.11 o superior. El entrenamiento requiere PyTorch con soporte CUDA; se recomienda Colab con GPU T4 y el PyTorch del entorno. El entrenamiento utiliza QLoRA con base NF4 de 4 bits y cómputo FP16. La inferencia conserva esa cuantización en GPU; en CPU utiliza el modelo en FP32.

```bash
pip install -r requirements.txt
bash scripts/colab_mysql.sh
export MYSQL_SOCKET=/tmp/my8run/mysql.sock
python ejecutar_proyecto.py --reanudar
python verificar_entrega.py
```

En el entorno local se utiliza `.venv-gpu/Scripts/python.exe`. El modelo descargado se reutiliza desde `.runtime/model` cuando está disponible.

En Windows se inicia la instancia local con `. ./scripts/iniciar_mysql.ps1`, que establece `MYSQL_PORT=3307`. Se ejecutan después los mismos comandos de Python. Las bases sintéticas usan el prefijo `p3_`; su reconstrucción reemplaza exclusivamente esas bases.

El flujo completo construye los datos, ejecuta el baseline, entrena las dos configuraciones, evalúa los adapters y compara la reparación. Se selecciona por EX ponderada; en empate se prefiere el rango 8. Los checkpoints permiten reanudar una corrida interrumpida.

La ampliación de cobertura continúa ambos rangos durante una época adicional completa y conserva los candidatos iniciales en la selección:

```bash
python ejecutar_proyecto.py --reanudar --ampliar-entrenamiento
```

`notebooks/04_entrenamiento_completo_t4.ipynb` integra la preparación del entorno, la comprobación de los datos, el entrenamiento y la evaluación en T4. Verifica el acelerador antes de ejecutar y guarda los registros obtenidos en ese dispositivo.

Para evaluar la entrega:

```bash
python evaluador.py --config config_base.json --salida resultados/baseline.csv
python evaluador.py --salida resultados/validacion_propia.csv
python analizar.py
python -m unittest discover -s tests -v
```

`solucion.py` expone `generar_sql(esquema, pregunta, ejecutar=None)`. `config.json` selecciona el modelo, el adapter y la semilla. Con `usar_adapter=false` se conserva el mismo prompt. La generación utiliza `do_sample=False`; la salida se limita a una consulta de lectura. La reparación utiliza como máximo dos llamadas a `ejecutar`.

## Experimentos y resultados

El diseño y las hipótesis se registran en [experimentos.md](experimentos.md). Cada entrenamiento guarda `resumen.json`, `loss.csv`, `loss.png`, checkpoint y adapter. La pérdida se calcula únicamente sobre la respuesta SQL; los ejemplos conservan el esquema completo, sin truncamiento silencioso.

Los resultados por pregunta, el análisis por categoría, la selección del adapter y la predicción de EX se guardan en `resultados/`. `oraculo.csv` comprueba las consultas de referencia y no representa el rendimiento del modelo. `verificacion.json` registra qué comprobaciones se cumplen.

### Resultados medidos

| Configuración | Aciertos | EX ponderada | Tiempo medio (s) |
|---|---:|---:|---:|
| Base NF4 | 15/40 | 0.280 | 15.67 |
| QLoRA rango 8 | 21/40 | 0.439 | 11.49 |
| QLoRA rango 16 | 20/40 | 0.402 | 11.83 |
| Adapter con reparación | 21/40 | 0.427 | 13.20 |
| Entrega seleccionada | 21/40 | 0.439 | 11.49 |

Se seleccionó lora_r8, con reparación desactivada. La EX oculta estimada es 0.35; corresponde a una predicción, no a una medición oficial.

La carga del modelo tardó 6.37 segundos. Los tres casos repetidos cumplieron determinismo, consulta de solo lectura, límite de llamadas y tiempo. Las 25 pruebas automatizadas se aprobaron.

## Estructura

| Ruta | Contenido |
|---|---|
| `solucion.py`, `prompt.py`, `config*.json` | Inferencia y prompt |
| `entrenar.py`, `configuraciones/` | Entrenamiento y comparación LoRA |
| `evaluador.py`, `analizar.py` | EX, errores y predicción |
| `ejecutar_proyecto.py` | Flujo completo |
| `generador/`, `datos/` | Bases sintéticas, pares y descartes |
| `notebooks/` | Datos, entrenamiento y evaluación |
| `adapter/`, `resultados/` | Pesos LoRA y evidencia experimental |
| `presentacion.pdf`, `presentacion_proyecto.pptx` | Presentación final de 11 diapositivas |
| `BITACORA.md`, `CONTRIBUCIONES.md`, `historial_git.txt` | Registro de actividades y contribuciones |

## Limitaciones

Los pares provienen de plantillas y pueden favorecer redacciones repetidas. Cada configuración procesa 304 ejemplos del corpus de 3,023 pares; esta cobertura limitada puede producir subajuste. La ejecución sin errores no garantiza que una consulta responda correctamente la pregunta. La selección entre adapters utiliza solo dos dominios de validación, por lo que la EX propia puede sobreestimar la generalización. Las mediciones corresponden a una GPU MX350 y no acreditan una ejecución en Colab T4.

## Licencias y uso de IA

El modelo base se distribuye bajo Apache-2.0. La procedencia de los datos y las licencias se describen en [LICENCIAS.md](LICENCIAS.md).

Se utilizó IA como apoyo para consultas, código y documentación. Las consultas SQL se comprobaron mediante ejecución en MySQL. No se utilizan APIs externas para generar SQL durante la inferencia.
