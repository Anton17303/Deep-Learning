"""Flujo completo de datos, baseline, entrenamiento, selección e inferencia."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def ejecutar(*argumentos):
    subprocess.run([sys.executable, *argumentos], cwd=RAIZ, check=True)


def evaluacion_valida(salida, config):
    csv_ruta, json_ruta = RAIZ / salida, (RAIZ / salida).with_suffix('.json')
    if not csv_ruta.exists() or not json_ruta.exists():
        return False
    try:
        esperado = json.loads((RAIZ / config).read_text(encoding='utf-8'))
        metadata = json.loads(json_ruta.read_text(encoding='utf-8'))
        if metadata.get('torch') != importlib.metadata.version('torch'):
            return False
        try:
            dispositivo = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                                 text=True, stderr=subprocess.DEVNULL).splitlines()[0].strip()
        except (OSError, subprocess.SubprocessError, IndexError):
            dispositivo = 'CPU'
        if '+cpu' in metadata['torch'] or os.environ.get('CUDA_VISIBLE_DEVICES') in ['', '-1']:
            dispositivo = 'CPU'
        if metadata.get('dispositivo') != dispositivo:
            return False
        preguntas_bytes = (RAIZ / 'datos/validacion/preguntas.jsonl').read_bytes()
        preguntas = {q['id']: q for q in (json.loads(l) for l in preguntas_bytes.decode('utf-8').splitlines())}
        with csv_ruta.open(encoding='utf-8', newline='') as f:
            filas = list(csv.DictReader(f))
        if metadata.get('configuracion') != esperado or metadata.get('sha256_preguntas') != hashlib.sha256(preguntas_bytes).hexdigest():
            return False
        if len(filas) != len(preguntas) or {r['id'] for r in filas} != set(preguntas):
            return False
        if not all(r['pregunta'] == preguntas[r['id']]['pregunta'] and r['sql_ref'] == preguntas[r['id']]['sql_ref'] for r in filas):
            return False
        if esperado.get('usar_adapter'):
            pesos = RAIZ / esperado['adapter'] / 'adapter_model.safetensors'
            if not pesos.exists():
                return False
            if metadata.get('sha256_adapter'):
                if metadata['sha256_adapter'] != hashlib.sha256(pesos.read_bytes()).hexdigest():
                    return False
            elif pesos.stat().st_mtime > csv_ruta.stat().st_mtime:
                return False
        return True
    except (OSError, ValueError, KeyError):
        return False


def entrenamiento_valido(nombre):
    resumen_ruta = RAIZ / f'resultados/{nombre}/resumen.json'
    if not resumen_ruta.exists():
        return False
    resumen = json.loads(resumen_ruta.read_text(encoding='utf-8'))
    config = json.loads((RAIZ / f'configuraciones/{nombre}.json').read_text(encoding='utf-8'))
    if config.get('adapter_inicial'):
        pesos = RAIZ / config['adapter_inicial'] / 'adapter_model.safetensors'
        if not pesos.exists() or resumen.get('sha256_adapter_inicial') != hashlib.sha256(pesos.read_bytes()).hexdigest():
            return False
    return (resumen.get('entrenamiento_completo', False) and resumen['config'] == config and
            resumen['sha256_dataset'] == hashlib.sha256((RAIZ / 'datos/entrenamiento.jsonl').read_bytes()).hexdigest() and
            all((RAIZ / f'resultados/{nombre}' / p).exists() for p in ['adapter/adapter_model.safetensors', 'loss.csv', 'loss.png']))


def normalizar_adapter(nombre):
    resumen = json.loads((RAIZ / f'resultados/{nombre}/resumen.json').read_text(encoding='utf-8'))
    ruta = RAIZ / f'resultados/{nombre}/adapter'
    configuracion = json.loads((ruta / 'adapter_config.json').read_text(encoding='utf-8'))
    configuracion['base_model_name_or_path'] = resumen['config']['modelo_base']
    (ruta / 'adapter_config.json').write_text(json.dumps(configuracion, indent=2) + '\n', encoding='utf-8')
    tarjeta = (f"---\nlicense: apache-2.0\nbase_model: {resumen['config']['modelo_base']}\nlibrary_name: peft\n---\n\n"
               f"# Adapter Text-to-SQL\n\nSe entrenó un adapter QLoRA de rango {resumen['config']['r']} "
               f"sobre la base NF4 de 4 bits, con semilla {resumen['config']['semilla']}. "
               f"Se procesaron {resumen['ejemplos_procesados']} ejemplos del corpus de {resumen['ejemplos_dataset']} pares "
               f"en {resumen['pasos_realizados']} pasos. La pérdida se calculó únicamente sobre la respuesta SQL.\n\n"
               f"Parámetros entrenables: {resumen['parametros_entrenables']:,}. "
               f"Tiempo de entrenamiento: {resumen['segundos_entrenamiento'] / 60:.2f} minutos.\n\n"
               "Los pesos del modelo base se descargan por separado. La inferencia se realiza mediante solucion.py.\n")
    if resumen['config'].get('adapter_inicial'):
        tarjeta += '\nSe continuó desde un adapter del mismo rango que procesó 304 ejemplos, con un optimizador reiniciado para recorrer una época adicional completa.\n'
    (ruta / 'README.md').write_text(tarjeta, encoding='utf-8')
    shutil.copy2(RAIZ / 'LICENCIA_MODELO.txt', ruta / 'LICENSE')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--omitir-datos', action='store_true')
    parser.add_argument('--reanudar', action='store_true')
    parser.add_argument('--max-steps', type=int)
    parser.add_argument('--ampliar-entrenamiento', action='store_true')
    args = parser.parse_args()
    os.environ.setdefault('USE_TF', '0')
    os.environ.setdefault('USE_FLAX', '0')
    if not args.omitir_datos:
        ejecutar('-m', 'generador.construir_bases')
        ejecutar('-m', 'generador.validar_pares')
        ejecutar('-m', 'generador.crear_validacion')
    ejecutar('evaluador.py', '--oraculo', '--salida', 'resultados/oraculo.csv')
    if not (args.reanudar and evaluacion_valida('resultados/baseline.csv', 'config_base.json')):
        ejecutar('evaluador.py', '--config', 'config_base.json', '--salida', 'resultados/baseline.csv')
    nombres = ['lora_r8', 'lora_r16']
    if args.ampliar_entrenamiento:
        nombres += ['lora_r8_completo', 'lora_r16_completo']
    for nombre in nombres:
        parametros = ['entrenar.py', '--config', f'configuraciones/{nombre}.json', '--salida', f'resultados/{nombre}']
        if args.reanudar:
            parametros.append('--reanudar')
        if args.max_steps:
            parametros.extend(['--max-steps', str(args.max_steps)])
        if not (args.reanudar and entrenamiento_valido(nombre)):
            ejecutar(*parametros)
        normalizar_adapter(nombre)
        rango = nombre.replace('lora_', '')
        if not (args.reanudar and evaluacion_valida(f'resultados/{nombre}.csv', f'configuraciones/evaluar_{rango}.json')):
            ejecutar('evaluador.py', '--config', f'configuraciones/evaluar_{rango}.json', '--salida', f'resultados/{nombre}.csv')
    from analizar import cargar_csv, resumir
    mejor = max(nombres, key=lambda n: resumir(cargar_csv(RAIZ / f'resultados/{n}.csv'))['ex'])
    destino = RAIZ / 'adapter'
    destino.mkdir(exist_ok=True)
    for archivo in (RAIZ / f'resultados/{mejor}/adapter').iterdir():
        if archivo.is_file():
            shutil.copy2(archivo, destino / archivo.name)
    config_adapter = json.loads((destino / 'adapter_config.json').read_text())
    config_adapter['base_model_name_or_path'] = 'Qwen/Qwen2.5-Coder-0.5B-Instruct'
    (destino / 'adapter_config.json').write_text(json.dumps(config_adapter, indent=2) + '\n', encoding='utf-8')
    config = json.loads((RAIZ / 'config.json').read_text())
    config.update(usar_adapter=True, reparar=False)
    (RAIZ / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    config_reparacion = {**config, 'reparar': True}
    (RAIZ / 'config_reparacion.json').write_text(json.dumps(config_reparacion, indent=2) + '\n', encoding='utf-8')
    if not (args.reanudar and evaluacion_valida('resultados/reparacion.csv', 'config_reparacion.json')):
        ejecutar('evaluador.py', '--config', 'config_reparacion.json', '--salida', 'resultados/reparacion.csv')
    original = resumir(cargar_csv(RAIZ / f'resultados/{mejor}.csv'))
    reparada = resumir(cargar_csv(RAIZ / 'resultados/reparacion.csv'))
    reparar = reparada['ex'] > original['ex'] and reparada['exceden_30s'] == 0
    config['reparar'] = reparar
    (RAIZ / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    fuente = 'reparacion' if reparar else mejor
    shutil.copy2(RAIZ / f'resultados/{fuente}.csv', RAIZ / 'resultados/validacion_propia.csv')
    shutil.copy2(RAIZ / f'resultados/{fuente}.json', RAIZ / 'resultados/validacion_propia.json')
    (RAIZ / 'resultados/seleccion.json').write_text(json.dumps(dict(adapter=mejor, reparar=reparar,
        ex_original=original['ex'], ex_reparacion=reparada['ex'],
        entrenamiento_completo=all(json.loads((RAIZ / f'resultados/{n}/resumen.json').read_text())['entrenamiento_completo']
                                    for n in nombres)), indent=2), encoding='utf-8')
    ejecutar('analizar.py')
    ejecutar('comprobar_inferencia.py')
    ejecutar('-m', 'unittest', 'discover', '-s', 'tests', '-v')


if __name__ == '__main__':
    main()
