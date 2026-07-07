@echo off
setlocal

REM Power Trading Desktop App Launcher

cd /d "%~dp0"

if /I "%~1"=="--check" goto :check

echo ==============================================
echo   Power Trading Desktop App Launcher
echo ==============================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Using Python: %PYTHON_EXE%
echo Starting desktop app...
echo.
"%PYTHON_EXE%" "desktop-app\run.py"
if errorlevel 1 (
    echo.
    echo Desktop app exited with an error.
    pause
    exit /b 1
)

exit /b 0

:check
echo Running desktop app smoke checks...
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -m py_compile "desktop-app\main.py" "desktop-app\run.py"
if errorlevel 1 (
    echo Syntax check failed.
    exit /b 1
)

echo Syntax check passed.
exit /b 0
