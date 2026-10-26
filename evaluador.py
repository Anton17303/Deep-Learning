"""Evaluador de exactitud por ejecución (EX ponderada), réplica del criterio del enunciado.

  - el orden de filas solo cuenta si la pregunta lo pide (campo `ordenado`)
  - números redondeados a 2 decimales
  - columnas adicionales en la predicción no penalizan
  - peso por nivel: fácil 1, media 2, difícil 3

Uso (en Colab, con MySQL y las bases construidas):
  python evaluador.py                                  # usa solucion.py + config.json
  python evaluador.py --config config_base.json        # modelo base sin adapter
  python evaluador.py --oraculo                        # prueba del evaluador: usa el SQL de referencia
"""
import argparse
import csv
import datetime
import decimal
import itertools
import json
import os
import re
import time
import hashlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


# ---------------------------------------------------------- comparación EX ---
def _norm(v):
    if isinstance(v, (decimal.Decimal, float, int)) and not isinstance(v, bool):
        return round(float(v), 2)
    if isinstance(v, (datetime.date, datetime.datetime)):
        return str(v)
    return v


def _clave(fila):
    return tuple((x is None, str(x)) for x in fila)


def _cols(filas):
    return list(zip(*filas)) if filas else []


def coincide(filas_pred, filas_ref, ordenado):
    """True si las columnas de la referencia están (en algún orden) dentro de la predicción."""
    pred = [tuple(_norm(v) for v in f) for f in filas_pred]
    ref = [tuple(_norm(v) for v in f) for f in filas_ref]
    if len(pred) != len(ref):
        return False
    if not ref:
        return True
    cp, cr = _cols(pred), _cols(ref)
    if len(cp) < len(cr):
        return False
    firma = (lambda c: list(map(str, c))) if ordenado else (lambda c: sorted(map(str, c)))
    cand = [[i for i, p in enumerate(cp) if firma(p) == firma(r)] for r in cr]
    if any(not c for c in cand):
        return False
    for asign in itertools.product(*cand):
        if len(set(asign)) != len(asign):
            continue
        proy = [tuple(f[i] for i in asign) for f in pred]
        if (proy == ref) if ordenado else (sorted(proy, key=_clave) == sorted(ref, key=_clave)):
            return True
    return False


# --------------------------------------------------- categorías de error ----
def _tablas(sql):
    return set(re.findall(r"\b(?:from|join)\s+`?(\w+)`?", sql, re.I))


def _rasgos_agg(sql):
    return (len(re.findall(r"\b(count|sum|avg|min|max)\s*\(", sql, re.I)),
            bool(re.search(r"\bgroup\s+by\b", sql, re.I)), bool(re.search(r"\bhaving\b", sql, re.I)),
            bool(re.search(r"\bover\s*\(", sql, re.I)))


def _where(sql):
    m = re.search(r"\bwhere\b(.*?)(\bgroup\s+by\b|\border\s+by\b|\bhaving\b|\blimit\b|$)", sql, re.I | re.S)
    return re.sub(r"\s+", "", m.group(1).lower()) if m else ""


def categoria_error(sql_pred, sql_ref, error):
    """Clasificación heurística; revisar a mano los casos dudosos (README)."""
    if error:
        e = error.lower()
        if "1054" in e or "1146" in e or "unknown column" in e or "doesn't exist" in e:
            return "columna o tabla inexistente"
        if "1055" in e or "1140" in e or "only_full_group_by" in e or "1111" in e:
            return "agregación"
        if "1052" in e or "ambiguous" in e:
            return "JOIN"
        return "sintaxis"
    if _tablas(sql_pred) != _tablas(sql_ref) or \
            len(re.findall(r"\bjoin\b", sql_pred, re.I)) != len(re.findall(r"\bjoin\b", sql_ref, re.I)):
        return "JOIN"
    if _rasgos_agg(sql_pred) != _rasgos_agg(sql_ref):
        return "agregación"
    if _where(sql_pred) != _where(sql_ref):
        return "filtro"
    return "resultado distinto"


