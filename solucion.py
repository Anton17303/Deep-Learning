"""Contrato del Proyecto 3. Expone generar_sql(esquema, pregunta, ejecutar=None) -> str.

Carga el modelo base de config.json y, si usar_adapter es true, el adapter LoRA.
Generación determinista (do_sample=False, semilla fija). Variable de entorno
CONFIG_JSON permite evaluar con otro config (p. ej. el modelo base sin adapter).
"""
import json
import os
import time
from pathlib import Path

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("CUDA_MODULE_LOADING", "LAZY")
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed

from prompt import construir_mensajes, es_solo_lectura, extraer_sql, resolver_modelo, corregir_identificadores

RAIZ = Path(__file__).resolve().parent
CFG = json.loads(Path(os.environ.get("CONFIG_JSON", RAIZ / "config.json")).read_text(encoding="utf-8"))

# ---- opciones de inferencia (el experimento de inferencia las cambia aquí) ----
FORMATO_ESQUEMA = CFG.get("formato_esquema", "show_create")
REPARAR = CFG.get("reparar", False)
MAX_REINTENTOS = 2
FEWSHOT = 0
MAX_NUEVOS_TOKENS = 320
LIMITE_SEG = 25                   # el evaluador corta a los 30 s por pregunta
FALLBACK = "SELECT 1"

if CFG["modelo_base"] not in {"Qwen/Qwen2.5-Coder-1.5B-Instruct", "Qwen/Qwen2.5-Coder-0.5B-Instruct", "Qwen/Qwen3-1.7B"}:
    raise ValueError("Modelo base fuera de la lista permitida")
if CFG.get("usar_adapter", True) and not (RAIZ / CFG["adapter"] / "adapter_model.safetensors").is_file():
    raise FileNotFoundError("No se encontró un adapter entrenado en la ruta configurada")
torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", "4")))
set_seed(CFG["semilla"])
_t0 = time.time()
_origen = resolver_modelo(CFG["modelo_base"])
_tok = AutoTokenizer.from_pretrained(_origen)
_cuda = torch.cuda.is_available()
_cuantizado = _cuda and CFG.get("cuantizacion") == "nf4"
_opciones = {}
if _cuantizado:
    _opciones["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
_modelo = AutoModelForCausalLM.from_pretrained(
    _origen,
    torch_dtype=torch.float16 if _cuda else torch.float32,  # la T4 no soporta bf16
    device_map="auto" if _cuda else None,
    **_opciones,
)
if CFG.get("usar_adapter", True):
    from peft import PeftModel
    _modelo = PeftModel.from_pretrained(_modelo, str(RAIZ / CFG["adapter"]))
    if not _cuantizado:
        _modelo = _modelo.merge_and_unload()
_modelo.eval()
CARGA_SEG = time.time() - _t0  # el límite de carga es 5 min
if CARGA_SEG > 300:
    raise TimeoutError("La carga del modelo superó los 300 segundos")

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
    if restante <= 0:
        return FALLBACK
    with torch.inference_mode():
        out = _modelo.generate(
            **ids, max_new_tokens=MAX_NUEVOS_TOKENS, do_sample=False, temperature=None,
            top_p=None, top_k=None, max_time=restante,
            pad_token_id=_tok.eos_token_id)
    return _tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True)


def generar_sql(esquema: str, pregunta: str, ejecutar=None) -> str:
    t0 = time.time()
    set_seed(CFG["semilla"])
    msgs = construir_mensajes(esquema, pregunta, FORMATO_ESQUEMA, _ejemplos_fewshot())
    sql = extraer_sql(_generar(msgs, LIMITE_SEG))
    if REPARAR and ejecutar is not None:
        for _ in range(MAX_REINTENTOS):          # 2 ejecuciones + 2 regeneraciones como máximo
            if time.time() - t0 > LIMITE_SEG - 10:
                break
            if es_solo_lectura(sql):
                r = ejecutar(sql)
            else:
                r = dict(ok=False, error="La salida no es una consulta SELECT o WITH SELECT válida de solo lectura.")
            if r.get("ok"):
                break
            corregido = corregir_identificadores(sql, esquema)
            if corregido != sql and es_solo_lectura(corregido):
                sql = corregido
                continue
            msgs = msgs + [
                {"role": "assistant", "content": sql},
                {"role": "user", "content": f"La consulta falló en MySQL con: {r.get('error')}. "
                                            "Comprueba las tablas, columnas y alias contra el esquema. "
                                            "Usa sus identificadores exactos, sin traducirlos ni inventarlos. "
                                            "Devuelve solo la consulta SQL corregida."}]
            sql = extraer_sql(_generar(msgs, LIMITE_SEG - (time.time() - t0)))
    return sql if es_solo_lectura(sql) else FALLBACK
