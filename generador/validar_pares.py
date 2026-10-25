"""Genera candidatos, los ejecuta en MySQL y separa aceptados / descartes.

Uso:  python -m generador.validar_pares [--semilla 2026]
Salida: datos/entrenamiento.jsonl, datos/descartes.jsonl, datos/reporte_datos.json
Un par se acepta solo si el SQL se ejecuta sin error y devuelve al menos una fila.
"""
import argparse
import collections
import json
from pathlib import Path

import pymysql

from .bd import conectar
from .esquemas import todos
from .pares import generar

RAIZ = Path(__file__).resolve().parent.parent
MAX_FILAS = 500


def motivo(exc):
    codigo = exc.args[0] if exc.args else 0
    return {1064: "sintaxis", 1054: "columna inexistente", 1146: "tabla inexistente",
            1055: "viola ONLY_FULL_GROUP_BY", 1052: "columna ambigua",
            1140: "viola ONLY_FULL_GROUP_BY"}.get(codigo, f"otro error ({codigo})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=2026)
    a = ap.parse_args()
    aceptados, descartes = [], []
    for S in todos(rol="train"):
        con = conectar(S.base)
        cur = con.cursor()
        for r in generar(S, a.semilla):
            try:
                cur.execute(r["sql"])
                filas = cur.fetchmany(MAX_FILAS + 1)
                cur.fetchall()
            except pymysql.MySQLError as e:
                descartes.append({**r, "motivo": motivo(e), "detalle": str(e)[:200]})
                continue
            if not filas:
                descartes.append({**r, "motivo": "resultado vacío"})
            elif len(filas) > MAX_FILAS:
                descartes.append({**r, "motivo": f"más de {MAX_FILAS} filas"})
            else:
                aceptados.append({**r, "n_filas": len(filas)})
        con.close()
    for i, r in enumerate(aceptados, 1):
        r["id"] = f"tr{i:05d}"
    (RAIZ / "datos").mkdir(exist_ok=True)
    for nombre, filas in (("entrenamiento", aceptados), ("descartes", descartes)):
        with open(RAIZ / f"datos/{nombre}.jsonl", "w", encoding="utf-8") as f:
            for r in filas:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rep = {
        "candidatos": len(aceptados) + len(descartes),
        "aceptados": len(aceptados),
        "descartados": len(descartes),
        "descartes_por_motivo": dict(collections.Counter(d["motivo"] for d in descartes)),
        "descartes_por_plantilla": dict(collections.Counter(d["plantilla"] for d in descartes)),
        "aceptados_por_nivel": dict(collections.Counter(r["nivel"] for r in aceptados)),
        "aceptados_por_esquema": dict(collections.Counter(r["esquema_id"] for r in aceptados)),
        "motor": "MySQL (ver README: pre-validado en 8.0.46; repetir en 8.4.10)",
    }
    (RAIZ / "datos/reporte_datos.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
