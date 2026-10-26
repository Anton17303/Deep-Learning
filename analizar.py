"""Resumen de evaluaciones por ejecución y predicción de generalización."""
import argparse
import collections
import csv
import json
import hashlib
from pathlib import Path

import numpy as np


def cargar_csv(ruta):
    with Path(ruta).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def resumir(filas):
    pesos = np.array([int(r['peso']) for r in filas])
    aciertos = np.array([int(r['acierto']) for r in filas])
    tiempos = np.array([float(r['tiempo_s']) for r in filas])
    return dict(preguntas=len(filas), aciertos=int(aciertos.sum()),
                ex=float((pesos * aciertos).sum() / pesos.sum()),
                tiempo_medio_s=float(tiempos.mean()), tiempo_maximo_s=float(tiempos.max()),
                tiempo_mediano_s=float(np.median(tiempos)),
                exceden_30s=int((tiempos > 30).sum()),
                errores=dict(collections.Counter(r.get('categoria_revisada', r['categoria_error']) for r in filas if r['acierto'] == '0')),
                por_nivel={str(n): dict(preguntas=sum(int(r['nivel']) == n for r in filas),
                                       aciertos=sum(int(r['acierto']) for r in filas if int(r['nivel']) == n))
                           for n in [1, 2, 3]})


