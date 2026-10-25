"""Plantillas de pares (pregunta en español, SQL MySQL) sobre un Esquema.

Cada plantilla devuelve un dict {nivel, pregunta, sql, ordenado} o None si no
aplica al esquema. Las preguntas siempre indican qué columnas devolver.
Nivel 1 = una tabla; 2 = JOIN/GROUP BY/HAVING; 3 = subconsultas, WITH,
funciones de ventana y fechas (mismos niveles que la evaluación oculta).
"""
import random

from .esquemas import POOLS


# ------------------------------------------------------------- utilidades ---
def lista(items):
    items = list(items)
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " y " + items[-1]


SINGULARES = {"almacenes": "almacén", "ordenes": "orden", "órdenes": "orden", "funciones": "función",
              "reservaciones": "reservación", "inscripciones": "inscripción",
              "transacciones": "transacción", "aerolineas": "aerolínea", "categorias": "categoría",
              "peliculas": "película", "medicos": "médico", "prestamos": "préstamo", "envios": "envío",
              "especialidades": "especialidad", "habitaciones": "habitación", "sucursales": "sucursal",
              "conductores": "conductor", "profesores": "profesor", "aeropuertos": "aeropuerto",
              "carreras": "carrera", "salas": "sala", "mesas": "mesa", "cuentas": "cuenta",
              "clientes": "cliente", "pasajeros": "pasajero", "pacientes": "paciente"}


def sing(etiqueta):
    """Singular de la primera palabra de una etiqueta de tabla ('tipos de habitación' -> 'tipo de habitación')."""
    primera, *resto = etiqueta.split(" ")
    if primera in SINGULARES:
        nueva = SINGULARES[primera]
    elif primera.endswith("s") and len(primera) > 3:
        nueva = primera[:-1]
    else:
        nueva = primera
    return " ".join([nueva] + resto)


def literal(v):
    return f"'{v}'" if isinstance(v, str) else str(v)


def valor_num(c, rng):
    lo, hi = float(c.arg[0]), float(c.arg[1])
    v = lo + (hi - lo) * rng.uniform(0.25, 0.75)
    return int(round(v)) if c.tipo == "int" or hi - lo > 50 else round(v, 1)


def descriptivas(t, rng, maximo=2):
    """Columnas 'para mostrar' de una tabla: nombres/categorías o, si no hay, la pk."""
    base = t.noms + t.cats
    if not base:
        return [t.pk]
    k = rng.randint(1, min(maximo, len(base)))
    return rng.sample(base, k)


def nombre_pref(t, rng):
    c = t.noms or t.cats or [t.pk]
    return c[0] if rng.random() < 0.8 else rng.choice(c)


def alias_estilo(rng):
    return rng.choice([["t1", "t2", "t3", "t4"], ["a", "b", "c", "d"], ["x", "y", "z", "w"]])


def hijos(S):
    """[(tabla_hija, col_fk, tabla_padre)] sin autorreferencias."""
    out = []
    for t in S.tablas.values():
        for c, padre in t.fks:
            if padre != t.orig:
                out.append((t, c, S.tablas[padre]))
    return out


def sel(cols, alias=None):
    return ", ".join(f"{alias}.{c.db}" if alias else c.db for c in cols)


def fraccion_hijos(h, p):
    return max(1, h.filas / max(p.filas, 1))


# ---------------------------------------------------------------- nivel 1 ---
def e_filtro_num(S, rng):
    t = rng.choice([t for t in S.tablas.values() if t.nums and (t.noms or t.cats)] or [None])
    if t is None:
        return None
    n = rng.choice(t.nums)
    d = descriptivas(t, rng)
    op, txt = rng.choice([(">", "mayor que"), (">=", "mayor o igual que"),
                          ("<", "menor que"), ("<=", "menor o igual que")])
    v = valor_num(n, rng)
    cols = d + [n]
    preg = rng.choice([
        f"Muestra {lista(c.etiqueta for c in cols)} de {t.etiqueta} cuyo {n.etiqueta} sea {txt} {v}.",
        f"¿Qué registros de {t.etiqueta} tienen {n.etiqueta} {txt} {v}? Devuelve {lista(c.etiqueta for c in cols)}.",
        f"Lista {lista(c.etiqueta for c in cols)} de {t.etiqueta} donde el {n.etiqueta} es {txt} {v}.",
    ])
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT {sel(cols)} FROM {t.db} WHERE {n.db} {op} {v}")


