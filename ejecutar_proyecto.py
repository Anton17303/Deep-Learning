"""Flujo completo de datos, baseline, entrenamiento, selección e inferencia."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def ejecutar(*argumentos):
    subprocess.run([sys.executable, *argumentos], cwd=RAIZ, check=True)


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
    (ruta / 'README.md').write_text(tarjeta, encoding='utf-8')
    shutil.copy2(RAIZ / 'LICENCIA_MODELO.txt', ruta / 'LICENSE')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--omitir-datos', action='store_true')
    parser.add_argument('--reanudar', action='store_true')
    parser.add_argument('--max-steps', type=int)
    args = parser.parse_args()
    os.environ.setdefault('USE_TF', '0')
    os.environ.setdefault('USE_FLAX', '0')
    if not args.omitir_datos:
        ejecutar('-m', 'generador.construir_bases')
        ejecutar('-m', 'generador.validar_pares')
        ejecutar('-m', 'generador.crear_validacion')
    ejecutar('evaluador.py', '--oraculo', '--salida', 'resultados/oraculo.csv')
    ejecutar('evaluador.py', '--config', 'config_base.json', '--salida', 'resultados/baseline.csv')
    for nombre in ['lora_r8', 'lora_r16']:
        parametros = ['entrenar.py', '--config', f'configuraciones/{nombre}.json', '--salida', f'resultados/{nombre}']
        if args.reanudar:
            parametros.append('--reanudar')
        if args.max_steps:
            parametros.extend(['--max-steps', str(args.max_steps)])
        ejecutar(*parametros)
        normalizar_adapter(nombre)
        rango = nombre.replace('lora_', '')
        ejecutar('evaluador.py', '--config', f'configuraciones/evaluar_{rango}.json', '--salida', f'resultados/{nombre}.csv')
    from analizar import cargar_csv, resumir
    mejor = max(['lora_r8', 'lora_r16'], key=lambda n: resumir(cargar_csv(RAIZ / f'resultados/{n}.csv'))['ex'])
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
    ejecutar('evaluador.py', '--config', 'config_reparacion.json', '--salida', 'resultados/reparacion.csv')
    original = resumir(cargar_csv(RAIZ / f'resultados/{mejor}.csv'))
    reparada = resumir(cargar_csv(RAIZ / 'resultados/reparacion.csv'))
    reparar = reparada['ex'] > original['ex'] and reparada['exceden_30s'] == 0
    config['reparar'] = reparar
    (RAIZ / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    fuente = 'reparacion' if reparar else mejor
    shutil.copy2(RAIZ / f'resultados/{fuente}.csv', RAIZ / 'resultados/validacion_propia.csv')
    shutil.copy2(RAIZ / f'resultados/{fuente}.json', RAIZ / 'resultados/validacion_propia.json')
    if reparar:
        config_base_reparacion = {**config_reparacion, 'usar_adapter': False}
        (RAIZ / 'config_base_reparacion.json').write_text(json.dumps(config_base_reparacion, indent=2) + '\n', encoding='utf-8')
        ejecutar('evaluador.py', '--config', 'config_base_reparacion.json', '--salida', 'resultados/baseline_reparacion.csv')
    (RAIZ / 'resultados/seleccion.json').write_text(json.dumps(dict(adapter=mejor, reparar=reparar,
        ex_original=original['ex'], ex_reparacion=reparada['ex'],
        entrenamiento_completo=all(json.loads((RAIZ / f'resultados/{n}/resumen.json').read_text())['entrenamiento_completo']
                                    for n in ['lora_r8', 'lora_r16'])), indent=2), encoding='utf-8')
    ejecutar('analizar.py')
    ejecutar('comprobar_inferencia.py')
    ejecutar('preparar_presentacion.py')
    ejecutar('-m', 'unittest', 'discover', '-s', 'tests', '-v')


if __name__ == '__main__':
    main()
