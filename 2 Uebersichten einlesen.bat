@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Lese die Excel-Uebersichten ein...
echo.
python uebersicht_einlesen.py %1
if errorlevel 1 (
  echo.
  echo Fehler. Ist Python installiert? Siehe ANLEITUNG.md.
)
echo.
pause