def e_filtro_cat(S, rng):
    cand = [t for t in S.tablas.values() if t.cats and (t.noms or len(t.cols) > 2)]
    if not cand:
        return None
    t = rng.choice(cand)
    c = rng.choice(t.cats)
    val = rng.choice(c.arg[0].split("/"))
    d = [x for x in descriptivas(t, rng) if x is not c] or [t.pk]
    preg = rng.choice([
        f"Devuelve {lista(x.etiqueta for x in d)} de {t.etiqueta} donde {c.etiqueta} sea '{val}'.",
        f"¿Qué {t.etiqueta} tienen {c.etiqueta} igual a '{val}'? Muestra {lista(x.etiqueta for x in d)}.",
    ])
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT {sel(d)} FROM {t.db} WHERE {c.db} = '{val}'")


def e_count_total(S, rng):
    t = rng.choice(list(S.tablas.values()))
    preg = rng.choice([
        f"¿Cuántos registros hay en {t.etiqueta}? Devuelve una sola columna con el total.",
        f"Cuenta los registros de {t.etiqueta} y devuelve el total.",
    ])
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT COUNT(*) AS total FROM {t.db}")


def e_count_cat(S, rng):
    cand = [t for t in S.tablas.values() if t.cats]
    if not cand:
        return None
    t = rng.choice(cand)
    c = rng.choice(t.cats)
    val = rng.choice(c.arg[0].split("/"))
    preg = rng.choice([
        f"¿Cuántos registros de {t.etiqueta} tienen {c.etiqueta} igual a '{val}'? Devuelve una sola columna con el total.",
        f"Cuenta los {t.etiqueta} cuyo {c.etiqueta} es '{val}'.",
    ])
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT COUNT(*) AS total FROM {t.db} WHERE {c.db} = '{val}'")


def e_agg(S, rng):
    cand = [t for t in S.tablas.values() if t.nums]
    t = rng.choice(cand)
    n = rng.choice(t.nums)
    fn, nombre = rng.choice([("AVG", "promedio"), ("SUM", "suma total"), ("MAX", "valor máximo"),
                             ("MIN", "valor mínimo")])
    preg = rng.choice([
        f"¿Cuál es el {nombre} de {n.etiqueta} en {t.etiqueta}? Devuelve una sola columna.",
        f"Calcula el {nombre} de {n.etiqueta} de todos los registros de {t.etiqueta}.",
    ])
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT {fn}({n.db}) AS resultado FROM {t.db}")


def e_top_n(S, rng):
    cand = [t for t in S.tablas.values() if t.nums and (t.noms or t.cats)]
    t = rng.choice(cand)
    n = rng.choice(t.nums)
    d = [nombre_pref(t, rng)]
    k = rng.choice([3, 5, 5, 10])
    desc, txt = rng.choice([("DESC", "mayor"), ("ASC", "menor")])
    orden = "de mayor a menor" if desc == "DESC" else "de menor a mayor"
    preg = rng.choice([
        f"Obtén los {k} registros de {t.etiqueta} con {txt} {n.etiqueta}. Devuelve {lista(c.etiqueta for c in d + [n])}, ordenados {orden}.",
        f"Muestra {lista(c.etiqueta for c in d + [n])} de los {k} {t.etiqueta} con {txt} {n.etiqueta}, {orden}.",
    ])
    return dict(nivel=1, pregunta=preg, ordenado=True,
                sql=f"SELECT {sel(d + [n])} FROM {t.db} ORDER BY {n.db} {desc} LIMIT {k}")


def e_distinct(S, rng):
    cand = [t for t in S.tablas.values() if t.cats]
    if not cand:
        return None
    t = rng.choice(cand)
    c = rng.choice(t.cats)
    preg = f"Lista los distintos valores de {c.etiqueta} en {t.etiqueta}, en orden alfabético."
    return dict(nivel=1, pregunta=preg, ordenado=True,
                sql=f"SELECT DISTINCT {c.db} FROM {t.db} ORDER BY {c.db}")


