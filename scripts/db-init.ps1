# 数据库初始化脚本（Windows PowerShell）
# 用法：powershell -ExecutionPolicy Bypass -File scripts\db-init.ps1 [-Proxy http://127.0.0.1:7890]
# 本机（schannel 故障环境）pip 需走代理；其他机器可省略 -Proxy。
param([string]$Proxy = "")

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "==> 创建虚拟环境 .venv"
    python -m venv .venv
}

$pipArgs = @("install", "-e", "apps/api[akshare,dev]")
if ($Proxy) { $pipArgs += @("--proxy", $Proxy) }
Write-Host "==> 安装依赖（editable）"
& ".\.venv\Scripts\python.exe" -m pip @pipArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Alembic 迁移 upgrade head（数据库默认 storage/db/ashare_review.db）"
& ".\.venv\Scripts\alembic.exe" -c apps/api/alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> 完成。可运行测试：.\.venv\Scripts\python.exe -m pytest apps/api -v"
