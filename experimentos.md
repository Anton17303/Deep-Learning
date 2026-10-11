# Experimentos (escribir ANTES de entrenar)

Condiciones fijas en todos: mismos datos, `--seed 42`, `--epochs 100`, `--eval_seed 1234`.
Configuración base: DCGAN, pérdida BCE no saturante, Adam lr 2e-4 beta1 0.5, BatchNorm en D.

## Experimento de pérdida (cambia solo `--loss`)
Corrida: `python train.py --data data/processed --name exp_loss_hinge --epochs 100 --loss hinge`
> Creemos que mejorará ___ porque ___. Lo consideraremos útil si ___.

**Qué pasó:** (completar con curvas, rejilla fija, diversidad)

## Experimento de estabilización (cambia solo una cosa)
Opciones de una línea: `--spectral`, `--label_real 0.9`, `--d_dropout 0.3`, `--lr_d 1e-4`
Corrida sugerida: `python train.py --data data/processed --name exp_stab_sn --epochs 100 --spectral`
> Creemos que mejorará ___ porque ___. Lo consideraremos útil si ___.

**Qué pasó:** (completar)

## Extras opcionales (si sobra tiempo)
- `--loss bce_sat` (minimax original) para mostrar el problema del gradiente saturado.
- WGAN-GP: `--loss wgan_gp --d_norm ln --n_critic 5 --beta1 0 --beta2 0.9` (cambia varias cosas a la vez: documentarlo como variante completa, no como experimento controlado).