def e_fecha_anio(S, rng):
    cand = [t for t in S.tablas.values() if t.fechas and (t.noms or t.cats or t.nums)]
    t = rng.choice(cand)
    f = rng.choice(t.fechas)
    y = rng.randint(int(f.arg[0]), int(f.arg[1]))
    d = [x for x in (t.noms[:1] + t.nums[:1] + t.cats[:1])][: rng.randint(1, 2)] or [t.pk]
    preg = rng.choice([
        f"Muestra {lista(c.etiqueta for c in d + [f])} de {t.etiqueta} cuyo {f.etiqueta} sea del año {y}.",
        f"¿Qué registros de {t.etiqueta} ocurrieron en {y}? Devuelve {lista(c.etiqueta for c in d + [f])}.",
    ])
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT {sel(d + [f])} FROM {t.db} WHERE YEAR({f.db}) = {y}")


def e_between(S, rng):
    cand = [t for t in S.tablas.values() if t.nums and (t.noms or t.cats)]
    t = rng.choice(cand)
    n = rng.choice(t.nums)
    a = valor_num(n, rng)
    b = a + max(1, abs(round((float(n.arg[1]) - float(n.arg[0])) * 0.2)))
    d = descriptivas(t, rng, 1)
    preg = f"Devuelve {lista(c.etiqueta for c in d + [n])} de {t.etiqueta} con {n.etiqueta} entre {a} y {b} (ambos incluidos)."
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT {sel(d + [n])} FROM {t.db} WHERE {n.db} BETWEEN {a} AND {b}")


def e_like(S, rng):
    cand = [(t, c) for t in S.tablas.values() for c in t.noms if c.arg[0] in POOLS]
    if not cand:
        return None
    t, c = rng.choice(cand)
    letra = rng.choice(POOLS[c.arg[0]])[0]
    extra = [x for x in (t.nums[:1] or t.cats[:1])]
    preg = f"Muestra {lista(x.etiqueta for x in [c] + extra)} de {t.etiqueta} cuyo {c.etiqueta} comience con la letra {letra}."
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT {sel([c] + extra)} FROM {t.db} WHERE {c.db} LIKE '{letra}%'")


def e_rango_fechas(S, rng):
    cand = [t for t in S.tablas.values() if t.fechas and (t.noms or t.cats or t.nums)]
    t = rng.choice(cand)
    f = rng.choice(t.fechas)
    y = rng.randint(int(f.arg[0]), int(f.arg[1]))
    m1 = rng.randint(1, 6)
    m2 = m1 + rng.randint(1, 5)
    d = (t.noms[:1] + t.nums[:1] + t.cats[:1])[:2] or [t.pk]
    ini, fin = f"{y}-{m1:02d}-01", f"{y}-{m2:02d}-28"
    preg = f"Devuelve {lista(c.etiqueta for c in d + [f])} de {t.etiqueta} entre el {ini} y el {fin}."
    return dict(nivel=1, pregunta=preg, ordenado=False,
                sql=f"SELECT {sel(d + [f])} FROM {t.db} WHERE {f.db} BETWEEN '{ini}' AND '{fin}'")


# ---------------------------------------------------------------- nivel 2 ---
def m_join_filtro(S, rng):
    hs = [h for h in hijos(S)]
    h, fk, p = rng.choice(hs)
    A, B = alias_estilo(rng)[:2]
    dh, dp = nombre_pref(h, rng), nombre_pref(p, rng)
    if h.nums and rng.random() < 0.5:
        n = rng.choice(h.nums)
        v = valor_num(n, rng)
        cond, txt = f"{A}.{n.db} > {v}", f"{n.etiqueta} mayor que {v}"
    elif p.cats:
        c = rng.choice(p.cats)
        val = rng.choice(c.arg[0].split("/"))
        cond, txt = f"{B}.{c.db} = '{val}'", f"{c.etiqueta} igual a '{val}' en {p.etiqueta}"
    else:
        return None
    pregs = [
        f"Muestra el {dh.etiqueta} de {h.etiqueta} y el {dp.etiqueta} de {p.etiqueta} relacionado, solo para registros con {txt}.",
        f"Une {h.etiqueta} con {p.etiqueta} y devuelve {dh.etiqueta} ({h.etiqueta}) y {dp.etiqueta} ({p.etiqueta}) cuando {txt}.",
    ]
    sql = (f"SELECT {A}.{dh.db}, {B}.{dp.db} FROM {h.db} {A} JOIN {p.db} {B} "
           f"ON {A}.{fk.db} = {B}.{p.pk.db} WHERE {cond}")
    return dict(nivel=2, pregunta=rng.choice(pregs), sql=sql, ordenado=False)


