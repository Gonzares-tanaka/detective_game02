@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" -B -X utf8 tools\build_release.py
if errorlevel 1 pause
