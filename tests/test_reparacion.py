import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

from prompt import es_solo_lectura, extraer_sql, corregir_identificadores


def funcion_controlada(respuestas, ejecutar):
    raiz = Path(__file__).resolve().parents[1]
    arbol = ast.parse((raiz / 'solucion.py').read_text(encoding='utf-8'))
    funcion = next(n for n in arbol.body if isinstance(n, ast.FunctionDef) and n.name == 'generar_sql')
    respuestas = iter(respuestas)
    espacio = dict(time=SimpleNamespace(time=lambda: 0), set_seed=lambda _: None,
                   CFG={'semilla': 2026}, FORMATO_ESQUEMA='show_create', REPARAR=True,
                   MAX_REINTENTOS=2, LIMITE_SEG=25, FALLBACK='SELECT 1',
                   construir_mensajes=lambda *args: [], _ejemplos_fewshot=lambda: [],
                   _generar=lambda *args: next(respuestas), extraer_sql=extraer_sql,
                   corregir_identificadores=corregir_identificadores,
                   es_solo_lectura=es_solo_lectura)
    exec(compile(ast.Module(body=[funcion], type_ignores=[]), 'solucion.py', 'exec'), espacio)
    return espacio['generar_sql']('CREATE TABLE t(nombre TEXT)', 'Devuelve nombre de t.', ejecutar)


class TestReparacion(unittest.TestCase):
    def test_corrige_una_tabla_cercana_sin_tocar_literales(self):
        sql = corregir_identificadores("SELECT nombre FROM HOTELS WHERE nombre = 'HOTELS'",
                                       'CREATE TABLE hoteles (nombre TEXT)')
        self.assertIn('`hoteles`', sql)
        self.assertIn("'HOTELS'", sql)

    def test_conserva_consultas_validas_y_nombres_ambiguos(self):
        esquema = 'CREATE TABLE cliente1 (nombre TEXT); CREATE TABLE cliente2 (nombre TEXT)'
        valida = 'SELECT nombre FROM cliente1'
        ambigua = 'SELECT nombre FROM cliente'
        self.assertEqual(corregir_identificadores(valida, esquema), valida)
        self.assertEqual(corregir_identificadores(ambigua, esquema), ambigua)

    def test_conserva_alias_de_cte(self):
        esquema = 'CREATE TABLE hoteles (nombre TEXT)'
        sql = 'WITH hotels AS (SELECT nombre FROM hoteles) SELECT nombre FROM hotels'
        self.assertEqual(corregir_identificadores(sql, esquema), sql)

    def test_no_ejecuta_una_salida_que_modifica_la_base(self):
        llamadas = []

        def ejecutar(sql):
            llamadas.append(sql)
            return {'ok': True}

        sql = funcion_controlada(['DELETE FROM t', 'SELECT nombre FROM t'], ejecutar)
        self.assertEqual(sql, 'SELECT nombre FROM t')
        self.assertEqual(llamadas, ['SELECT nombre FROM t'])

    def test_respeta_el_maximo_de_llamadas(self):
        llamadas = []

        def ejecutar(sql):
            llamadas.append(sql)
            return {'ok': False, 'error': 'Unknown column'}

        sql = funcion_controlada(['SELECT a FROM t', 'SELECT b FROM t', 'SELECT nombre FROM t'], ejecutar)
        self.assertEqual(len(llamadas), 2)
        self.assertEqual(sql, 'SELECT nombre FROM t')


if __name__ == '__main__':
    unittest.main()
