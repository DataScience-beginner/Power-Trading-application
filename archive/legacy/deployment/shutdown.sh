#!/bin/bash

# Shutdown script for Power Trading Application

echo "Stopping Power Trading Application..."

# Kill backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo "✓ Backend stopped" || echo "ℹ Backend not running"
    rm backend.pid
fi

# Kill frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo "✓ Frontend stopped" || echo "ℹ Frontend not running"
    rm frontend.pid
fi

# Kill any remaining processes on ports 8000 and 3000
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null && echo "✓ Cleaned up port 8000"
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null && echo "✓ Cleaned up port 3000"

echo ""
echo "Application stopped successfully."
