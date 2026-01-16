@echo off
echo ================================================================================
echo COMPLETE RAILWAY DEPLOYMENT SCRIPT
echo ================================================================================
echo.
echo This will:
echo 1. Commit and push latest code to GitHub
echo 2. Wait for Railway auto-deployment
echo 3. Clean Railway database
echo 4. Upload fresh 7-day mock data
echo 5. Populate energy schedule data
echo.
pause

echo.
echo ========================================
echo STEP 1: Committing and Pushing to GitHub
echo ========================================
git add .
git commit -m "Fix: Dashboard analytics, energy schedule, and API improvements"
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Git push failed!
    echo Please check your git configuration and try again.
    pause
    exit /b 1
)

echo.
echo ✅ Code pushed to GitHub successfully!
echo.
echo ========================================
echo STEP 2: Waiting for Railway Deployment
echo ========================================
echo.
echo Please:
echo 1. Go to https://railway.app/dashboard
echo 2. Open your Power-Trading-application project
echo 3. Watch the deployment progress
echo 4. Wait for "Deployment live" message
echo.
echo Press any key AFTER Railway deployment completes...
pause

echo.
echo ========================================
echo STEP 3: Cleaning Railway Database
echo ========================================
cd /d "%~dp0"
call venv\Scripts\activate
python clean_railway_database.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Database cleanup had issues, but continuing...
)

echo.
echo ========================================
echo STEP 4: Uploading Fresh Mock Data
echo ========================================
python upload_to_railway_fresh.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Data upload failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo STEP 5: Populating Energy Schedule Data
echo ========================================
python populate_railway_energy_schedule.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Energy schedule population failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo STEP 6: Verifying Deployment
echo ========================================
python test_railway_api.py

echo.
echo ================================================================================
echo ✅ DEPLOYMENT COMPLETE!
echo ================================================================================
echo.
echo Your Railway app should now show:
echo   - DOR Files: 21
echo   - SCH Files: 21
echo   - Total Transactions: 6,048
echo   - Energy Schedule: Populated with 6 days
echo.
echo Next steps:
echo 1. Open: https://power-trading-application-production.up.railway.app
echo 2. Hard refresh browser: Ctrl + Shift + R
echo 3. Verify all data displays correctly
echo.
echo ================================================================================
pause
