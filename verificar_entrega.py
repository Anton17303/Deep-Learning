"""Comprobación de integridad y empaquetado de archivos del proyecto."""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIRECTORIOS = ['adapter', 'datos', 'generador', 'notebooks', 'resultados', 'scripts', 'tests', 'configuraciones']
ARCHIVOS = ['solucion.py', 'prompt.py', 'evaluador.py', 'entrenar.py', 'analizar.py',
            'ejecutar_proyecto.py', 'comprobar_inferencia.py', 'preparar_presentacion.py', 'presentacion.pdf', 'verificar_entrega.py', 'config.json', 'config_base.json',
            'config_reparacion.json', 'config_base_reparacion.json', 'requirements.txt', 'README.md', 'BITACORA.md',
            'CONTRIBUCIONES.md', 'historial_git.txt', 'experimentos.md', 'LICENCIAS.md']


def archivos_proyecto():
    rutas = [RAIZ / p for p in ARCHIVOS if (RAIZ / p).exists()]
    for nombre in DIRECTORIOS:
        for ruta in (RAIZ / nombre).rglob('*'):
            if ruta.is_file() and '__pycache__' not in ruta.parts and ruta.suffix not in ['.pt', '.pyc', '.log'] and ruta.name != '.gitkeep':
                rutas.append(ruta)
    return sorted(rutas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', action='store_true')
    args = parser.parse_args()
    leer = lambda p: [json.loads(l) for l in (RAIZ / p).read_text(encoding='utf-8').splitlines() if l.strip()]
    train, val = leer('datos/entrenamiento.jsonl'), leer('datos/validacion/preguntas.jsonl')
    reporte = json.loads((RAIZ / 'datos/reporte_datos.json').read_text(encoding='utf-8'))
    checks = dict(dataset_minimo=len(train) >= 2000,
                  esquemas_entrenamiento=len({r['esquema_id'].rsplit('_', 1)[0] for r in train}) >= 10,
                  preguntas_validacion=len(val) >= 40,
                  esquemas_validacion=len({r['esquema_id'] for r in val}) >= 2,
                  particion_sin_fuga=not bool({r['esquema_id'].rsplit('_', 1)[0] for r in train} &
                                             {r['esquema_id'].rsplit('_', 1)[0] for r in val}),
                  mysql_correcto=reporte['motor'] == 'MySQL 8.4.10',
                  adapter_presente=(RAIZ / 'adapter/adapter_model.safetensors').exists(),
                  resultados_presentes=(RAIZ / 'resultados/validacion_propia.csv').exists(),
                  notebooks=all((RAIZ / f'notebooks/{n}.ipynb').exists() for n in ['01_datos', '02_entrenamiento', '03_evaluacion']))
    for nombre in ['lora_r8', 'lora_r16']:
        p = RAIZ / f'resultados/{nombre}/resumen.json'
        checks[f'{nombre}_completo'] = p.exists() and json.loads(p.read_text())['entrenamiento_completo']
    contrato = RAIZ / 'resultados/contrato_inferencia.json'
    checks['contrato_inferencia'] = contrato.exists() and json.loads(contrato.read_text(encoding='utf-8'))['cumple']
    pruebas = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'], cwd=RAIZ,
                             capture_output=True, text=True)
    checks['pruebas'] = pruebas.returncode == 0
    estado = dict(comprobaciones=checks, completo=all(checks.values()),
                  pruebas=pruebas.stderr, sha256_dataset=hashlib.sha256((RAIZ / 'datos/entrenamiento.jsonl').read_bytes()).hexdigest())
    (RAIZ / 'resultados/verificacion.json').write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifiesto = {str(p.relative_to(RAIZ)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in archivos_proyecto() if p.name != 'manifest.json'}
    (RAIZ / 'resultados/manifest.json').write_text(json.dumps(manifiesto, indent=2) + '\n', encoding='utf-8')
    if args.zip:
        with zipfile.ZipFile(RAIZ / 'entrega.zip', 'w', zipfile.ZIP_DEFLATED) as z:
            for ruta in archivos_proyecto():
                z.write(ruta, ruta.relative_to(RAIZ))
    print(json.dumps(estado, indent=2, ensure_ascii=False))
    return 0 if estado['completo'] else 1


if __name__ == '__main__':
    sys.exit(main())
