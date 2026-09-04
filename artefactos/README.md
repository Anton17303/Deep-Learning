# Artefactos del modelo

`modelo_A.joblib` contiene el escalador, el modelo de Gradient Boosting y el orden de las variables agregadas.

`modelo_B_state.pt` contiene los pesos de la LSTM.

`norm_stats.pkl` contiene las estadísticas de normalización, los diccionarios de categorías y canales, el largo de la ventana y la configuración de la arquitectura de B.

`modelo_C_meta.joblib` contiene el modelo logístico que combina los puntajes de A y B.

`tabla_mecanismo.csv` y `resultados.json` contienen las métricas finales de la ejecución confirmatoria.

La definición de la clase `SeqFraudLSTM` y la preparación completa de entradas se encuentran en `proyecto1_najera_anton.ipynb`.
