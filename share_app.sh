#!/bin/bash

# Quick Deploy Script for Power Trading Application
# This script sets up the app for sharing via port forwarding

echo "================================================"
echo "  Power Trading App - Quick Share Setup"
echo "================================================"
echo ""

# Check if servers are running
echo "1. Checking if servers are running..."

BACKEND_PID=$(lsof -ti:8000 2>/dev/null)
FRONTEND_PID=$(lsof -ti:3000 2>/dev/null)

if [ -z "$BACKEND_PID" ]; then
    echo "   ⚠️  Backend not running. Starting FastAPI server..."
    cd /workspaces/Power-Trading-application
    nohup uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 & echo $! > server.pid
    sleep 3
    echo "   ✅ Backend started on port 8000"
else
    echo "   ✅ Backend already running on port 8000"
fi

if [ -z "$FRONTEND_PID" ]; then
    echo "   ⚠️  Frontend not running. Starting React dev server..."
    cd /workspaces/Power-Trading-application/frontend-react
    nohup npm run dev > vite.log 2>&1 &
    sleep 5
    echo "   ✅ Frontend started on port 3000"
else
    echo "   ✅ Frontend already running on port 3000"
fi

echo ""
echo "2. Testing endpoints..."
sleep 2

# Test backend
BACKEND_STATUS=$(curl -s http://localhost:8000/api/health | grep -o "healthy" || echo "")
if [ "$BACKEND_STATUS" = "healthy" ]; then
    echo "   ✅ Backend API is healthy"
else
    echo "   ❌ Backend API is not responding"
fi

# Test frontend
FRONTEND_STATUS=$(curl -s http://localhost:3000 | grep -o "Power Trading" || echo "")
if [ "$FRONTEND_STATUS" = "Power Trading" ]; then
    echo "   ✅ Frontend is accessible"
else
    echo "   ❌ Frontend is not responding"
fi

echo ""
echo "================================================"
echo "  🎉 App is Ready for Sharing!"
echo "================================================"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. In VS Code, click the 'PORTS' tab (bottom panel)"
echo ""
echo "2. Find these ports and make them PUBLIC:"
echo "   • Port 3000 (Frontend - React Dashboard)"
echo "   • Port 8000 (Backend - FastAPI)"
echo ""
echo "3. Right-click each port → 'Port Visibility' → 'Public'"
echo ""
echo "4. Copy the 'Forwarded Address' for each:"
echo "   • Frontend URL will be like: https://***-3000.app.github.dev"
echo "   • Backend URL will be like: https://***-8000.app.github.dev"
echo ""
echo "5. Share BOTH URLs with your co-founder"
echo ""
echo "================================================"
echo "  Testing Instructions for Co-Founder"
echo "================================================"
echo ""
echo "📧 Email Template:"
echo ""
echo "---"
echo "Hi [Co-Founder Name],"
echo ""
echo "The Power Trading Dashboard is ready for testing!"
echo ""
echo "🔗 Access the app: [FRONTEND_URL]"
echo ""
echo "Features to test:"
echo "• Dashboard - View transactions and analytics"
echo "• Energy Schedule - Hourly/Daily/Weekly/Monthly views"
echo "• Analytics - Market analysis and charts"
echo "• Reports - Download PDF/Excel reports"
echo ""
echo "Test scenarios:"
echo "1. Select 'Mellbro Sugars Pvt Ltd' from sidebar"
echo "2. Try different view modes (Hourly/Daily/Weekly/Monthly)"
echo "3. Filter by market type (GDAM/DAM/RTM)"
echo "4. Download reports (PDF and Excel)"
echo ""
echo "Current data: Jan 1-15, 2026 (2,072 transactions)"
echo ""
echo "Let me know what you think!"
echo "---"
echo ""
echo "================================================"
echo ""
echo "💡 TIP: Keep this terminal open. Servers will run in background."
echo ""
echo "To stop servers later, run: ./stop_servers.sh"
echo ""
