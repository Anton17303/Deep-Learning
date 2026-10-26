"""Prompt compartido entre ENTRENAMIENTO e INFERENCIA.

Regla de oro: el formato que se use para entrenar debe ser el mismo que usa
solucion.py; si se cambia aquí, hay que reentrenar.
"""
import json
import os
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def resolver_modelo(modelo_base):
    origen = os.environ.get('MODEL_LOCAL_PATH')
    if origen:
        return origen
    local = RAIZ / '.runtime/model'
    if modelo_base == 'Qwen/Qwen2.5-Coder-0.5B-Instruct' and (local / 'model.safetensors').is_file():
        return str(local)
    return modelo_base

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


def corregir_identificadores(sql, esquema):
    """Corrige nombres inexistentes con una coincidencia fuerte y única en el DDL."""
    from collections import defaultdict
    from difflib import SequenceMatcher
    import unicodedata
    from sqlglot import parse, parse_one, exp
    if not es_solo_lectura(sql):
        return sql

    def normalizar(nombre):
        return ''.join(c for c in unicodedata.normalize('NFKD', nombre).casefold() if c.isalnum())

    def cercano(nombre, candidatos):
        if nombre in candidatos:
            return nombre
        puntuaciones = sorted(((SequenceMatcher(None, normalizar(nombre), normalizar(c)).ratio(), c)
                               for c in candidatos), reverse=True)
        if not puntuaciones or puntuaciones[0][0] < .88:
            return None
        if len(puntuaciones) > 1 and puntuaciones[0][0] - puntuaciones[1][0] < .10:
            return None
        return puntuaciones[0][1]

    try:
        tablas = {}
        partes = [p for p in re.split(r'(?im)(?=^[ \t]*CREATE[ \t]+TABLE\b)', esquema) if p.strip()]
        sentencias = [parse_one(p, read='mysql') for p in partes] if len(partes) > 1 else parse(esquema, read='mysql')
        for ddl in sentencias:
            if isinstance(ddl, exp.Create) and isinstance(ddl.this, exp.Schema):
                tablas[ddl.this.this.name] = {c.name for c in ddl.this.expressions if isinstance(c, exp.ColumnDef)}
        if not tablas:
            return sql
        arbol = parse_one(sql, read='mysql')
        ctes = {c.alias_or_name.casefold() for c in arbol.find_all(exp.CTE)}
        relaciones, renombres, cambios = defaultdict(set), {}, False
        usadas, desconocidas = set(), False
        for tabla in arbol.find_all(exp.Table):
            if tabla.name.casefold() in ctes:
                continue
            original = tabla.name
            nombre = cercano(original, tablas)
            if nombre is None:
                desconocidas = True
                continue
            if nombre != original:
                tabla.set('this', exp.to_identifier(nombre, quoted=True))
                cambios = True
                if not tabla.alias:
                    renombres[original] = nombre
            usadas.add(nombre)
            relaciones[tabla.alias_or_name.casefold()].add(nombre)
        aliases_salida = {a.alias.casefold() for a in arbol.find_all(exp.Alias)}
        for columna in arbol.find_all(exp.Column):
            if columna.table in renombres:
                columna.set('table', exp.to_identifier(renombres[columna.table], quoted=True))
            if columna.name.casefold() in aliases_salida:
                continue
            if columna.table:
                opciones = relaciones.get(columna.table.casefold(), set())
            else:
                opciones = usadas if not desconocidas else set()
            if len(opciones) != 1:
                continue
            candidatas = tablas[next(iter(opciones))]
            nombre = cercano(columna.name, candidatas)
            if nombre is not None and nombre != columna.name:
                columna.set('this', exp.to_identifier(nombre, quoted=True))
                cambios = True
        return arbol.sql(dialect='mysql') if cambios else sql
    except Exception:
        return sql


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
