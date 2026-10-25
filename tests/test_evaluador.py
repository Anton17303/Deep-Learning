import unittest
from decimal import Decimal

from evaluador import categoria_error, coincide
from prompt import es_solo_lectura, extraer_sql, formatear_esquema


class TestCoincide(unittest.TestCase):
    def test_orden_irrelevante(self):
        self.assertTrue(coincide([(2, "b"), (1, "a")], [(1, "a"), (2, "b")], False))

    def test_orden_exigido(self):
        self.assertFalse(coincide([(2, "b"), (1, "a")], [(1, "a"), (2, "b")], True))
        self.assertTrue(coincide([(1, "a"), (2, "b")], [(1, "a"), (2, "b")], True))

    def test_redondeo_dos_decimales(self):
        self.assertTrue(coincide([(Decimal("3.14159"),)], [(3.14,)], False))
        self.assertFalse(coincide([(Decimal("3.19"),)], [(3.14,)], False))

    def test_columna_extra_no_penaliza(self):
        self.assertTrue(coincide([("a", 1, 9), ("b", 2, 8)], [(1,), (2,)], False))
        self.assertTrue(coincide([(9, "a", 1), (8, "b", 2)], [("a", 1), ("b", 2)], False))

    def test_columnas_mal_emparejadas(self):
        # mismos valores por columna pero filas cruzadas -> distinto
        self.assertFalse(coincide([("a", 2), ("b", 1)], [("a", 1), ("b", 2)], False))

    def test_filas_distintas_o_faltan_columnas(self):
        self.assertFalse(coincide([(1,)], [(1,), (2,)], False))
        self.assertFalse(coincide([(1,)], [(1, 2)], False))


class TestCategorias(unittest.TestCase):
    def test_errores_de_ejecucion(self):
        self.assertEqual(categoria_error("x", "y", "(1054, \"Unknown column 'a'\")"), "columna o tabla inexistente")
        self.assertEqual(categoria_error("x", "y", "(1146, \"Table 'b' doesn't exist\")"), "columna o tabla inexistente")
        self.assertEqual(categoria_error("x", "y", "(1064, 'You have an error in your SQL syntax')"), "sintaxis")
        self.assertEqual(categoria_error("x", "y", "(1055, 'ONLY_FULL_GROUP_BY')"), "agregación")

    def test_resultado_distinto(self):
        ref = "SELECT n FROM t JOIN u ON t.a=u.a WHERE x > 3 GROUP BY n"
        self.assertEqual(categoria_error("SELECT n FROM t WHERE x > 3 GROUP BY n", ref, None), "JOIN")
        self.assertEqual(categoria_error("SELECT n FROM t JOIN u ON t.a=u.a WHERE x > 3", ref, None), "agregación")
        self.assertEqual(categoria_error("SELECT n FROM t JOIN u ON t.a=u.a WHERE x > 9 GROUP BY n", ref, None), "filtro")
        self.assertEqual(categoria_error(ref + " ORDER BY n", ref, None), "resultado distinto")


class TestPrompt(unittest.TestCase):
    def test_extraer_sql(self):
        self.assertEqual(extraer_sql("```sql\nSELECT 1;\n```"), "SELECT 1")
        self.assertEqual(extraer_sql("Claro: select a from t; select b from u;"), "select a from t")
        self.assertEqual(extraer_sql("SELECT ';' AS x FROM t"), "SELECT ';' AS x FROM t")

    def test_solo_lectura(self):
        self.assertTrue(es_solo_lectura("WITH a AS (SELECT 1) SELECT * FROM a"))
        self.assertTrue(es_solo_lectura("SELECT REPLACE(nombre,'a','b') AS fecha_update FROM t"))
        self.assertFalse(es_solo_lectura("DELETE FROM t"))
        self.assertFalse(es_solo_lectura("SELECT 1; DROP TABLE t"))
        self.assertFalse(es_solo_lectura("WITH x AS (SELECT 1) UPDATE t SET a=1"))

    def test_formato_compacto(self):
        esq = "CREATE TABLE `t` (\n  `a` int NOT NULL COMMENT 'x',\n  KEY `k` (`a`)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Tabla t';"
        out = formatear_esquema(esq, "compacto")
        self.assertNotIn("ENGINE", out)
        self.assertNotIn("KEY", out)
        self.assertIn("COMMENT='Tabla t'", out)


if __name__ == "__main__":
    unittest.main()
