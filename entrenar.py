"""Entrenamiento LoRA con pérdida únicamente sobre la respuesta SQL."""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import time
from pathlib import Path

os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('USE_FLAX', '0')
import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

from prompt import cargar_ejemplos, construir_mensajes

RAIZ = Path(__file__).resolve().parent


def codificar(tokenizer, fila, formato, max_length):
    mensajes = construir_mensajes(fila['esquema'], fila['pregunta'], formato)
    prefijo = tokenizer.apply_chat_template(mensajes, tokenize=True, add_generation_prompt=True)
    completo = tokenizer.apply_chat_template(
        mensajes + [{'role': 'assistant', 'content': fila['sql']}],
        tokenize=True, add_generation_prompt=False)
    if completo[:len(prefijo)] != prefijo:
        raise ValueError('El prefijo del prompt no coincide con el texto de entrenamiento')
    if len(completo) > max_length:
        raise ValueError(f"Ejemplo {fila['id']} con {len(completo)} tokens; límite {max_length}")
    return {'input_ids': completo, 'labels': [-100] * len(prefijo) + completo[len(prefijo):]}


def entrenar(config, salida, max_steps=None, reanudar=False):
    set_seed(config['semilla'])
    torch.set_num_threads(int(os.environ.get('TORCH_NUM_THREADS', '4')))
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    dispositivo = 'cuda' if torch.cuda.is_available() else 'cpu'
    dtype = torch.float16 if dispositivo == 'cuda' else torch.float32
    origen = os.environ.get('MODEL_LOCAL_PATH', config['modelo_base'])
    tokenizer = AutoTokenizer.from_pretrained(origen)
    tokenizer.pad_token = tokenizer.eos_token
    modelo = AutoModelForCausalLM.from_pretrained(origen, torch_dtype=dtype)
    modelo.config.use_cache = False
    modelo = get_peft_model(modelo, LoraConfig(
        task_type='CAUSAL_LM', r=config['r'], lora_alpha=config['lora_alpha'],
        lora_dropout=config['lora_dropout'], target_modules=config['target_modules'], bias='none'))
    modelo.to(dispositivo)
    modelo.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    datos = cargar_ejemplos()
    sha_dataset = hashlib.sha256((RAIZ / 'datos/entrenamiento.jsonl').read_bytes()).hexdigest()
    ejemplos = [codificar(tokenizer, r, config['formato_esquema'], config['max_length']) for r in datos]
    orden = list(range(len(ejemplos)))
    random.Random(config['semilla']).shuffle(orden)
    acumulacion = config['gradient_accumulation_steps']
    pasos_epoca = math.ceil(len(orden) / acumulacion)
    pasos_totales = math.ceil(pasos_epoca * config['num_train_epochs'])
    limite = min(max_steps, pasos_totales) if max_steps else pasos_totales
    entrenables = sum(p.numel() for p in modelo.parameters() if p.requires_grad)
    total = sum(p.numel() for p in modelo.parameters())
    optim = torch.optim.AdamW((p for p in modelo.parameters() if p.requires_grad),
                             lr=config['learning_rate'], weight_decay=config['weight_decay'])
    calentamiento = max(1, round(pasos_totales * config['warmup_ratio']))

    def escala(paso):
        return min((paso + 1) / calentamiento, max(0., (pasos_totales - paso) /
                   max(1, pasos_totales - calentamiento)))

    scheduler = torch.optim.lr_scheduler.LambdaLR(optim, escala)
    scaler = torch.amp.GradScaler('cuda', enabled=dispositivo == 'cuda')
    checkpoint = salida / 'estado.pt'
    inicio_paso, historial, transcurrido = 0, [], 0.
    if reanudar and checkpoint.exists():
        estado = torch.load(checkpoint, map_location=dispositivo, weights_only=False)
        if estado['config'] != config:
            raise ValueError('El checkpoint corresponde a otra configuración')
        if estado.get('sha256_dataset') != sha_dataset:
            raise ValueError('Los datos cambiaron respecto al checkpoint')
        from peft import set_peft_model_state_dict
        set_peft_model_state_dict(modelo, estado['adapter'])
        optim.load_state_dict(estado['optim'])
        scheduler.load_state_dict(estado['scheduler'])
        scaler.load_state_dict(estado['scaler'])
        inicio_paso, historial, transcurrido = estado['paso'], estado['historial'], estado['segundos']
        torch.set_rng_state(estado['rng_cpu'].cpu())
        if dispositivo == 'cuda' and estado.get('rng_cuda') is not None:
            torch.cuda.set_rng_state_all(estado['rng_cuda'])
    print(json.dumps({'dispositivo': dispositivo, 'parametros_entrenables': entrenables,
                      'parametros_totales': total, 'ejemplos': len(ejemplos),
                      'pasos_completos': pasos_totales, 'limite': limite}), flush=True)
    inicio = time.perf_counter()
    modelo.train()
    for paso in range(inicio_paso, limite):
        t0 = time.perf_counter()
        epoca, dentro = divmod(paso, pasos_epoca)
        indices = orden[dentro * acumulacion:(dentro + 1) * acumulacion]
        optim.zero_grad(set_to_none=True)
        perdida, tokens = 0., 0
        for i in indices:
            e = ejemplos[i]
            ids = torch.tensor([e['input_ids']], device=dispositivo)
            labels = torch.tensor([e['labels']], device=dispositivo)
            with torch.autocast(device_type=dispositivo, dtype=dtype, enabled=dispositivo == 'cuda'):
                respuesta = int((labels != -100).sum().item()) + 1
                loss = modelo(input_ids=ids, attention_mask=torch.ones_like(ids),
                              labels=labels[:, -respuesta:], logits_to_keep=respuesta).loss
            if not torch.isfinite(loss):
                raise RuntimeError('Pérdida no finita')
            scaler.scale(loss / len(indices)).backward()
            perdida += loss.detach().float().item() / len(indices)
            tokens += len(e['input_ids'])
        scaler.unscale_(optim)
        torch.nn.utils.clip_grad_norm_((p for p in modelo.parameters() if p.requires_grad), 1.)
        scaler.step(optim)
        scaler.update()
        scheduler.step()
        registro = dict(paso=paso + 1, epoca=epoca + min((dentro + 1) * acumulacion / len(orden), 1.),
                        loss=perdida, learning_rate=scheduler.get_last_lr()[0],
                        segundos=time.perf_counter() - t0, tokens=tokens)
        historial.append(registro)
        print(json.dumps(registro), flush=True)
        if (paso + 1) % 1 == 0:
            from peft import get_peft_model_state_dict
            modelo.save_pretrained(salida / 'adapter', safe_serialization=True)
            torch.save(dict(config=config, sha256_dataset=sha_dataset, paso=paso + 1, historial=historial,
                            segundos=transcurrido + time.perf_counter() - inicio,
                            adapter=get_peft_model_state_dict(modelo), optim=optim.state_dict(),
                            scheduler=scheduler.state_dict(), scaler=scaler.state_dict(),
                            rng_cpu=torch.get_rng_state(),
                            rng_cuda=torch.cuda.get_rng_state_all() if dispositivo == 'cuda' else None), checkpoint)
            guardar_resultados(salida, config, historial, entrenables, total, len(ejemplos),
                               pasos_totales, transcurrido + time.perf_counter() - inicio, dispositivo)
    return salida / 'adapter'


