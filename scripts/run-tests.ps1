# 运行数据层测试（Windows PowerShell；默认离线，排除 smoke）
param(
    [string]$Extra = "",
    [switch]$Smoke
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "未找到 .venv，请先运行 scripts\db-init.ps1"
    exit 1
}

$args = @("-m", "pytest", "apps/api", "-v")
if ($Smoke) { $args = @("-m", "pytest", "apps/api", "-m", "smoke", "-v") }
if ($Extra) { $args += $Extra.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries) }

& ".\.venv\Scripts\python.exe" @args
exit $LASTEXITCODE
