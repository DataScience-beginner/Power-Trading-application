#!/bin/bash

# Stop all servers script

echo "Stopping Power Trading Application servers..."

# Stop backend
BACKEND_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
    echo "✅ Backend server stopped"
else
    echo "ℹ️  Backend not running"
fi

# Stop frontend  
FRONTEND_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Frontend server stopped"
else
    echo "ℹ️  Frontend not running"
fi

# Clean up pid files
rm -f server.pid frontend-react/vite.log 2>/dev/null

echo ""
echo "All servers stopped."