# ---------------------------------------------------------------- ejecución ---
class Ejecutor:
    """Replica `ejecutar(sql)` del contrato: solo lectura, máx. 10 filas, 3 llamadas por pregunta."""

    def __init__(self, base):
        from generador.bd import conectar
        self.con = conectar(base)
        cur = self.con.cursor()
        cur.execute("SET SESSION TRANSACTION READ ONLY")
        self.llamadas = 0

    def __call__(self, sql):
        from prompt import es_solo_lectura
        self.llamadas += 1
        if self.llamadas > 3:
            return dict(ok=False, columnas=[], filas=[], error="límite de 3 llamadas excedido")
        if not es_solo_lectura(sql):
            return dict(ok=False, columnas=[], filas=[], error="solo se permiten SELECT/WITH")
        try:
            cur = self.con.cursor()
            cur.execute("SET SESSION MAX_EXECUTION_TIME=10000")
            cur.execute(sql)
            cols = [d[0] for d in cur.description]
            filas = [list(map(str, f)) for f in cur.fetchmany(10)]
            cur.fetchall()
            return dict(ok=True, columnas=cols, filas=filas, error=None)
        except Exception as e:  # noqa: BLE001
            return dict(ok=False, columnas=[], filas=[], error=str(e)[:300])

    def completo(self, sql):
        from prompt import es_solo_lectura
        if not es_solo_lectura(sql):
            raise ValueError("Solo se permite una consulta SELECT o WITH SELECT")
        cur = self.con.cursor()
        cur.execute("SET SESSION MAX_EXECUTION_TIME=10000")
        cur.execute(sql)
        return cur.fetchall()

    def cerrar(self):
        self.con.close()


def evaluar(preguntas, generar, salida):
    from prompt import cargar_esquema
    filas_csv = []
    for q in preguntas:
        ej = Ejecutor(f"p3_{q['esquema_id']}")
        t0 = time.time()
        sql_pred, error, acierto = "", None, False
        try:
            sql_pred = generar(cargar_esquema(q["esquema_id"]), q["pregunta"], ej)
        except Exception as e:  # noqa: BLE001
            error = f"excepción en generar_sql: {e}"
        seg = time.time() - t0
        ref = ej.completo(q["sql_ref"])
        if not error:
            ej.llamadas = 0
            try:
                pred = ej.completo(sql_pred)
                acierto = coincide(pred, ref, q["ordenado"]) and seg <= 30
            except Exception as e:  # noqa: BLE001
                error = str(e)[:300]
        cat = "" if acierto else ("tiempo excedido" if seg > 30 else categoria_error(sql_pred, q["sql_ref"], error))
        filas_csv.append(dict(id=q["id"], esquema_id=q["esquema_id"], nivel=q["nivel"], peso=q["peso"],
                              acierto=int(acierto), categoria_error=cat, tiempo_s=round(seg, 2),
                              pregunta=q["pregunta"], sql_pred=sql_pred, sql_ref=q["sql_ref"], error=error or ""))
        ej.cerrar()
        print(f"{q['id']} nivel {q['nivel']} {'OK ' if acierto else 'FALLA'} {cat} {seg:.2f}s", flush=True)
        Path(salida).parent.mkdir(parents=True, exist_ok=True)
        with open(salida, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas_csv[0]))
            w.writeheader()
            w.writerows(filas_csv)
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas_csv[0]))
        w.writeheader()
        w.writerows(filas_csv)
    total = sum(r["peso"] for r in filas_csv)
    ex = sum(r["peso"] for r in filas_csv if r["acierto"]) / total
    print(f"\nEX ponderada = {ex:.3f}")
    resumen = dict(ex_ponderada=ex, preguntas=len(filas_csv), peso_total=total,
                   aciertos=sum(r['acierto'] for r in filas_csv),
                   tiempo_medio_s=sum(r['tiempo_s'] for r in filas_csv) / len(filas_csv),
                   tiempo_maximo_s=max(r['tiempo_s'] for r in filas_csv))
    Path(salida).with_suffix('.json').write_text(json.dumps(resumen, indent=2), encoding='utf-8')
    for n in (1, 2, 3):
        rs = [r for r in filas_csv if r["nivel"] == n]
        print(f"  nivel {n}: {sum(r['acierto'] for r in rs)}/{len(rs)}")
    return ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preguntas", default="datos/validacion/preguntas.jsonl")
    ap.add_argument("--salida", default="resultados/validacion_propia.csv")
    ap.add_argument("--config", help="config.json alternativo (p. ej. usar_adapter=false)")
    ap.add_argument("--oraculo", action="store_true", help="usa el SQL de referencia (prueba del evaluador)")
    a = ap.parse_args()
    qs = [json.loads(l) for l in (RAIZ / a.preguntas).read_text(encoding="utf-8").splitlines() if l.strip()]
    if not qs:
        raise ValueError("No hay preguntas para evaluar")
    if a.oraculo:
        refs = {q["pregunta"]: q["sql_ref"] for q in qs}
        generar = lambda esquema, pregunta, ejecutar=None: refs[pregunta]  # noqa: E731
    else:
        if a.config:
            os.environ["CONFIG_JSON"] = a.config
        from solucion import generar_sql as generar
    evaluar(qs, generar, a.salida)


if __name__ == "__main__":
    main()
