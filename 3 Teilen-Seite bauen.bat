@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Baue die Teilen-Seite...
echo.
python teilen.py
if errorlevel 1 (
  echo.
  echo Fehler. Ist Python installiert? Siehe ANLEITUNG.md, letzter Abschnitt.
)
echo.
pause
