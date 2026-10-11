#!/usr/bin/env bash
# Misma semilla, mismos datos, mismas épocas y mismo ruido de evaluación en todos.
# Cada experimento cambia UNA sola cosa respecto a "base".
set -e
DATA=${1:-data/processed}
EP=${2:-100}
python train.py --data $DATA --name base            --epochs $EP
python train.py --data $DATA --name exp_loss_hinge  --epochs $EP --loss hinge          # experimento de pérdida
python train.py --data $DATA --name exp_stab_sn     --epochs $EP --spectral            # experimento de estabilización
python analysis.py compare runs/base runs/exp_loss_hinge runs/exp_stab_sn
