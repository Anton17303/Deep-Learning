"""Contrato del Proyecto 3. Expone generar_sql(esquema, pregunta, ejecutar=None) -> str.

Carga el modelo base de config.json y, si usar_adapter es true, el adapter LoRA.
Generación determinista (do_sample=False, semilla fija). Variable de entorno
CONFIG_JSON permite evaluar con otro config (p. ej. el modelo base sin adapter).
"""
import json
import os
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

from prompt import construir_mensajes, es_solo_lectura, extraer_sql

RAIZ = Path(__file__).resolve().parent
CFG = json.loads(Path(os.environ.get("CONFIG_JSON", RAIZ / "config.json")).read_text(encoding="utf-8"))

# ---- opciones de inferencia (el experimento de inferencia las cambia aquí) ----
FORMATO_ESQUEMA = "show_create"   # "show_create" | "compacto"  (debe coincidir con el entrenamiento)
REPARAR = False                   # True: usa `ejecutar` para corregir errores (máx. 2 reintentos)
MAX_REINTENTOS = 2                # = 2 llamadas a ejecutar (el límite del evaluador es 3)
FEWSHOT = 0                       # nº de ejemplos de datos/entrenamiento.jsonl antepuestos al prompt
MAX_NUEVOS_TOKENS = 320
LIMITE_SEG = 25                   # el evaluador corta a los 30 s por pregunta
FALLBACK = "SELECT 1"

set_seed(CFG["semilla"])
_t0 = time.time()
_tok = AutoTokenizer.from_pretrained(CFG["modelo_base"])
_cuda = torch.cuda.is_available()
_modelo = AutoModelForCausalLM.from_pretrained(
    CFG["modelo_base"],
    torch_dtype=torch.float16 if _cuda else torch.float32,  # la T4 no soporta bf16
    device_map="auto" if _cuda else None,
)
if CFG.get("usar_adapter", True):
    from peft import PeftModel
    _modelo = PeftModel.from_pretrained(_modelo, str(RAIZ / CFG["adapter"]))
    _modelo = _modelo.merge_and_unload()
_modelo.eval()
CARGA_SEG = time.time() - _t0  # el límite de carga es 5 min

_QWEN3 = "Qwen3" in CFG["modelo_base"]
_FEW = None


def _ejemplos_fewshot():
    global _FEW
    if _FEW is None:
        _FEW = []
        if FEWSHOT:
            from prompt import cargar_ejemplos
            filas = cargar_ejemplos()
            paso = max(1, len(filas) // FEWSHOT)
            _FEW = [(r["esquema"], r["pregunta"], r["sql"]) for r in filas[::paso][:FEWSHOT]]
    return _FEW


def _generar(mensajes, restante):
    kw = {"enable_thinking": False} if _QWEN3 else {}
    texto = _tok.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True, **kw)
    ids = _tok(texto, return_tensors="pt").to(_modelo.device)
    with torch.inference_mode():
        out = _modelo.generate(
            **ids, max_new_tokens=MAX_NUEVOS_TOKENS, do_sample=False, temperature=None,
            top_p=None, top_k=None, max_time=max(3.0, restante),
            pad_token_id=_tok.eos_token_id)
    return _tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True)


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    t0 = time.time()
    set_seed(CFG["semilla"])
    msgs = construir_mensajes(esquema, pregunta, FORMATO_ESQUEMA, _ejemplos_fewshot())
    sql = extraer_sql(_generar(msgs, LIMITE_SEG))
    if REPARAR and ejecutar is not None:
        for _ in range(MAX_REINTENTOS):          # 2 ejecuciones + 2 regeneraciones como máximo
            if not es_solo_lectura(sql) or time.time() - t0 > LIMITE_SEG - 10:
                break
            r = ejecutar(sql)
            if r.get("ok"):
                break
            msgs = msgs + [
                {"role": "assistant", "content": sql},
                {"role": "user", "content": f"La consulta falló en MySQL con: {r.get('error')}. "
                                            f"Devuelve solo la consulta SQL corregida."}]
            sql = extraer_sql(_generar(msgs, LIMITE_SEG - (time.time() - t0)))
    return sql if es_solo_lectura(sql) else FALLBACK
