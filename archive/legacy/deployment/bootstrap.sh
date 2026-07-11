#!/bin/bash

# Power Trading Application - One-Click Bootstrap
# This script sets up and runs the entire application automatically

set -e  # Exit on any error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     POWER TRADING APPLICATION - AUTO SETUP & START           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This will automatically:"
echo "  ✓ Check/install Python dependencies"
echo "  ✓ Check/install Node.js dependencies"
echo "  ✓ Initialize database with sample data"
echo "  ✓ Start backend API server (port 8000)"
echo "  ✓ Start frontend dashboard (port 3000)"
echo ""
echo "Press Ctrl+C to cancel, or wait 3 seconds to continue..."
sleep 3
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Check Python
print_step "Step 1/6: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Step 2: Install Python dependencies
print_step "Step 2/6: Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt --quiet --disable-pip-version-check
    print_success "Python packages installed"
else
    print_warning "requirements.txt not found, skipping..."
fi

# Step 3: Check Node.js
print_step "Step 3/6: Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 16 or higher from https://nodejs.org"
    exit 1
fi

# Step 4: Install Node.js dependencies
print_step "Step 4/6: Installing frontend dependencies..."
cd frontend-react
if [ -f "package.json" ]; then
    npm install --silent > /dev/null 2>&1
    print_success "Frontend packages installed"
else
    print_error "package.json not found"
    exit 1
fi
cd ..

# Step 5: Initialize Database
print_step "Step 5/6: Setting up database..."
if [ ! -f "power_trading.db" ]; then
    print_warning "Database not found. Creating new database..."
    python3 init_database.py > /dev/null 2>&1
    print_success "Database initialized"
    
    # Load sample data
    if [ -f "upload_mock_reports.py" ]; then
        print_step "Loading sample transaction data (2,072 records)..."
        python3 upload_mock_reports.py > /dev/null 2>&1
        print_success "Sample data loaded (Jan 1-15, 2026)"
    fi
else
    print_success "Database already exists"
fi

# Step 6: Start servers
print_step "Step 6/6: Starting application servers..."
echo ""

# Kill any existing servers on these ports
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true

# Start backend
print_step "Starting Backend API (FastAPI)..."
nohup python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
sleep 3

# Check if backend started
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    print_success "Backend running on http://localhost:8000"
else
    print_error "Backend failed to start. Check backend.log for details."
    exit 1
fi

# Start frontend
print_step "Starting Frontend Dashboard (React + Vite)..."
cd frontend-react
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..
sleep 5

# Check if frontend started
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend running on http://localhost:3000"
else
    print_error "Frontend failed to start. Check frontend.log for details."
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                  ✅ APPLICATION IS READY!                     ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🌐 Open your browser and go to:${NC}"
echo ""
echo -e "   ${BLUE}http://localhost:3000${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 What to test:"
echo "   • Dashboard - View statistics and transaction data"
echo "   • Energy Schedule - Hourly/Daily/Weekly/Monthly views"
echo "   • Analytics - Market trends and charts"
echo "   • Reports - Download PDF/Excel reports"
echo ""
echo "📁 Sample Data Available:"
echo "   • Client: Mellbro Sugars Pvt Ltd"
echo "   • Transactions: 2,072 records"
echo "   • Date Range: January 1-15, 2026"
echo "   • Markets: GDAM, DAM, RTM"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🛑 To stop the application:"
echo "   Run: ./shutdown.sh"
echo ""
echo "📝 Server logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "💡 The application will keep running in the background."
echo "   You can close this terminal window safely."
echo ""
