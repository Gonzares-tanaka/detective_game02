@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -B -X utf8 -m unittest discover -s tests -v
if errorlevel 1 (
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -B -X utf8 tools\verify_release.py
if errorlevel 1 pause