def guardar_resultados(salida, config, historial, entrenables, total, ejemplos, pasos_totales, segundos, dispositivo):
    with (salida / 'loss.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(historial[0]))
        w.writeheader()
        w.writerows(historial)
    resumen = dict(config=config, parametros_entrenables=entrenables, parametros_totales=total,
                   ejemplos_dataset=ejemplos, pasos_realizados=len(historial), pasos_previstos=pasos_totales,
                   ejemplos_procesados=min(len(historial) * config['gradient_accumulation_steps'], ejemplos),
                   entrenamiento_completo=len(historial) >= pasos_totales,
                   segundos_entrenamiento=segundos, dispositivo=dispositivo,
                   sha256_dataset=hashlib.sha256((RAIZ / 'datos/entrenamiento.jsonl').read_bytes()).hexdigest(),
                   torch=torch.__version__)
    (salida / 'resumen.json').write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([h['paso'] for h in historial], [h['loss'] for h in historial], linewidth=1)
    ax.set(xlabel='Paso de optimización', ylabel='Loss sobre SQL', title=config['nombre'])
    fig.tight_layout()
    fig.savefig(salida / 'loss.png', dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--salida', required=True)
    parser.add_argument('--max-steps', type=int)
    parser.add_argument('--reanudar', action='store_true')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    entrenar(config, args.salida, args.max_steps, args.reanudar)


if __name__ == '__main__':
    main()
