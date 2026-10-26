param([int]$Port = 3307)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$runtime = Join-Path $root '.runtime'
$base = Join-Path $runtime 'mysql-8.4.10-winx64'
$data = Join-Path $runtime 'mysql-data'
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
if (-not (Test-Path (Join-Path $base 'bin/mysqld.exe'))) {
    $archive = Join-Path $runtime 'mysql-8.4.10-winx64.zip'
    Invoke-WebRequest 'https://downloads.mysql.com/archives/get/p/23/file/mysql-8.4.10-winx64.zip' -OutFile $archive
    Expand-Archive -LiteralPath $archive -DestinationPath $runtime -Force
}
if (-not (Test-Path (Join-Path $data 'mysql'))) {
    & "$base/bin/mysqld.exe" --no-defaults --initialize-insecure "--basedir=$base" "--datadir=$data" --console
    if ($LASTEXITCODE -ne 0) { throw 'Falló la inicialización de MySQL' }
}
$env:MYSQL_HOST = '127.0.0.1'
$env:MYSQL_PORT = "$Port"
$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $listener) {
    Start-Process -FilePath "$base/bin/mysqld.exe" -WindowStyle Hidden -ArgumentList @(
        '--no-defaults', "--basedir=`"$base`"", "--datadir=`"$data`"", "--port=$Port",
        '--bind-address=127.0.0.1', '--mysqlx=OFF', '--console'
    ) -RedirectStandardOutput (Join-Path $runtime 'mysql.stdout.log') -RedirectStandardError (Join-Path $runtime 'mysql.stderr.log')
}
Write-Output "MySQL: 127.0.0.1:$Port"
