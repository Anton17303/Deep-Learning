"""Prompt compartido entre ENTRENAMIENTO e INFERENCIA.

Regla de oro: el formato que se use para entrenar debe ser el mismo que usa
solucion.py; si se cambia aquí, hay que reentrenar.
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

SISTEMA = (
    "Eres un experto en MySQL 8.4. Recibes el esquema de una base de datos (sentencias "
    "CREATE TABLE con sus COMMENT) y una pregunta en español. Responde ÚNICAMENTE con una "
    "consulta SQL de solo lectura (SELECT o WITH ... SELECT), sin explicaciones ni comentarios. "
    "Respeta ONLY_FULL_GROUP_BY y devuelve exactamente las columnas que pide la pregunta."
)


def formatear_esquema(esquema: str, formato: str = "show_create") -> str:
    """'show_create' = texto tal cual. 'compacto' = sin ENGINE/CHARSET/KEY, conserva COMMENT
    (útil como experimento de inferencia: menos tokens)."""
    if formato == "show_create":
        return esquema.strip()
    if formato != "compacto":
        raise ValueError(f"formato desconocido: {formato}")
    salida = []
    for linea in esquema.splitlines():
        if linea.lstrip().startswith("KEY "):
            continue
        if linea.startswith(") ENGINE="):
            m = re.search(r"COMMENT='(.*)'", linea)
            linea = ")" + (f" COMMENT='{m.group(1)}'" if m else "") + ";"
        salida.append(linea)
    return "\n".join(salida).strip()


def mensaje_usuario(esquema: str, pregunta: str, formato: str = "show_create") -> str:
    return f"### Esquema\n{formatear_esquema(esquema, formato)}\n\n### Pregunta\n{pregunta.strip()}\n\n### SQL"


def construir_mensajes(esquema, pregunta, formato="show_create", fewshot=None):
    """fewshot: lista de (esquema, pregunta, sql) que se anteponen como turnos previos."""
    msgs = [{"role": "system", "content": SISTEMA}]
    for e, p, s in (fewshot or []):
        msgs.append({"role": "user", "content": mensaje_usuario(e, p, formato)})
        msgs.append({"role": "assistant", "content": s})
    msgs.append({"role": "user", "content": mensaje_usuario(esquema, pregunta, formato)})
    return msgs


# ------------------------------------------------------------ post-proceso ---
_PROHIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|grant|revoke|create|rename|call|handler|load)\b"
    r"|\binto\s+(outfile|dumpfile)\b", re.I)


def _sin_literales(sql):
    return re.sub(r"'(?:[^'\\]|\\.|'')*'|\"(?:[^\"\\]|\\.)*\"|`[^`]*`", "''", sql)


def extraer_sql(texto: str) -> str:
    t = texto.strip()
    m = re.search(r"```(?:sql)?\s*(.*?)```", t, re.S | re.I)
    if m:
        t = m.group(1).strip()
    m = re.search(r"\b(with|select)\b", t, re.I)
    if m:
        t = t[m.start():]
    comilla, i = "", 0
    while i < len(t):
        ch = t[i]
        if comilla:
            if ch == "\\" and comilla != "`":
                i += 2
                continue
            if ch == comilla:
                if i + 1 < len(t) and t[i + 1] == comilla:
                    i += 2
                    continue
                comilla = ""
        elif ch in "'\"`":
            comilla = ch
        elif t[i:i + 2] == "/*":
            fin = t.find("*/", i + 2)
            if fin == -1:
                return ""
            i = fin + 2
            continue
        elif ch == "#" or (t[i:i + 2] == "--" and (i + 2 == len(t) or t[i + 2].isspace())):
            fin = t.find("\n", i)
            if fin == -1:
                break
            i = fin + 1
            continue
        elif ch == ";":
            t = t[:i]
            break
        i += 1
    return t.strip()


def es_solo_lectura(sql: str) -> bool:
    from sqlglot import parse, exp
    try:
        if '/*!' in sql:
            return False
        sentencias = [s for s in parse(sql, read="mysql") if s is not None]
        if len(sentencias) != 1:
            return False
        arbol = sentencias[0]
        if not isinstance(arbol, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
            return False
        prohibidas = (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop,
                      exp.Alter, exp.Command, exp.Into, exp.Lock, exp.Merge)
        return not any(isinstance(n, prohibidas) for n in arbol.walk())
    except Exception:
        return False


# ------------------------------------------------------------------- datos ---
def cargar_esquema(esquema_id: str) -> str:
    return (RAIZ / "datos/esquemas" / f"{esquema_id}.sql").read_text(encoding="utf-8")


def cargar_ejemplos(archivo="datos/entrenamiento.jsonl"):
    """Devuelve filas con 'esquema' (texto), 'pregunta' y 'sql' listas para entrenar."""
    cache, filas = {}, []
    for linea in (RAIZ / archivo).read_text(encoding="utf-8").splitlines():
        r = json.loads(linea)
        if r["esquema_id"] not in cache:
            cache[r["esquema_id"]] = cargar_esquema(r["esquema_id"])
        r["esquema"] = cache[r["esquema_id"]]
        filas.append(r)
    return filas
