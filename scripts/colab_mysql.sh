#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
trap 'echo "Error al preparar MySQL (linea $LINENO)." >&2' ERR
RUNTIME=/content/mysql-p3
BASE="$RUNTIME/mysql-8.4.10"
mkdir -p "$RUNTIME" /tmp/my8run
if [ ! -x "$BASE/bin/mysqld" ]; then
  echo '[1/5] Instalando dependencias de MySQL'
  APT_OPCIONES=(-o Acquire::Retries=2 -o Acquire::http::Timeout=30 -o Acquire::https::Timeout=30)
  apt-get "${APT_OPCIONES[@]}" update -qq < /dev/null
  apt-get "${APT_OPCIONES[@]}" install -y -qq libnuma1 xz-utils wget < /dev/null
  apt-get "${APT_OPCIONES[@]}" install -y -qq libaio1 < /dev/null || apt-get "${APT_OPCIONES[@]}" install -y -qq libaio1t64 < /dev/null
  echo '[2/5] Descargando MySQL 8.4.10 (73 MiB)'
  wget --timeout=30 --tries=2 --progress=dot:giga https://cdn.mysql.com/archives/mysql-8.4/mysql-8.4.10-linux-glibc2.17-x86_64-minimal.tar.xz -O "$RUNTIME/mysql.tar.xz.part"
  xz -t "$RUNTIME/mysql.tar.xz.part"
  mv "$RUNTIME/mysql.tar.xz.part" "$RUNTIME/mysql.tar.xz"
  echo '[3/5] Extrayendo MySQL'
  mkdir -p "$BASE"
  tar xf "$RUNTIME/mysql.tar.xz" -C "$BASE" --strip-components=1
else
  echo '[1-3/5] Binarios de MySQL disponibles'
fi
AIO=$(find /usr/lib /lib -name 'libaio.so.1t64' -print -quit 2>/dev/null || true)
if [ -n "$AIO" ]; then ln -sf "$AIO" "$BASE/lib/libaio.so.1"; fi
export LD_LIBRARY_PATH="$BASE/lib:${LD_LIBRARY_PATH:-}"
if [ ! -d "$RUNTIME/data/mysql" ]; then
  echo '[4/5] Inicializando MySQL'
  "$BASE/bin/mysqld" --no-defaults --initialize-insecure --user=root --basedir="$BASE" --datadir="$RUNTIME/data"
fi
echo '[5/5] Comprobando el servidor MySQL'
if ! MYSQL_SOCKET=/tmp/my8run/mysql.sock python -c 'from generador.bd import conectar; c=conectar(); c.close()' 2>/dev/null; then
  nohup "$BASE/bin/mysqld" --no-defaults --user=root --basedir="$BASE" --datadir="$RUNTIME/data" --socket=/tmp/my8run/mysql.sock --bind-address=127.0.0.1 --port=3306 --mysqlx=OFF > "$RUNTIME/mysql.log" 2>&1 < /dev/null &
fi
for i in $(seq 1 60); do
  if MYSQL_SOCKET=/tmp/my8run/mysql.sock python -c 'from generador.bd import conectar; c=conectar(); q=c.cursor(); q.execute("SELECT VERSION()"); assert q.fetchone()[0].startswith("8.4.10"); c.close()' 2>/dev/null; then
    echo 'MySQL 8.4.10 disponible en /tmp/my8run/mysql.sock'
    exit 0
  fi
  sleep 1
done
echo 'MySQL no respondio dentro del tiempo de espera.' >&2
if [ -f "$RUNTIME/mysql.log" ]; then cat "$RUNTIME/mysql.log"; fi
exit 1
