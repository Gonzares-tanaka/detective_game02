@echo off
cd /d "%~dp0"
echo Open http://localhost:8000/ - Ctrl+C to stop.
".venv\Scripts\python.exe" -B -m http.server 8000 --bind 0.0.0.0 --directory web
if errorlevel 1 pause
