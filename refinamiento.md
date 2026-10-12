# Variante adicional de calidad

## Motivo

La base DCGAN de 60 épocas produjo textura con mucho ruido y poca variedad. El discriminador mantuvo una pérdida muy baja durante una gran parte del entrenamiento. La variante hinge comenzó a mostrar cuerpos, pero la diversidad cayó entre las épocas 10 y 30. Estas observaciones justifican probar una variante completa para la galería, además de los experimentos controlados.

## Hipótesis registrada antes de ejecutar la variante

Creemos que un generador con ampliación bilineal seguida de convoluciones, junto con un discriminador espectral sin BatchNorm y una tasa menor para D, mejorará la calidad porque reduce los patrones de tablero y limita la ventaja del discriminador. Lo consideraremos útil si, entre 200 candidatos, se pueden seleccionar al menos 10 cuerpos reconocibles con diferencias visibles de forma o color, y las rejillas de ruido fijo muestran variedad sostenida.

## Configuración

Se conservan las 1,536 imágenes, el vector latente de 64 componentes, los canales iniciales de 16 y las semillas. Se realizan 120 épocas con hinge, normalización espectral, ausencia de BatchNorm en D y tasas 0.0002 para G y 0.0001 para D. El generador conserva BatchNorm y Tanh, pero sustituye las cuatro ampliaciones de convolución transpuesta por ampliación bilineal y convolución de 3 × 3.

Esta corrida cambia varias condiciones. Se considera una variante completa de calidad, no un experimento que permita atribuir el efecto a una sola técnica. Los requisitos de comparación de pérdida y estabilización se evalúan únicamente con las tres corridas controladas de 60 épocas.

## Comando

```bash
python train.py --data data/processed --name refined --epochs 120 --g_arch resize --loss hinge --spectral --d_norm none --lr_d 0.0001
```

El resultado posterior y la decisión sobre su uso en la galería se registran en `resultados.md`.
