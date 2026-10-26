import json
import unittest
from pathlib import Path

from prompt import es_solo_lectura, extraer_sql


class TestContrato(unittest.TestCase):
    def test_sentencias_multiples_y_archivos(self):
        for sql in ["SELECT 1; SELECT 2", "SELECT 1 INTO OUTFILE '/tmp/salida'",
                    "WITH x AS (SELECT 1) DELETE FROM t", "SELECT * FROM t FOR UPDATE",
                    "SELECT 1 /*! INTO OUTFILE '/tmp/salida' */"]:
            self.assertFalse(es_solo_lectura(sql), sql)

    def test_comillas_escapadas(self):
        sql = "SELECT 'a\\\';b' AS valor; SELECT 2"
        self.assertEqual(extraer_sql(sql), "SELECT 'a\\\';b' AS valor")
        self.assertEqual(extraer_sql("SELECT 'a'';b' AS valor;"), "SELECT 'a'';b' AS valor")
        self.assertEqual(extraer_sql("SELECT /* ; */ 1; SELECT 2"), "SELECT /* ; */ 1")

    def test_particion_y_cantidad(self):
        raiz = Path(__file__).resolve().parents[1]
        leer = lambda p: [json.loads(l) for l in (raiz / p).read_text(encoding='utf-8').splitlines() if l]
        train, val = leer('datos/entrenamiento.jsonl'), leer('datos/validacion/preguntas.jsonl')
        self.assertGreaterEqual(len(train), 2000)
        self.assertEqual(len(val), 40)
        self.assertFalse({r['esquema_id'] for r in train} & {r['esquema_id'] for r in val})
        self.assertFalse({r['esquema_id'].rsplit('_', 1)[0] for r in train} &
                         {r['esquema_id'].rsplit('_', 1)[0] for r in val})
        self.assertEqual({r['nivel'] for r in val}, {1, 2, 3})

    def test_un_solo_factor_lora(self):
        raiz = Path(__file__).resolve().parents[1] / 'configuraciones'
        a, b = [json.loads((raiz / n).read_text()) for n in ['lora_r8.json', 'lora_r16.json']]
        diferencias = {k for k in a if a[k] != b[k]} - {'nombre'}
        self.assertEqual(diferencias, {'r'})


if __name__ == '__main__':
    unittest.main()
