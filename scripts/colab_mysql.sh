#!/bin/bash
# Instala y arranca MySQL 8.4.10 (binario Linux del enunciado) en Colab/Kaggle.
# NOTA: no pude probar este script (sin acceso a downloads.mysql.com desde mi entorno). Si falla,
# usar la alternativa: apt-get install -y mysql-server  (será 8.0.x; ver README, sección Motor).
set -e
cd /content 2>/dev/null || cd ~
apt-get install -y -qq libaio1 libnuma1 >/dev/null
URL=https://downloads.mysql.com/archives/get/p/23/file/mysql-8.4.10-linux-glibc2.17-x86_64-minimal.tar.xz
[ -d mysql-8.4.10 ] || { wget -q "$URL" -O mysql.tar.xz && mkdir mysql-8.4.10 && tar xf mysql.tar.xz -C mysql-8.4.10 --strip-components=1; }
mkdir -p /tmp/my8data /tmp/my8run
if [ ! -d /tmp/my8data/mysql ]; then
  mysql-8.4.10/bin/mysqld --initialize-insecure --user=root --datadir=/tmp/my8data
fi
setsid nohup mysql-8.4.10/bin/mysqld --user=root --datadir=/tmp/my8data \
  --socket=/tmp/my8run/mysql.sock --port=3306 --bind-address=127.0.0.1 --mysqlx=OFF \
  --secure-file-priv="" > /tmp/mysqld.log 2>&1 < /dev/null &
for i in $(seq 1 60); do [ -S /tmp/my8run/mysql.sock ] && break; sleep 1; done
echo "export MYSQL_SOCKET=/tmp/my8run/mysql.sock"
