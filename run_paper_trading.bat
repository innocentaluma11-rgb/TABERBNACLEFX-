@echo off
setlocal
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Create the environment first with: python -m venv .venv
  exit /b 1
)
if not exist .env (
  echo Copy .env.example to .env and configure paper-trading settings first.
  exit /b 1
)
.venv\Scripts\python.exe scheduler.py --symbol EURUSD --interval 5
endlocal
