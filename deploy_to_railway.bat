@echo off
REM Script to commit changes and push to Railway

echo ========================================
echo Deploying latest code to Railway
echo ========================================

echo.
echo Step 1: Adding all changes to git...
git add .

echo.
echo Step 2: Committing changes...
git commit -m "Fix: Updated dashboard analytics, energy schedule data, and API endpoints"

echo.
echo Step 3: Pushing to GitHub (will trigger Railway auto-deploy)...
git push origin main

echo.
echo ========================================
echo DONE!
echo ========================================
echo.
echo Railway should now auto-deploy the latest code.
echo Check Railway dashboard: https://railway.app/dashboard
echo.
echo After deployment completes:
echo 1. Run: python clean_railway_database.py (to clear old data)
echo 2. Run: python populate_energy_schedule_data.py (to add energy schedule data)
echo 3. Hard refresh browser (Ctrl+Shift+R) at your Railway URL
echo.
pause
