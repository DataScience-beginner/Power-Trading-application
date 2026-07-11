#!/bin/bash

# Simple package creator - no input needed
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="PowerTradingDashboard_${TIMESTAMP}.zip"

echo "================================================"
echo "  Creating Package for Co-Founder"
echo "================================================"
echo ""

# Create temp directory
TEMP_DIR="/tmp/power_trading_package"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

echo "✓ Copying application files..."

# Copy all necessary files
cp -r api $TEMP_DIR/
cp -r database $TEMP_DIR/
cp -r parsers $TEMP_DIR/
cp -r schemas $TEMP_DIR/
cp -r frontend-react $TEMP_DIR/

# Copy Python scripts
cp *.py $TEMP_DIR/ 2>/dev/null || true
cp requirements.txt $TEMP_DIR/

# Copy bootstrap scripts
cp bootstrap.sh $TEMP_DIR/
cp bootstrap.bat $TEMP_DIR/
cp README_FOR_COFOUNDER.md $TEMP_DIR/

# Remove unnecessary files
echo "✓ Cleaning up..."
find $TEMP_DIR -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find $TEMP_DIR -name "*.pyc" -delete 2>/dev/null
find $TEMP_DIR -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null
find $TEMP_DIR -name ".git" -type d -exec rm -rf {} + 2>/dev/null
rm -f $TEMP_DIR/*.db 2>/dev/null
rm -f $TEMP_DIR/*.log 2>/dev/null

# Create zip
echo "✓ Creating ZIP file..."
cd /tmp
zip -r $PACKAGE_NAME power_trading_package/ -q

# Move to workspace
mv $PACKAGE_NAME /workspaces/Power-Trading-application/

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo "================================================"
echo "  ✅ PACKAGE CREATED SUCCESSFULLY!"
echo "================================================"
echo ""
echo "📦 File: $PACKAGE_NAME"
echo "📍 Location: /workspaces/Power-Trading-application/"
echo ""
ls -lh /workspaces/Power-Trading-application/$PACKAGE_NAME
echo ""
echo "📧 Send this ZIP file to your co-founder!"
echo ""
echo "Instructions for co-founder:"
echo "1. Extract the ZIP file"
echo "2. Open terminal in extracted folder"
echo "3. Run: ./bootstrap.sh (Linux/Mac) or bootstrap.bat (Windows)"
echo "4. Access dashboard at http://localhost:3000"
echo ""

