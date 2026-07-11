#!/bin/bash

# Get shareable URLs from GitHub Codespaces

echo "================================================"
echo "  📋 SHAREABLE URLS FOR YOUR CO-FOUNDER"
echo "================================================"
echo ""

# Try to detect codespace URL
if [ ! -z "$CODESPACE_NAME" ]; then
    CODESPACE_DOMAIN="${CODESPACE_NAME}.githubpreview.dev"
    
    echo "✅ Detected GitHub Codespace!"
    echo ""
    echo "🌐 FRONTEND (Dashboard):"
    echo "   https://${CODESPACE_NAME}-3000.app.github.dev"
    echo ""
    echo "🔌 BACKEND (API):"
    echo "   https://${CODESPACE_NAME}-8000.app.github.dev"
    echo ""
else
    echo "ℹ️  Not running in Codespace"
    echo ""
    echo "Manual steps:"
    echo "1. Click PORTS tab in VS Code (bottom panel)"
    echo "2. Find ports 3000 and 8000"
    echo "3. Copy the 'Forwarded Address' column"
    echo ""
fi

echo "================================================"
echo "  📧 COPY & PASTE THIS TO YOUR CO-FOUNDER"
echo "================================================"
echo ""
echo "Hi,"
echo ""
echo "Here's the Power Trading Dashboard for testing:"
echo ""

if [ ! -z "$CODESPACE_NAME" ]; then
    echo "🔗 Dashboard: https://${CODESPACE_NAME}-3000.app.github.dev"
else
    echo "🔗 Dashboard: [Get URL from PORTS tab - port 3000]"
fi

echo ""
echo "📱 Test on desktop and mobile browsers"
echo ""
echo "Features available:"
echo "• Dashboard with real-time analytics"
echo "• Energy Schedule (Hourly/Daily/Weekly/Monthly)"
echo "• Market Analysis charts"
echo "• PDF & Excel report downloads"
echo ""
echo "Sample client: Mellbro Sugars Pvt Ltd"
echo "Data: Jan 1-15, 2026 (2,072 transactions)"
echo ""
echo "Let me know your feedback!"
echo ""
echo "================================================"
echo ""

# Check if ports are public
echo "⚠️  IMPORTANT: Make sure ports are PUBLIC"
echo ""
echo "In VS Code:"
echo "1. PORTS tab → Right-click port 3000 → Port Visibility → Public"
echo "2. PORTS tab → Right-click port 8000 → Port Visibility → Public"
echo ""