def _grupo(S, rng):
    h, fk, p = rng.choice(hijos(S))
    A, B = alias_estilo(rng)[:2]
    return h, fk, p, A, B, nombre_pref(p, rng)


def m_group_count(S, rng):
    h, fk, p, A, B, dp = _grupo(S, rng)
    orden = rng.random() < 0.5
    preg = f"¿Cuántos registros de {h.etiqueta} tiene cada {sing(p.etiqueta)}? Devuelve {dp.etiqueta} y el total (columna total)"
    sql = (f"SELECT {B}.{dp.db}, COUNT(*) AS total FROM {p.db} {B} JOIN {h.db} {A} "
           f"ON {A}.{fk.db} = {B}.{p.pk.db} GROUP BY {B}.{p.pk.db}, {B}.{dp.db}")
    if orden:
        preg += ", ordenado de mayor a menor total."
        sql += " ORDER BY total DESC"
    else:
        preg += "."
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=orden)


def m_group_sum(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if h.nums]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    A, B = alias_estilo(rng)[:2]
    n, dp = rng.choice(h.nums), nombre_pref(p, rng)
    fn, nombre = rng.choice([("SUM", "suma"), ("AVG", "promedio"), ("MAX", "máximo")])
    preg = f"Para cada {sing(p.etiqueta)}, calcula el {nombre} de {n.etiqueta} en {h.etiqueta}. Devuelve {dp.etiqueta} y el resultado (columna resultado)."
    sql = (f"SELECT {B}.{dp.db}, {fn}({A}.{n.db}) AS resultado FROM {p.db} {B} JOIN {h.db} {A} "
           f"ON {A}.{fk.db} = {B}.{p.pk.db} GROUP BY {B}.{p.pk.db}, {B}.{dp.db}")
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=False)


def m_group_cat(S, rng):
    cand = [t for t in S.tablas.values() if t.cats and t.nums]
    if not cand:
        return None
    t = rng.choice(cand)
    c, n = rng.choice(t.cats), rng.choice(t.nums)
    fn, nombre = rng.choice([("AVG", "promedio"), ("SUM", "suma"), ("MAX", "máximo"), ("MIN", "mínimo")])
    orden = rng.random() < 0.4
    preg = f"Calcula el {nombre} de {n.etiqueta} por {c.etiqueta} en {t.etiqueta}. Devuelve {c.etiqueta} y el resultado (columna resultado)"
    sql = f"SELECT {c.db}, {fn}({n.db}) AS resultado FROM {t.db} GROUP BY {c.db}"
    if orden:
        preg += ", ordenado de mayor a menor."
        sql += " ORDER BY resultado DESC"
    else:
        preg += "."
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=orden)


def m_count_cat(S, rng):
    cand = [t for t in S.tablas.values() if t.cats]
    if not cand:
        return None
    t = rng.choice(cand)
    c = rng.choice(t.cats)
    preg = f"¿Cuántos registros de {t.etiqueta} hay por cada {c.etiqueta}? Devuelve {c.etiqueta} y el total (columna total)."
    return dict(nivel=2, pregunta=preg, ordenado=False,
                sql=f"SELECT {c.db}, COUNT(*) AS total FROM {t.db} GROUP BY {c.db}")


def m_having_count(S, rng):
    h, fk, p, A, B, dp = _grupo(S, rng)
    k = max(1, int(fraccion_hijos(h, p) * rng.uniform(0.7, 1.3)))
    preg = f"¿Qué {p.etiqueta} tienen más de {k} registros en {h.etiqueta}? Devuelve {dp.etiqueta} y la cantidad (columna total)."
    sql = (f"SELECT {B}.{dp.db}, COUNT(*) AS total FROM {p.db} {B} JOIN {h.db} {A} "
           f"ON {A}.{fk.db} = {B}.{p.pk.db} GROUP BY {B}.{p.pk.db}, {B}.{dp.db} HAVING COUNT(*) > {k}")
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=False)


def m_having_avg(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if h.nums]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    A, B = alias_estilo(rng)[:2]
    n, dp = rng.choice(h.nums), nombre_pref(p, rng)
    v = valor_num(n, rng)
    preg = f"Muestra los {p.etiqueta} cuyo promedio de {n.etiqueta} en {h.etiqueta} supere {v}. Devuelve {dp.etiqueta} y el promedio (columna promedio)."
    sql = (f"SELECT {B}.{dp.db}, AVG({A}.{n.db}) AS promedio FROM {p.db} {B} JOIN {h.db} {A} "
           f"ON {A}.{fk.db} = {B}.{p.pk.db} GROUP BY {B}.{p.pk.db}, {B}.{dp.db} HAVING AVG({A}.{n.db}) > {v}")
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=False)


