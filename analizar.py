"""Resumen de evaluaciones por ejecución y predicción de generalización."""
import argparse
import collections
import csv
import json
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
                exceden_30s=int((tiempos > 30).sum()),
                errores=dict(collections.Counter(r['categoria_error'] for r in filas if r['acierto'] == '0')),
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
            s = resumir(filas)
            resumen[nombre] = s
            lineas.append(f"| {nombre} | {s['aciertos']}/40 | {s['ex']:.3f} | {s['tiempo_medio_s']:.2f} | {s['tiempo_maximo_s']:.2f} |")
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
        if 'baseline' in resumen:
            mejora = s['ex'] - resumen['baseline']['ex']
            puntos = 30 * min(1., s['ex'] / .70) + 10 * min(1., max(0., mejora) / .15)
            lineas.extend(['', f'La mejora local frente al baseline es {mejora:+.3f}. Si estos valores se repitieran en la evaluación oculta, el componente de rendimiento sería {puntos:.1f}/40. No corresponde a una nota observada del docente.'])
    (raiz / 'resumen_resultados.json').write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding='utf-8')
    (raiz / 'analisis.md').write_text('\n'.join(lineas) + '\n', encoding='utf-8')
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
