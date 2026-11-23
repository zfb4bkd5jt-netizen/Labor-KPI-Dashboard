@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PY=
where py >nul 2>nul && set PY=py -3
if not defined PY (where python >nul 2>nul && set PY=python)
if not defined PY (
  echo Python wurde auf diesem Rechner nicht gefunden.
  echo Bitte Python 3.9 oder neuer installieren ^(python.org oder ueber die IT^)
  echo und danach einmalig ausfuehren:   pip install pandas openpyxl
  echo.
  echo Das Dashboard laesst sich auch ohne Python oeffnen ^(Labor-KPI-Dashboard.html^),
  echo zeigt dann aber den Stand der zuletzt erzeugten Daten.
  echo.
  pause
  exit /b 1
)
start "" "Labor-KPI-Dashboard.html"
%PY% aktualisieren.py --ueberwachen %*
echo.
pause