def m_join3(S, rng):
    cand = [t for t in S.tablas.values()
            if len({a for _, a in t.fks}) >= 2 and t.nums]
    if not cand:
        return None
    t = rng.choice(cand)
    (c1, p1n), (c2, p2n) = rng.sample([(c, a) for c, a in t.fks if a != t.orig], 2) \
        if len({a for _, a in t.fks}) >= 2 else (None, None)
    if p1n == p2n:
        return None
    p1, p2 = S.tablas[p1n], S.tablas[p2n]
    A, B, C = alias_estilo(rng)[:3]
    n = rng.choice(t.nums)
    v = valor_num(n, rng)
    d1, d2 = nombre_pref(p1, rng), nombre_pref(p2, rng)
    preg = (f"Muestra el {d1.etiqueta} de {p1.etiqueta}, el {d2.etiqueta} de {p2.etiqueta} y el {n.etiqueta} "
            f"de {t.etiqueta} para los registros con {n.etiqueta} mayor que {v}.")
    sql = (f"SELECT {B}.{d1.db}, {C}.{d2.db}, {A}.{n.db} FROM {t.db} {A} "
           f"JOIN {p1.db} {B} ON {A}.{c1.db} = {B}.{p1.pk.db} "
           f"JOIN {p2.db} {C} ON {A}.{c2.db} = {C}.{p2.pk.db} WHERE {A}.{n.db} > {v}")
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=False)


def m_group_anio(S, rng):
    cand = [t for t in S.tablas.values() if t.fechas and (t.nums or True)]
    t = rng.choice(cand)
    f = rng.choice(t.fechas)
    if t.nums and rng.random() < 0.6:
        n = rng.choice(t.nums)
        agg, que = f"SUM({n.db})", f"la suma de {n.etiqueta}"
    else:
        agg, que = "COUNT(*)", "el número de registros"
    preg = f"Calcula {que} de {t.etiqueta} por año de {f.etiqueta}. Devuelve el año (columna anio) y el resultado (columna total), ordenado por año."
    sql = f"SELECT YEAR({f.db}) AS anio, {agg} AS total FROM {t.db} GROUP BY YEAR({f.db}) ORDER BY anio"
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=True)


def m_count_distinct(S, rng):
    h, fk, p = rng.choice(hijos(S))
    preg = f"¿Cuántos valores distintos de {fk.etiqueta} hay en {h.etiqueta}? Devuelve una sola columna con el total."
    return dict(nivel=2, pregunta=preg, ordenado=False,
                sql=f"SELECT COUNT(DISTINCT {fk.db}) AS total FROM {h.db}")


def m_group_filtro_padre(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if p.cats]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    A, B = alias_estilo(rng)[:2]
    c = rng.choice(p.cats)
    val = rng.choice(c.arg[0].split("/"))
    dp = nombre_pref(p, rng)
    if dp is c:
        return None
    preg = (f"Para los {p.etiqueta} con {c.etiqueta} igual a '{val}', cuenta sus registros en {h.etiqueta}. "
            f"Devuelve {dp.etiqueta} y el total (columna total).")
    sql = (f"SELECT {B}.{dp.db}, COUNT({A}.{h.pk.db}) AS total FROM {p.db} {B} LEFT JOIN {h.db} {A} "
           f"ON {A}.{fk.db} = {B}.{p.pk.db} WHERE {B}.{c.db} = '{val}' GROUP BY {B}.{p.pk.db}, {B}.{dp.db}")
    return dict(nivel=2, pregunta=preg, sql=sql, ordenado=False)


