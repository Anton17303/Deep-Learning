# Reparto del trabajo y qué sigue

## Ya hecho (mitad A: datos, contrato, evaluador)
Esquemas + 3,023 pares validados · set de validación (40) · `prompt.py` · `solucion.py` ·
`config.json` · `requirements.txt` · `evaluador.py` con categorías de error · pruebas.

## Pendiente — Persona B: ENTRENAMIENTO (área propia, ~mitad de los puntos técnicos)
Orden sugerido (hoy es 23 oct; la entrega es el 25 a las 23:59):

1. **Probar `solucion.py` en Colab T4** con `usar_adapter=false`: carga < 5 min, < 30 s por pregunta,
   sin errores. Crear `config_base.json` (copia con `"usar_adapter": false`).
2. **Baseline**: `python evaluador.py --config config_base.json --salida resultados/baseline.csv`.
3. **Escribir las hipótesis ANTES de entrenar** en `experimentos.md` y hacer commit (la fecha del commit
   es la evidencia). Dos configuraciones de LoRA que difieran en **un solo factor** (por ejemplo rango
   `r`, o módulos objetivo, o tasa de aprendizaje).
4. **`notebooks/02_entrenamiento.ipynb`**: construir el texto con
   `prompt.construir_mensajes(esquema, pregunta)` + respuesta = SQL, usando
   `prompt.cargar_ejemplos()`. Calcular la pérdida solo sobre la respuesta. Usar `fp16` (la T4 no
   soporta bf16). Reportar `print_trainable_parameters()`, tiempo y curvas de loss (de
   `trainer.state.log_history`). Guardar el adapter en `adapter/`. Cada ejemplo pesa ~1,000-1,500
   tokens de esquema: medir con 50 pasos antes de decidir épocas; guardar checkpoints en Drive.
5. **Evaluar ambas configuraciones** en la validación propia y elegir la del adapter final.
6. **Experimento de inferencia** (una sola variable): `REPARAR=True`, `FORMATO_ESQUEMA="compacto"`
   (¡exige entrenar con ese formato!) o `FEWSHOT=n`, en las constantes de `solucion.py`.

## Pendiente — compartido
- **Análisis de errores**: `resultados/validacion_propia.csv` ya trae `categoria_error` (heurística);
  revisar a mano los casos dudosos y resumir por categoría y por nivel.
- **Predicción justificada de EX** y `presentacion.pdf` (máx. 12 diapositivas).
- **Colaboración real**: ambos con commits desde su cuenta, repo compartido con el docente,
  `BITACORA.md` (≥ 8 entradas con fecha y autor reales), `CONTRIBUCIONES.md`,
  `git log --all --date=iso --stat > historial_git.txt`. No se puede fabricar ni retrodatar: empiecen
  a commitear hoy.
- Coevaluación individual en Canvas.

## Pendiente — Persona A (lo que no alcanza a cubrir esta mitad)
- Repetir la validación de datos en **MySQL 8.4.10** y actualizar `reporte_datos.json`.
- Revisar y reescribir a su estilo las 40 preguntas de validación; confirmar que cada consulta de
  referencia es la única interpretación razonable.
- Mejorar la diversidad de los datos (el mayor riesgo para la nota oculta): parafrasear preguntas con un
  LLM, y/o convertir un subconjunto de Spider/BIRD a MySQL y traducirlo. Documentar descartes.
- README final: licencias y alcance del uso de IA.
