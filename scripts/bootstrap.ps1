param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "Using interpreter: $Python"
& $Python -c "import sys; print(sys.executable); print(sys.version)"
if ($LASTEXITCODE -ne 0) {
    throw "Python interpreter failed. Install a supported Python and pass it with -Python."
}

if (!(Test-Path ".venv")) {
    & $Python -m venv .venv
}

$VenvPython = ".\.venv\Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip setuptools wheel
& $VenvPython -m pip install -r requirements.txt
& $VenvPython -m scripts.check_environment

Write-Host "Next commands:"
Write-Host "$VenvPython -m pytest"
Write-Host "$VenvPython -m scripts.run_sql_eval"
