@echo off
setlocal

REM ============================================================
REM   Stylometric Comparison - Deep Scan launcher
REM ============================================================
REM Double-click this file (or run it from any terminal) to:
REM   1. Start the local Flask server in this window
REM   2. Open your default browser to the Deep Scan page
REM
REM The server runs until you close this window or press Ctrl+C.
REM ============================================================

cd /d "%~dp0"

echo ============================================================
echo   Stylometric Comparison - Deep Scan
echo ============================================================
echo.

REM Sanity check: is Python on the PATH?
where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python is not on your PATH.
  echo Install Python 3.10+ from https://python.org and re-run this file.
  echo.
  pause
  exit /b 1
)

REM Sanity check: are we sitting next to app.py?
if not exist "app.py" (
  echo ERROR: app.py not found in this folder.
  echo This .bat file needs to live next to app.py in the project root.
  echo Current folder: %CD%
  echo.
  pause
  exit /b 1
)

echo Starting local server at http://127.0.0.1:5050
echo Your browser will open at /deep-scan in a few seconds.
echo.
echo ============================================================
echo  To stop:  press Ctrl+C in this window, or close it.
echo ============================================================
echo.

REM Open the browser after a short delay so Flask + spaCy have time to load.
start "" cmd /c "timeout /t 5 /nobreak >nul && start http://127.0.0.1:5050/deep-scan"

REM Run the Flask server in the foreground.
python app.py

echo.
echo ============================================================
echo  Server stopped.
echo ============================================================
echo.
pause
