# Licencias y procedencia

## Modelo

Se utiliza Qwen/Qwen2.5-Coder-0.5B-Instruct, distribuido bajo Apache License 2.0. El adapter contiene únicamente los pesos LoRA entrenados para este proyecto. Los pesos del modelo base se descargan por separado.

- Modelo: https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct
- Licencia: https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct/blob/main/LICENSE
- El texto completo de la licencia se conserva en `LICENCIA_MODELO.txt` y acompaña los adapters.
- Transformers: Apache-2.0.
- PEFT: Apache-2.0.
- PyTorch: BSD-3-Clause.
- MySQL Community Server: GPL-2.0, distribuido por Oracle.

## Datos

Los esquemas, registros y pares pregunta-SQL son sintéticos. Se generan mediante el código de generador/ con semilla 2026. No se incorporan datos personales reales ni subconjuntos de Spider o BIRD. La autoría de los archivos del proyecto se documenta mediante el historial de Git.
