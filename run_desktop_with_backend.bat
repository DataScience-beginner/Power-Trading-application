@echo off
setlocal EnableDelayedExpansion

REM One-click launcher: start backend, wait for health, then launch desktop app

cd /d "%~dp0"

if /I "%~1"=="--check" goto :check
if /I "%~1"=="--keep-backend" (
    set "KEEP_BACKEND=1"
) else (
    set "KEEP_BACKEND=0"
)

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo ==============================================
echo   Power Trading Desktop + Backend Launcher
echo ==============================================
echo.
echo Using Python: %PYTHON_EXE%

set "SERVER_URL=http://127.0.0.1:8000/api/health"
set "STARTED_SERVER=0"
set "WAIT_SECONDS=45"

echo Checking backend health...
call :health_check
if %ERRORLEVEL% EQU 0 (
    echo Backend already running.
) else (
    echo Starting backend server...
    start "PowerTradingBackend" /B "%PYTHON_EXE%" -m uvicorn api.main:app --host 127.0.0.1 --port 8000
    set "STARTED_SERVER=1"
)

echo Waiting for backend readiness...
for /L %%i in (1,1,%WAIT_SECONDS%) do (
    call :health_check
    if !ERRORLEVEL! EQU 0 (
        echo Backend is ready.
        goto :launch_desktop
    )
    timeout /t 1 /nobreak > nul
)

echo ERROR: Backend did not become ready within %WAIT_SECONDS% seconds.
goto :cleanup_error

:launch_desktop
echo Launching desktop app...
"%PYTHON_EXE%" "desktop-app\run.py"
set "APP_EXIT=%ERRORLEVEL%"

if %KEEP_BACKEND% EQU 1 (
    echo Keeping backend running because --keep-backend was provided.
    exit /b %APP_EXIT%
)

if %STARTED_SERVER% EQU 1 (
    echo Stopping backend started by this launcher...
    call :stop_backend
)

exit /b %APP_EXIT%

:cleanup_error
if %STARTED_SERVER% EQU 1 (
    call :stop_backend
)
exit /b 1

:health_check
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%SERVER_URL%'; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" > nul 2>&1
exit /b %ERRORLEVEL%

:stop_backend
for /f "tokens=2 delims=," %%p in ('tasklist /FI "WINDOWTITLE eq PowerTradingBackend" /FO CSV /NH') do (
    taskkill /F /PID %%~p > nul 2>&1
)

REM Fallback: kill uvicorn processes on 127.0.0.1:8000
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%p > nul 2>&1
)
exit /b 0

:check
echo Running launcher checks...
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -m py_compile "api\main.py" "desktop-app\main.py" "desktop-app\run.py"
if errorlevel 1 (
    echo Syntax check failed.
    exit /b 1
)

echo Syntax check passed.
exit /b 0
