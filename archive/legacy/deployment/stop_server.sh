#!/bin/bash
# Stop the Power Trading Application Server

if [ -f server.pid ]; then
    PID=$(cat server.pid)
    echo "🛑 Stopping server (PID: $PID)..."
    kill $PID 2>/dev/null
    rm server.pid
    echo "✅ Server stopped"
else
    echo "❌ No server PID file found"
    echo "Server may not be running or was started in foreground mode"
fi