def bootstrap(filas):
    rng = np.random.default_rng(2026)
    bloques = [[r for r in filas if r['esquema_id'] == e] for e in sorted({r['esquema_id'] for r in filas})]
    valores = []
    for _ in range(2000):
        muestra = []
        for i in rng.integers(0, len(bloques), len(bloques)):
            bloque = bloques[i]
            muestra.extend(bloque[j] for j in rng.integers(0, len(bloque), len(bloque)))
        valores.append(sum(int(r['peso']) * int(r['acierto']) for r in muestra) /
                       sum(int(r['peso']) for r in muestra))
    return [float(v) for v in np.quantile(valores, [.025, .975])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directorio', default='resultados')
    args = parser.parse_args()
    raiz = Path(args.directorio)
    nombres = ['baseline', 'lora_r8', 'lora_r16', 'reparacion', 'validacion_propia']
    revisiones = cargar_csv(raiz / 'revision_errores.csv') if (raiz / 'revision_errores.csv').exists() else []
    resumen = {}
    lineas = ['# Resultados de Text-to-SQL', '',
              'La exactitud se calcula mediante ejecución en MySQL 8.4.10. Los niveles fácil, medio y difícil tienen pesos 1, 2 y 3. El oráculo utiliza las respuestas de referencia y solo comprueba el evaluador.', '',
              '| Evaluación | Aciertos | EX ponderada | Tiempo medio (s) | Tiempo máximo (s) |',
              '|---|---:|---:|---:|---:|']
    for nombre in nombres:
        ruta = raiz / f'{nombre}.csv'
        if ruta.exists():
            filas = cargar_csv(ruta)
            if len(filas) != 40:
                continue
            for fila in filas:
                sha = hashlib.sha256(fila['sql_pred'].encode()).hexdigest()
                revision = next((r for r in revisiones if r['evaluacion'] == nombre and r['id'] == fila['id']
                                 and r['sha256_sql'] == sha), None)
                if revision:
                    fila['categoria_revisada'] = revision['categoria_revisada']
            s = resumir(filas)
            resumen[nombre] = s
            lineas.append(f"| {nombre} | {s['aciertos']}/40 | {s['ex']:.3f} | {s['tiempo_medio_s']:.2f} | {s['tiempo_maximo_s']:.2f} |")
    entrenamientos = []
    for nombre in ['lora_r8', 'lora_r16']:
        ruta = raiz / nombre / 'resumen.json'
        if ruta.exists():
            entrenamientos.append(json.loads(ruta.read_text(encoding='utf-8')))
    if entrenamientos:
        lineas.extend(['', '## Entrenamiento', '',
                       '| Rango | Parámetros entrenables | Pasos | Ejemplos procesados | Tiempo (min) |',
                       '|---|---:|---:|---:|---:|'])
        for e in entrenamientos:
            lineas.append(f"| {e['config']['r']} | {e['parametros_entrenables']:,} | {e['pasos_realizados']}/{e['pasos_previstos']} | {e['ejemplos_procesados']}/{e['ejemplos_dataset']} | {e['segundos_entrenamiento']/60:.2f} |")
        lineas.extend(['', 'Se utiliza la misma base NF4, semilla, orden de ejemplos, tasa de aprendizaje y presupuesto. El rango es el único factor de comparación. La cobertura de 304 ejemplos no equivale a recorrer el corpus completo.', '',
                       'Las curvas se conservan en lora_r8/loss.png y lora_r16/loss.png, junto con sus CSV por paso.'])
        for e in entrenamientos:
            perdidas = cargar_csv(raiz / e['config']['nombre'] / 'loss.csv')
            if len(perdidas) >= 20:
                inicial = np.mean([float(p['loss']) for p in perdidas[:10]])
                final = np.mean([float(p['loss']) for p in perdidas[-10:]])
                lineas.extend(['', f"En rango {e['config']['r']}, la pérdida media de los primeros diez pasos fue {inicial:.3f} y la de los últimos diez fue {final:.3f}."])
        lineas.extend(['', 'Estos promedios describen el ajuste sobre ejemplos de entrenamiento distintos. Una pérdida menor no garantiza una EX mayor en esquemas nuevos; la selección se apoya en la evaluación por ejecución.'])
    if 'lora_r8' in resumen and 'lora_r16' in resumen:
        diferencia = resumen['lora_r16']['ex'] - resumen['lora_r8']['ex']
        lineas.extend(['', f"El rango 16 obtuvo una diferencia de EX de {diferencia:+.3f} frente al rango 8. " +
                       ('La hipótesis de mayor EX con rango 16 recibió apoyo en esta validación.' if diferencia > 0 else
                        'No se observó una mejora de EX al aumentar el rango bajo este presupuesto.') +
                       ' La comparación se limita a 40 preguntas y dos esquemas; no demuestra una ventaja general sobre bases desconocidas.'])
    seleccion_ruta = raiz / 'seleccion.json'
    if 'reparacion' in resumen and seleccion_ruta.exists():
        seleccion = json.loads(seleccion_ruta.read_text(encoding='utf-8'))
        originales = {f['id']: f for f in cargar_csv(raiz / f"{seleccion['adapter']}.csv")}
        reparadas = cargar_csv(raiz / 'reparacion.csv')
        mejoras = sum(f['acierto'] == '1' and originales[f['id']]['acierto'] == '0' for f in reparadas)
        perdidas = sum(f['acierto'] == '0' and originales[f['id']]['acierto'] == '1' for f in reparadas)
        original, reparada = resumen[seleccion['adapter']], resumen['reparacion']
        lineas.extend(['', '## Efecto de la reparación', '',
                       f"La reparación convirtió {mejoras} errores en aciertos y perdió {perdidas} aciertos. La diferencia de EX fue {reparada['ex'] - original['ex']:+.3f}; el tiempo medio pasó de {original['tiempo_medio_s']:.2f} a {reparada['tiempo_medio_s']:.2f} segundos.", '',
                       'La corrección de nombres puede resolver identificadores cercanos. La regeneración tiene un presupuesto limitado y puede terminar con una consulta incompleta. Los filtros o las agregaciones incorrectos que sí se ejecutan no producen un error de MySQL para activar otra generación.'])
    for nombre, s in resumen.items():
        lineas.extend(['', f'## Errores: {nombre}', '', '| Categoría | Cantidad |', '|---|---:|'])
        lineas.extend(f'| {c} | {n} |' for c, n in sorted(s['errores'].items()))
        if not s['errores']:
            lineas.append('| Sin errores | 0 |')
        lineas.extend(['', '| Nivel | Aciertos |', '|---|---:|'])
        lineas.extend(f"| {n} | {v['aciertos']}/{v['preguntas']} |" for n, v in s['por_nivel'].items())
    if 'validacion_propia' in resumen:
        s = resumen['validacion_propia']
        filas = cargar_csv(raiz / 'validacion_propia.csv')
        intervalo = bootstrap(filas)
        estimacion = max(0., s['ex'] * .8)
        resumen['prediccion_oculta'] = dict(ex_estimada=estimacion, intervalo_bootstrap=intervalo,
                                           metodo='EX propia con descuento relativo heurístico de 20%')
        lineas.extend(['', '## Predicción de evaluación oculta', '',
                      f"Se estima una EX oculta de **{estimacion:.2f}**, frente a {s['ex']:.3f} en la validación propia. Se aplica un descuento relativo del 20% por la generación con plantillas, el uso de solo dos dominios de validación y la selección del adapter sobre ese mismo conjunto. El descuento es una hipótesis conservadora, no una medición ni un intervalo de confianza.", '',
                      f"El intervalo bootstrap jerárquico de EX propia es [{intervalo[0]:.3f}, {intervalo[1]:.3f}]. Se remuestrean esquemas y preguntas con semilla 2026. Con dos esquemas, este intervalo no representa toda la variación esperable entre bases desconocidas.", '',
                      'Los errores de tablas o columnas indican problemas de correspondencia con el esquema; los de JOIN y agregación requieren revisar relaciones y nivel de agrupación. Una consulta ejecutable puede seguir teniendo filtros o resultados incorrectos. La clasificación automática es heurística; los casos particulares se registran en revision_errores.csv.'])
        seleccion_ruta = raiz / 'seleccion.json'
        seleccion = json.loads(seleccion_ruta.read_text(encoding='utf-8')) if seleccion_ruta.exists() else {}
        if 'baseline' in resumen and seleccion.get('adapter') in resumen:
            mejora = resumen[seleccion['adapter']]['ex'] - resumen['baseline']['ex']
            puntos_ex = 30 * min(1., s['ex'] / .70)
            lineas.extend(['', f'La mejora atribuible al adapter, medida sin reparación en ambas versiones, es {mejora:+.3f}. La reparación se evalúa como un experimento separado sobre ese adapter.', '',
                           f'Si la EX final se repitiera en la evaluación oculta, correspondería a {puntos_ex:.1f}/30 en el componente de exactitud. El aporte del entrenamiento en la configuración final se determinará al evaluar las dos versiones con la misma estrategia de inferencia.'])
    (raiz / 'resumen_resultados.json').write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding='utf-8')
    (raiz / 'analisis.md').write_text('\n'.join(lineas) + '\n', encoding='utf-8')
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
