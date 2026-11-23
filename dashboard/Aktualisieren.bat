@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Python suchen: zuerst das mitgelieferte im Unterordner python (Offline-Paket),
rem sonst ein installiertes - aber nur, wenn es auch wirklich startet
rem (der Starter "py" kann ohne installiertes Python vorhanden sein,
rem "python" kann der Platzhalter aus dem Microsoft Store sein)
set PY=
if exist "%~dp0python\python.exe" set PY="%~dp0python\python.exe" -E -s
if not defined PY (py -3 -c "import sys" >nul 2>nul && set PY=py -3)
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
