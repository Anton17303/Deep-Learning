# Ajuste de los rasgos del rostro

## Observación previa

La variante condicional mejoró el color y la silueta durante las primeras 70 épocas, pero mantuvo un ojo dominante en muchas muestras. Los indicadores de cantidad de ojos no bastaron para obtener los tres casos de forma clara.

## Hipótesis previa

Se espera que dar mayor peso al error en la zona de los ojos mejore la variedad de rostros porque esa región ocupa pocos píxeles y tiene poca influencia en la pérdida global. Se considerará útil si las condiciones de uno, dos y tres ojos producen diferencias visibles de rostro y se conserva el fondo, el color y la silueta.

## Método

Se utilizan los pesos de G y D de la variante condicional de 80 épocas. Se inicia una fase adicional de 40 épocas con optimizadores nuevos y tasas 0.0001 en ambas redes. Se conserva el ruido, las condiciones, hinge, L1 con peso 10 y estadísticas con peso 2.

Se añade un error cuadrático medio con peso 15 en las filas 22 a 35 y columnas 20 a 43 de la imagen de 64 × 64. Esa ventana contiene la región de los ojos del conjunto centrado. La referencia es una imagen real con los mismos atributos; el ruido no identifica una imagen de entrenamiento.

El modelo final conserva la misma arquitectura. La fase completa comprende 80 épocas iniciales y 40 de ajuste. El archivo `GD_final.pt` guarda los pesos que inician el ajuste y su huella se registra en la configuración. La etapa cero de la rejilla corresponde al modelo ya entrenado durante 80 épocas, no a una inicialización aleatoria.

## Limitaciones

El método depende del encuadre fijo del conjunto. No se presenta como una técnica general de reconocimiento de ojos. Puede suavizar detalles y reducir la variedad dentro de una condición. Se comprueba el parecido con imágenes reales mediante vecinos y se analizan los rasgos que todavía no se cumplan.

La comparación se considera una fase de ajuste posterior a una observación. No se usa para reemplazar los dos experimentos controlados obligatorios.

## Ejecución

```bash
python refine_attributes.py
```
