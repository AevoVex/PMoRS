param(
    [ValidateSet('yatube', 'kittygram', 'lessons')][string]$Project = 'yatube'
)
$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    $pythonPath = Join-Path (Split-Path $PSScriptRoot -Parent) '.venv-drf\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create the virtual environment as described in README.md.' }
$projectFolder = if ($Project -eq 'lessons') { 'kittygram' } else { $Project }
$port = switch ($Project) { 'yatube' { 8000 } 'kittygram' { 8001 } 'lessons' { 8002 } }
$extraArgs = if ($Project -eq 'lessons') { @('--settings=config.lesson_settings') } else { @() }
Push-Location (Join-Path $PSScriptRoot $projectFolder)
try {
    & $pythonPath manage.py migrate @extraArgs
    if ($LASTEXITCODE -ne 0) { throw 'Migration failed.' }
    & $pythonPath manage.py runserver "127.0.0.1:$port" @extraArgs
} finally {
    Pop-Location
}
