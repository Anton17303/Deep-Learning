"""Conexión a MySQL. Variables de entorno: MYSQL_HOST, MYSQL_PORT, MYSQL_USER,
MYSQL_PASSWORD, MYSQL_SOCKET (si se define, se usa el socket)."""
import os
import pymysql


def conectar(base=None, autocommit=True):
    kw = dict(user=os.environ.get("MYSQL_USER", "root"),
              password=os.environ.get("MYSQL_PASSWORD", ""),
              database=base, autocommit=autocommit, charset="utf8mb4",
              cursorclass=pymysql.cursors.Cursor)
    sock = os.environ.get("MYSQL_SOCKET")
    if sock:
        kw["unix_socket"] = sock
    else:
        kw["host"] = os.environ.get("MYSQL_HOST", "127.0.0.1")
        kw["port"] = int(os.environ.get("MYSQL_PORT", "3306"))
    kw.update(connect_timeout=10, read_timeout=35, write_timeout=35)
    return pymysql.connect(**kw)
