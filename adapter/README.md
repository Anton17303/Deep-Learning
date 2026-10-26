---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-0.5B-Instruct
library_name: peft
---

# Adapter Text-to-SQL

Se entrenó un adapter QLoRA de rango 8 sobre la base NF4 de 4 bits, con semilla 2026. Se procesaron 304 ejemplos del corpus de 3023 pares en 76 pasos. La pérdida se calculó únicamente sobre la respuesta SQL.

Parámetros entrenables: 540,672. Tiempo de entrenamiento: 37.11 minutos.

Los pesos del modelo base se descargan por separado. La inferencia se realiza mediante solucion.py.
