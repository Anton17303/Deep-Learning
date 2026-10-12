#!/usr/bin/env bash
# Misma semilla, mismos datos, mismas épocas y mismo ruido de evaluación en todos.
# Cada experimento cambia UNA sola cosa respecto a "base".
set -e
DATA=${1:-data/processed}
EP=${2:-60}
python run_experiments.py --data "$DATA" --epochs "$EP"