# ---------------------------------------------------------------- nivel 3 ---
def h_sub_avg(S, rng):
    cand = [t for t in S.tablas.values() if t.nums and (t.noms or t.cats)]
    t = rng.choice(cand)
    n = rng.choice(t.nums)
    d = [nombre_pref(t, rng)]
    arriba = rng.random() < 0.7
    op, txt = (">", "supera el") if arriba else ("<", "está por debajo del")
    preg = f"Devuelve {lista(c.etiqueta for c in d + [n])} de los {t.etiqueta} cuyo {n.etiqueta} {txt} promedio general de {t.etiqueta}."
    sql = f"SELECT {sel(d + [n])} FROM {t.db} WHERE {n.db} {op} (SELECT AVG({n.db}) FROM {t.db})"
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_sin_hijos(S, rng):
    h, fk, p = rng.choice(hijos(S))
    A, B = alias_estilo(rng)[:2]
    dp = nombre_pref(p, rng)
    variante = rng.choice(["not_exists", "not_in", "left"])
    if variante == "not_exists":
        sql = (f"SELECT {B}.{dp.db} FROM {p.db} {B} WHERE NOT EXISTS "
               f"(SELECT 1 FROM {h.db} {A} WHERE {A}.{fk.db} = {B}.{p.pk.db})")
    elif variante == "not_in":
        sql = f"SELECT {B}.{dp.db} FROM {p.db} {B} WHERE {B}.{p.pk.db} NOT IN (SELECT {fk.db} FROM {h.db})"
    else:
        sql = (f"SELECT {B}.{dp.db} FROM {p.db} {B} LEFT JOIN {h.db} {A} ON {A}.{fk.db} = {B}.{p.pk.db} "
               f"WHERE {A}.{h.pk.db} IS NULL")
    preg = rng.choice([
        f"¿Qué {p.etiqueta} no tienen ningún registro en {h.etiqueta}? Devuelve {dp.etiqueta}.",
        f"Lista el {dp.etiqueta} de {p.etiqueta} que nunca aparecen en {h.etiqueta}.",
    ])
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def _total_por_padre(h, fk, p, n, A):
    return f"SELECT {A}.{fk.db} AS id_padre, SUM({A}.{n.db}) AS total FROM {h.db} {A} GROUP BY {A}.{fk.db}"


def h_cte_sobre_promedio(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if h.nums]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    A, B = alias_estilo(rng)[:2]
    n, dp = rng.choice(h.nums), nombre_pref(p, rng)
    preg = (f"Calcula la suma de {n.etiqueta} de {h.etiqueta} por cada {sing(p.etiqueta)} y muestra solo los {p.etiqueta} "
            f"cuya suma supere el promedio de esas sumas. Devuelve {dp.etiqueta} y la suma (columna total).")
    sql = (f"WITH tot AS ({_total_por_padre(h, fk, p, n, A)}) "
           f"SELECT {B}.{dp.db}, tot.total FROM {p.db} {B} JOIN tot ON tot.id_padre = {B}.{p.pk.db} "
           f"WHERE tot.total > (SELECT AVG(total) FROM tot)")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_top1_por_padre(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if h.nums]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    A, B = alias_estilo(rng)[:2]
    n, dp = rng.choice(h.nums), nombre_pref(p, rng)
    preg = (f"Para cada {sing(p.etiqueta)}, obtén el registro de {h.etiqueta} con mayor {n.etiqueta}. "
            f"Devuelve {dp.etiqueta} y ese {n.etiqueta}.")
    sql = (f"WITH r AS (SELECT {A}.{fk.db} AS id_padre, {A}.{n.db} AS valor, "
           f"ROW_NUMBER() OVER (PARTITION BY {A}.{fk.db} ORDER BY {A}.{n.db} DESC, {A}.{h.pk.db}) AS rn "
           f"FROM {h.db} {A}) SELECT {B}.{dp.db}, r.valor FROM r JOIN {p.db} {B} "
           f"ON r.id_padre = {B}.{p.pk.db} WHERE r.rn = 1")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_acumulado(S, rng):
    cand = [t for t in S.tablas.values() if t.fechas and t.nums]
    t = rng.choice(cand)
    f, n = rng.choice(t.fechas), rng.choice(t.nums)
    k = rng.choice([10, 15, 20])
    preg = (f"Muestra los primeros {k} registros de {t.etiqueta} ordenados por {f.etiqueta} (y por id en caso de empate), "
            f"con {f.etiqueta}, {n.etiqueta} y el acumulado de {n.etiqueta} (columna acumulado).")
    sql = (f"SELECT {f.db}, {n.db}, SUM({n.db}) OVER (ORDER BY {f.db}, {t.pk.db}) AS acumulado "
           f"FROM {t.db} ORDER BY {f.db}, {t.pk.db} LIMIT {k}")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=True)


