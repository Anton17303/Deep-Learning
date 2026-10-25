"""Crea y puebla una base por esquema/variante y guarda el texto de
SHOW CREATE TABLE (el que recibe el modelo) en datos/esquemas/<id>.sql.

Uso:  python -m generador.construir_bases [--semilla 2026]
"""
import argparse
import random
from pathlib import Path

from .bd import conectar
from .esquemas import todos

RAIZ = Path(__file__).resolve().parent.parent


def construir(esq, semilla):
    rng = random.Random(f"{semilla}-{esq.id}")
    con = conectar()
    cur = con.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS `{esq.base}`")
    cur.execute(f"CREATE DATABASE `{esq.base}` CHARACTER SET utf8mb4")
    cur.execute(f"USE `{esq.base}`")
    for ddl in esq.ddl():
        cur.execute(ddl)
    ids = {}
    for n in esq.orden_creacion():
        t = esq.tablas[n]
        filas = esq.filas_de(n, rng, ids)
        marcas = ",".join(["%s"] * len(t.cols))
        cols = ",".join(f"`{c.db}`" for c in t.cols)
        cur.executemany(f"INSERT INTO `{t.db}` ({cols}) VALUES ({marcas})", filas)
    textos = []
    for n in esq.orden_creacion():
        cur.execute(f"SHOW CREATE TABLE `{esq.tablas[n].db}`")
        textos.append(cur.fetchone()[1] + ";")
    con.close()
    return "\n\n".join(textos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semilla", type=int, default=2026)
    a = ap.parse_args()
    (RAIZ / "datos/esquemas").mkdir(parents=True, exist_ok=True)
    for esq in todos():
        texto = construir(esq, a.semilla)
        (RAIZ / "datos/esquemas" / f"{esq.id}.sql").write_text(texto, encoding="utf-8")
        print("ok", esq.id)


if __name__ == "__main__":
    main()
