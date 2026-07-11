#!/bin/bash
# Start the Power Trading Application Server

echo "=========================================="
echo "⚡ POWER TRADING APPLICATION SERVER"
echo "=========================================="
echo ""

# Check if running in background or foreground
MODE=${1:-"foreground"}

if [ "$MODE" == "background" ] || [ "$MODE" == "-b" ]; then
    echo "🚀 Starting server in background mode..."
    echo ""
    nohup python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
    echo $! > server.pid
    echo "✅ Server started in background (PID: $(cat server.pid))"
    echo "📝 Logs: tail -f server.log"
    echo "🌐 Access at: http://localhost:8000"
    echo ""
    echo "To stop: ./stop_server.sh"
else
    echo "🚀 Starting server in foreground mode..."
    echo ""
    echo "🌐 Web UI will be available at:"
    echo "   http://localhost:8000"
    echo ""
    echo "📚 API Documentation:"
    echo "   http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    echo "=========================================="
    echo ""
    
    python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
fi