def h_ranking(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if h.nums]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    A, B = alias_estilo(rng)[:2]
    n, dp = rng.choice(h.nums), nombre_pref(p, rng)
    fn = rng.choice(["RANK", "DENSE_RANK"])
    preg = (f"Calcula la suma de {n.etiqueta} de {h.etiqueta} por {sing(p.etiqueta)} y asigna una posición "
            f"({'con huecos' if fn == 'RANK' else 'sin huecos'} en caso de empate) de mayor a menor suma. "
            f"Devuelve {dp.etiqueta}, la suma (columna total) y la posición (columna posicion), ordenado por posición.")
    sql = (f"WITH tot AS ({_total_por_padre(h, fk, p, n, A)}) "
           f"SELECT {B}.{dp.db}, tot.total, {fn}() OVER (ORDER BY tot.total DESC) AS posicion "
           f"FROM {p.db} {B} JOIN tot ON tot.id_padre = {B}.{p.pk.db} ORDER BY posicion, {B}.{p.pk.db}")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=True)


def h_datediff(S, rng):
    cand = [t for t in S.tablas.values() if t.fechas and (t.noms or t.cats or t.nums)]
    t = rng.choice(cand)
    f = rng.choice(t.fechas)
    y = rng.randint(int(f.arg[0]), int(f.arg[1]))
    d = [t.pk] if not (t.noms or t.cats) else [nombre_pref(t, rng)]
    preg = (f"Para los registros de {t.etiqueta} con {f.etiqueta} en {y}, calcula cuántos días pasaron hasta el 2026-01-01. "
            f"Devuelve {d[0].etiqueta} y los días (columna dias).")
    sql = f"SELECT {sel(d)}, DATEDIFF('2026-01-01', {f.db}) AS dias FROM {t.db} WHERE YEAR({f.db}) = {y}"
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_mes_top(S, rng):
    cand = [t for t in S.tablas.values() if t.fechas and t.nums]
    t = rng.choice(cand)
    f, n = rng.choice(t.fechas), rng.choice(t.nums)
    preg = (f"¿En qué mes (formato AAAA-MM) se acumula la mayor suma de {n.etiqueta} en {t.etiqueta} según {f.etiqueta}? "
            f"Devuelve el mes (columna mes) y la suma (columna total).")
    sql = (f"SELECT DATE_FORMAT({f.db}, '%Y-%m') AS mes, SUM({n.db}) AS total FROM {t.db} "
           f"GROUP BY DATE_FORMAT({f.db}, '%Y-%m') ORDER BY total DESC LIMIT 1")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=True)


