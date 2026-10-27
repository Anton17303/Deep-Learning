---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-0.5B-Instruct
library_name: peft
---

# Adapter Text-to-SQL

Se entrenó un adapter QLoRA de rango 16 sobre la base NF4 de 4 bits, con semilla 2026. Se procesaron 3023 ejemplos del corpus de 3023 pares en 756 pasos. La pérdida se calculó únicamente sobre la respuesta SQL.

Parámetros entrenables: 1,081,344. Tiempo de entrenamiento: 26.99 minutos.

Los pesos del modelo base se descargan por separado. La inferencia se realiza mediante solucion.py.

Se continuó desde un adapter del mismo rango que procesó 304 ejemplos, con un optimizador reiniciado para recorrer una época adicional completa.
