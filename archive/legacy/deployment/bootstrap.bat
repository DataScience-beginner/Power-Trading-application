@echo off
REM Power Trading Application - Windows Bootstrap Script

echo ===============================================================
echo.
echo      POWER TRADING APPLICATION - AUTO SETUP (WINDOWS)
echo.
echo ===============================================================
echo.
echo This will automatically:
echo   - Check/install Python dependencies
echo   - Check/install Node.js dependencies  
echo   - Initialize database with sample data
echo   - Start backend API server (port 8000)
echo   - Start frontend dashboard (port 3000)
echo.
echo Press Ctrl+C to cancel, or wait 3 seconds to continue...
timeout /t 3 /nobreak > nul
echo.

REM Step 1: Check Python
echo [Step 1/6] Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
echo SUCCESS: Python found
echo.

REM Step 2: Install Python dependencies
echo [Step 2/6] Installing Python dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt --quiet --disable-pip-version-check
    echo SUCCESS: Python packages installed
) else (
    echo WARNING: requirements.txt not found
)
echo.

REM Step 3: Check Node.js
echo [Step 3/6] Checking Node.js installation...
node --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)
echo SUCCESS: Node.js found
echo.

REM Step 4: Install Node.js dependencies
echo [Step 4/6] Installing frontend dependencies...
cd frontend-react
if exist package.json (
    call npm install --silent > nul 2>&1
    echo SUCCESS: Frontend packages installed
) else (
    echo ERROR: package.json not found
    pause
    exit /b 1
)
cd ..
echo.

REM Step 5: Initialize Database
echo [Step 5/6] Setting up database...
if not exist power_trading.db (
    echo Creating new database...
    python init_database.py > nul 2>&1
    echo SUCCESS: Database initialized
    
    if exist upload_mock_reports.py (
        echo Loading sample data (2,072 transactions)...
        python upload_mock_reports.py > nul 2>&1
        echo SUCCESS: Sample data loaded
    )
) else (
    echo SUCCESS: Database already exists
)
echo.

REM Step 6: Start servers
echo [Step 6/6] Starting application servers...
echo.

REM Kill any existing processes (optional, might fail on Windows)
echo Starting Backend API (FastAPI)...
start /B python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1
timeout /t 3 /nobreak > nul
echo SUCCESS: Backend running on http://localhost:8000
echo.

echo Starting Frontend Dashboard (React + Vite)...
cd frontend-react
start /B npm run dev > ..\frontend.log 2>&1
cd ..
timeout /t 5 /nobreak > nul
echo SUCCESS: Frontend running on http://localhost:3000
echo.

echo ===============================================================
echo.
echo                    APPLICATION IS READY!
echo.
echo ===============================================================
echo.
echo Open your browser and go to:
echo.
echo    http://localhost:3000
echo.
echo ===============================================================
echo.
echo What to test:
echo   * Dashboard - View statistics and transaction data
echo   * Energy Schedule - Hourly/Daily/Weekly/Monthly views
echo   * Analytics - Market trends and charts
echo   * Reports - Download PDF/Excel reports
echo.
echo Sample Data:
echo   * Client: Mellbro Sugars Pvt Ltd
echo   * Transactions: 2,072 records
echo   * Date Range: January 1-15, 2026
echo.
echo ===============================================================
echo.
echo To stop: Close this window or press Ctrl+C
echo.
echo Server logs available in:
echo   - backend.log
echo   - frontend.log
echo.
pause
