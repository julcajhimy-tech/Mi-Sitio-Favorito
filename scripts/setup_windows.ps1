# Ejecutar una sola vez desde la terminal de VS Code (PowerShell).
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "Instalación terminada. Edita .env, luego ejecuta: python scripts/create_users.py"
