@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Python suchen: nur nehmen, was auch wirklich startet
rem (der Starter "py" kann ohne installiertes Python vorhanden sein,
rem "python" kann der Platzhalter aus dem Microsoft Store sein)
set PY=
py -3 -c "import sys" >nul 2>nul && set PY=py -3
if not defined PY (python -c "import sys" >nul 2>nul && set PY=python)
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
%PY% aktualisieren.py %*
echo.
pause