def h_porcentaje(S, rng):
    cand = [t for t in S.tablas.values() if t.cats and t.nums]
    if not cand:
        return None
    t = rng.choice(cand)
    c, n = rng.choice(t.cats), rng.choice(t.nums)
    preg = (f"¿Qué porcentaje de la suma total de {n.etiqueta} de {t.etiqueta} representa cada {c.etiqueta}? "
            f"Devuelve {c.etiqueta} y el porcentaje redondeado a 2 decimales (columna porcentaje).")
    sql = (f"SELECT {c.db}, ROUND(100 * SUM({n.db}) / (SELECT SUM({n.db}) FROM {t.db}), 2) AS porcentaje "
           f"FROM {t.db} GROUP BY {c.db}")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_max_por_cat(S, rng):
    cand = [t for t in S.tablas.values() if t.cats and t.nums and (t.noms or True)]
    if not cand:
        return None
    t = rng.choice(cand)
    c, n = rng.choice(t.cats), rng.choice(t.nums)
    d = nombre_pref(t, rng)
    if d is c:
        return None
    A, B = alias_estilo(rng)[:2]
    preg = (f"Para cada {c.etiqueta} de {t.etiqueta}, encuentra los registros con el mayor {n.etiqueta} de su {c.etiqueta}. "
            f"Devuelve {d.etiqueta}, {c.etiqueta} y {n.etiqueta}.")
    sql = (f"SELECT {A}.{d.db}, {A}.{c.db}, {A}.{n.db} FROM {t.db} {A} WHERE {A}.{n.db} = "
           f"(SELECT MAX({B}.{n.db}) FROM {t.db} {B} WHERE {B}.{c.db} = {A}.{c.db})")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_sobre_prom_grupo(S, rng):
    cand = [t for t in S.tablas.values() if t.cats and t.nums]
    if not cand:
        return None
    t = rng.choice(cand)
    c, n = rng.choice(t.cats), rng.choice(t.nums)
    d = nombre_pref(t, rng)
    if d is c:
        return None
    A, B = alias_estilo(rng)[:2]
    preg = (f"Devuelve {d.etiqueta}, {c.etiqueta} y {n.etiqueta} de los {t.etiqueta} cuyo {n.etiqueta} es mayor "
            f"que el promedio de {n.etiqueta} de su mismo {c.etiqueta}.")
    sql = (f"SELECT {A}.{d.db}, {A}.{c.db}, {A}.{n.db} FROM {t.db} {A} WHERE {A}.{n.db} > "
           f"(SELECT AVG({B}.{n.db}) FROM {t.db} {B} WHERE {B}.{c.db} = {A}.{c.db})")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_en_subconsulta(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if h.nums]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    n, dp = rng.choice(h.nums), nombre_pref(p, rng)
    v = valor_num(n, rng)
    preg = (f"Lista el {dp.etiqueta} de los {p.etiqueta} que tienen al menos un registro en {h.etiqueta} "
            f"con {n.etiqueta} mayor que {v}.")
    sql = (f"SELECT {dp.db} FROM {p.db} WHERE {p.pk.db} IN "
           f"(SELECT {fk.db} FROM {h.db} WHERE {n.db} > {v})")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_promedio_de_conteos(S, rng):
    h, fk, p = rng.choice(hijos(S))
    preg = (f"¿Cuál es el promedio de registros de {h.etiqueta} por {sing(p.etiqueta)}, considerando solo los {p.etiqueta} "
            f"que tienen al menos uno? Devuelve una sola columna (columna promedio).")
    sql = f"SELECT AVG(c) AS promedio FROM (SELECT COUNT(*) AS c FROM {h.db} GROUP BY {fk.db}) AS conteos"
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=False)


def h_top_padre_cte(S, rng):
    cand = [(h, fk, p) for h, fk, p in hijos(S) if h.nums]
    if not cand:
        return None
    h, fk, p = rng.choice(cand)
    A, B = alias_estilo(rng)[:2]
    n, dp = rng.choice(h.nums), nombre_pref(p, rng)
    preg = (f"¿Cuál {sing(p.etiqueta)} acumula la mayor suma de {n.etiqueta} en {h.etiqueta}? "
            f"Devuelve {dp.etiqueta} y la suma (columna total).")
    sql = (f"WITH tot AS ({_total_por_padre(h, fk, p, n, A)}) "
           f"SELECT {B}.{dp.db}, tot.total FROM {p.db} {B} JOIN tot ON tot.id_padre = {B}.{p.pk.db} "
           f"ORDER BY tot.total DESC LIMIT 1")
    return dict(nivel=3, pregunta=preg, sql=sql, ordenado=True)


PLANTILLAS = {
    1: [e_filtro_num, e_filtro_cat, e_count_total, e_count_cat, e_agg, e_top_n, e_distinct,
        e_fecha_anio, e_between, e_like, e_rango_fechas],
    2: [m_join_filtro, m_group_count, m_group_sum, m_group_cat, m_count_cat, m_having_count,
        m_having_avg, m_join3, m_group_anio, m_count_distinct, m_group_filtro_padre],
    3: [h_sub_avg, h_sin_hijos, h_cte_sobre_promedio, h_top1_por_padre, h_acumulado, h_ranking,
        h_datediff, h_mes_top, h_porcentaje, h_max_por_cat, h_sobre_prom_grupo, h_en_subconsulta,
        h_promedio_de_conteos, h_top_padre_cte],
}
REPETICIONES = {1: 6, 2: 5, 3: 5}


def generar(S, semilla=2026):
    """Genera candidatos (sin validar) para un esquema/variante."""
    rng = random.Random(f"{semilla}-{S.id}")
    vistos, salida = set(), []
    for nivel, funcs in PLANTILLAS.items():
        for f in funcs:
            logrados, intentos = 0, 0
            while logrados < REPETICIONES[nivel] and intentos < 40:
                intentos += 1
                try:
                    r = f(S, rng)
                except (IndexError, ValueError):
                    r = None
                if not r or r["sql"] in vistos:
                    continue
                vistos.add(r["sql"])
                r.update(esquema_id=S.id, plantilla=f.__name__)
                salida.append(r)
                logrados += 1
    return salida
