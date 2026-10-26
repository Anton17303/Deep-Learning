# Bitácora

| Fecha | Autor | Actividad | Resultado |
|---|---|---|---|
| 2026-10-17 | Alejandro Antón | Se incorporó la primera parte del proyecto Text-to-SQL. | Se registraron los datos, generadores, contrato de inferencia y evaluador en `988ddfc`. |
| 2026-10-17 | Nina Nájera | Se comprobó la cantidad de pares y la separación de esquemas. | Se identificaron 3,023 pares únicos y 40 preguntas de validación sin intersección de esquemas. |
| 2026-10-18 | Nina Nájera | Se registraron las hipótesis para comparar dos rangos LoRA. | Se fijaron rangos 8 y 16 con el resto de hiperparámetros constantes en `cba09b8`. |
| 2026-10-19 | Nina Nájera | Se preparó una instancia aislada de MySQL 8.4.10. | Se habilitó la conexión local al puerto 3307. |
| 2026-10-20 | Nina Nájera | Se reconstruyeron las bases y se revalidaron los candidatos. | Se aceptaron 3,023 pares y se documentaron 79 descartes con `ONLY_FULL_GROUP_BY` activo. |
| 2026-10-21 | Nina Nájera | Se ejecutaron las consultas de referencia en los dos esquemas de validación. | Las 40 consultas se ejecutaron correctamente y el oráculo alcanzó EX 1.000. |
| 2026-10-22 | Nina Nájera | Se implementó el entrenamiento con pérdida solo sobre SQL y checkpoints. | Se ejecutó una prueba real de rango 8 con 540,672 parámetros entrenables. |
| 2026-10-22 | Nina Nájera | Se reforzó la validación de consultas y se añadieron pruebas de integridad. | Se aprobaron 16 pruebas del evaluador, extracción de SQL y contrato. |
| 2026-10-23 | Nina Nájera | Se integraron los notebooks y el flujo de comparación experimental. | Se automatizaron baseline, selección de adapter, reparación, análisis y empaquetado. |
| 2026-10-24 | Nina Nájera | Se preparó un entorno CUDA aislado y se ajustó el entrenamiento a NF4 con activaciones en CPU. | Se inició el entrenamiento QLoRA en la GPU MX350 sin modificar el controlador del equipo. |
| 2026-10-25 | Nina Nájera | Se completaron las dos configuraciones QLoRA con el mismo presupuesto. | Se procesaron 304 ejemplos en 76 pasos por configuración y se conservaron los adapters, pérdidas y tiempos. |
| 2026-10-25 | Nina Nájera | Se compararon baseline, rangos y reparación mediante ejecución. | Se seleccionó lora_r8 con EX 0.439; los resultados por pregunta y el análisis se guardaron en resultados/. |
| 2026-10-25 | Nina Nájera | Se comprobó el contrato de inferencia y se prepararon los documentos finales. | Se aprobaron 23 pruebas y los tres casos repetidos del contrato; se generó la presentación de 11 diapositivas. |
