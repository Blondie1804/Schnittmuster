@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Lese den Schnittmuster-Ordner neu ein...
echo.
python scan.py
if errorlevel 1 (
  echo.
  echo Fehler. Ist Python installiert? Siehe ANLEITUNG.md, letzter Abschnitt.
)
echo.
pause
