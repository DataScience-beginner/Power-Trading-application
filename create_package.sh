#!/bin/bash

# Script to create a distributable ZIP package for co-founder

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        Creating Portable Package for Co-Founder              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Set package name with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="PowerTradingDashboard_${TIMESTAMP}.zip"

echo "📦 Package name: $PACKAGE_NAME"
echo ""
echo "Including:"

# Create temporary directory for clean packaging
TEMP_DIR="power_trading_package"
rm -rf "$TEMP_DIR" 2>/dev/null
mkdir -p "$TEMP_DIR"

# Copy essential files
echo "  ✓ Application code..."
cp -r api database parsers schemas templates "$TEMP_DIR/" 2>/dev/null
cp -r frontend-react "$TEMP_DIR/" 2>/dev/null

# Copy configuration files
echo "  ✓ Configuration files..."
cp requirements.txt "$TEMP_DIR/" 2>/dev/null
cp init_database.py "$TEMP_DIR/" 2>/dev/null
cp upload_mock_reports.py "$TEMP_DIR/" 2>/dev/null
cp generate_mock_reports.py "$TEMP_DIR/" 2>/dev/null

# Copy scripts
echo "  ✓ Setup scripts..."
cp bootstrap.sh "$TEMP_DIR/" 2>/dev/null
cp bootstrap.bat "$TEMP_DIR/" 2>/dev/null
cp shutdown.sh "$TEMP_DIR/" 2>/dev/null
chmod +x "$TEMP_DIR/bootstrap.sh" 2>/dev/null
chmod +x "$TEMP_DIR/shutdown.sh" 2>/dev/null

# Copy documentation
echo "  ✓ Documentation..."
cp README_FOR_COFOUNDER.md "$TEMP_DIR/README.md" 2>/dev/null
cp SETUP_INSTRUCTIONS.md "$TEMP_DIR/" 2>/dev/null
cp DEPLOYMENT_GUIDE.md "$TEMP_DIR/" 2>/dev/null
cp PROJECT_SUMMARY.md "$TEMP_DIR/" 2>/dev/null

# Copy sample data
echo "  ✓ Sample data..."
mkdir -p "$TEMP_DIR/Data"
cp -r Data/mock_reports "$TEMP_DIR/Data/" 2>/dev/null

# Clean up node_modules and cache files to reduce size
echo "  ✓ Cleaning up unnecessary files..."
rm -rf "$TEMP_DIR/frontend-react/node_modules" 2>/dev/null
rm -rf "$TEMP_DIR/frontend-react/dist" 2>/dev/null
rm -rf "$TEMP_DIR/**/__pycache__" 2>/dev/null
rm -rf "$TEMP_DIR/**/*.pyc" 2>/dev/null
find "$TEMP_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find "$TEMP_DIR" -name "*.pyc" -delete 2>/dev/null
find "$TEMP_DIR" -name ".DS_Store" -delete 2>/dev/null

# Create README in package root
cat > "$TEMP_DIR/START_HERE.txt" << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           POWER TRADING DASHBOARD - QUICK START              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

PREREQUISITES (Install these first):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Python 3.8 or higher
   Download: https://www.python.org/downloads/
   ✅ Check "Add Python to PATH" during installation

2. Node.js 16 or higher (LTS version)
   Download: https://nodejs.org/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK START:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

macOS/Linux:
  1. Open terminal in this folder
  2. Run: ./bootstrap.sh
  3. Open browser: http://localhost:3000

Windows:
  1. Double-click "bootstrap.bat"
  2. Wait for setup to complete
  3. Browser opens automatically at http://localhost:3000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT YOU'LL SEE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Dashboard with transaction analytics
✓ Energy Schedule (Hourly/Daily/Weekly/Monthly views)
✓ Market Analysis with interactive charts
✓ PDF/Excel report downloads

Sample data included:
- 2,072 transactions (Jan 1-15, 2026)
- Client: Mellbro Sugars Pvt Ltd
- Markets: GDAM, DAM, RTM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Read: README.md (detailed instructions)
      SETUP_INSTRUCTIONS.md (troubleshooting)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENJOY! 🚀
EOF

# Create ZIP file
echo ""
echo "Creating ZIP archive..."
cd "$TEMP_DIR" || exit 1
zip -r "../$PACKAGE_NAME" . -q
cd ..

# Clean up temp directory
rm -rf "$TEMP_DIR"

# Get file size
SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                     ✅ PACKAGE CREATED!                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 File: $PACKAGE_NAME"
echo "📊 Size: $SIZE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📧 SEND THIS ZIP FILE TO YOUR CO-FOUNDER"
echo ""
echo "What's included:"
echo "  ✓ Complete application (backend + frontend)"
echo "  ✓ One-click setup scripts (bootstrap.sh/bat)"
echo "  ✓ Sample data (2,072 transactions)"
echo "  ✓ Documentation (README + guides)"
echo "  ✓ Everything needed to run locally"
echo ""
echo "Your co-founder can:"
echo "  1. Extract the ZIP file"
echo "  2. Run bootstrap script"
echo "  3. Start testing immediately"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Share via:"
echo "   • Email (if < 25 MB)"
echo "   • Google Drive / Dropbox / OneDrive"
echo "   • WeTransfer (wetransfer.com)"
echo "   • File.io (file.io)"
echo ""
echo "No cloud hosting needed! Runs 100% locally. 🚀"
echo ""
