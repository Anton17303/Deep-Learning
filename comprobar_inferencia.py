"""Verificación de carga, determinismo, formato de salida y tiempos."""
import json
from pathlib import Path
import time

from prompt import cargar_esquema, es_solo_lectura


def main():
    import solucion
    from evaluador import Ejecutor
    raiz = Path(__file__).resolve().parent
    preguntas = [json.loads(l) for l in (raiz / 'datos/validacion/preguntas.jsonl').read_text(encoding='utf-8').splitlines()]
    filas = []
    for indice in [0, 26, 13]:
        q = preguntas[indice]
        esquema = cargar_esquema(q['esquema_id'])
        respuestas, tiempos, llamadas = [], [], []
        for _ in range(2):
            ejecutor = Ejecutor(f"p3_{q['esquema_id']}")
            try:
                inicio = time.perf_counter()
                respuestas.append(solucion.generar_sql(esquema, q['pregunta'], ejecutor))
                tiempos.append(time.perf_counter() - inicio)
                llamadas.append(ejecutor.llamadas)
            finally:
                ejecutor.cerrar()
        filas.append(dict(id=q['id'], determinista=respuestas[0] == respuestas[1],
                          solo_lectura=all(es_solo_lectura(s) for s in respuestas),
                          cumple_tiempo=max(tiempos) <= 30, tiempos_segundos=tiempos,
                          llamadas_diagnostico=llamadas, cumple_llamadas=max(llamadas) <= 3,
                          sql=respuestas[0]))
    import torch
    resultado = dict(configuracion=solucion.CFG, carga_segundos=solucion.CARGA_SEG,
                     dispositivo=torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU',
                     torch=torch.__version__, cuda=torch.version.cuda,
                     carga_valida=solucion.CARGA_SEG <= 300, casos=filas,
                     cumple=solucion.CARGA_SEG <= 300 and all(r['determinista'] and r['solo_lectura'] and r['cumple_tiempo'] and r['cumple_llamadas'] for r in filas))
    (raiz / 'resultados/contrato_inferencia.json').write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return 0 if resultado['cumple'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
