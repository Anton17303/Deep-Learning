#!/usr/bin/env bash
set -euo pipefail
RUNTIME=/content/mysql-p3
BASE="$RUNTIME/mysql-8.4.10"
mkdir -p "$RUNTIME" /tmp/my8run
if [ ! -x "$BASE/bin/mysqld" ]; then
  apt-get update -qq
  apt-get install -y -qq libnuma1 xz-utils wget
  apt-get install -y -qq libaio1 || apt-get install -y -qq libaio1t64
  wget -q https://downloads.mysql.com/archives/get/p/23/file/mysql-8.4.10-linux-glibc2.17-x86_64-minimal.tar.xz -O "$RUNTIME/mysql.tar.xz"
  mkdir -p "$BASE"
  tar xf "$RUNTIME/mysql.tar.xz" -C "$BASE" --strip-components=1
fi
AIO=$(find /usr/lib /lib -name 'libaio.so.1t64' -print -quit 2>/dev/null || true)
if [ -n "$AIO" ]; then ln -sf "$AIO" "$BASE/lib/libaio.so.1"; fi
export LD_LIBRARY_PATH="$BASE/lib:${LD_LIBRARY_PATH:-}"
if [ ! -d "$RUNTIME/data/mysql" ]; then
  "$BASE/bin/mysqld" --no-defaults --initialize-insecure --user=root --basedir="$BASE" --datadir="$RUNTIME/data"
fi
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
cat "$RUNTIME/mysql.log"
exit 1
