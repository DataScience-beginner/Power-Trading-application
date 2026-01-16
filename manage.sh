#!/bin/bash
# Power Trading Application - Management Script

echo "========================================"
echo "⚡ POWER TRADING APPLICATION"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_menu() {
    echo "Select an option:"
    echo ""
    echo "  1) 🎬 Run Demo"
    echo "  2) 📄 Parse Excel File"
    echo "  3) 📊 View Last Parsed Output"
    echo "  4) 📁 List Output Files"
    echo "  5) 🧪 Check Dependencies"
    echo "  6) 📖 View Documentation"
    echo "  7) 🌲 Show Directory Structure"
    echo "  8) ❌ Exit"
    echo ""
    echo -n "Enter choice [1-8]: "
}

while true; do
    show_menu
    read choice
    echo ""
    
    case $choice in
        1)
            echo -e "${BLUE}Running demo...${NC}"
            echo ""
            python demo.py
            ;;
        2)
            echo -n "Enter Excel file path: "
            read filepath
            echo -n "Enter client ID (optional, press Enter to skip): "
            read clientid
            echo ""
            if [ -z "$clientid" ]; then
                python run_parser.py "$filepath"
            else
                python run_parser.py "$filepath" "$clientid"
            fi
            ;;
        3)
            echo -e "${BLUE}Viewing latest parsed output...${NC}"
            echo ""
            latest=$(ls -t output/*.json 2>/dev/null | head -1)
            if [ -z "$latest" ]; then
                echo "❌ No output files found"
            else
                echo "File: $latest"
                echo ""
                python -m json.tool "$latest" | head -50
                echo ""
                echo "... (showing first 50 lines)"
            fi
            ;;
        4)
            echo -e "${BLUE}Output files:${NC}"
            echo ""
            ls -lh output/*.json 2>/dev/null || echo "❌ No output files found"
            ;;
        5)
            echo -e "${BLUE}Checking dependencies...${NC}"
            echo ""
            python -c "import pandas; print('✅ pandas:', pandas.__version__)"
            python -c "import openpyxl; print('✅ openpyxl:', openpyxl.__version__)"
            python -c "import xlrd; print('✅ xlrd:', xlrd.__version__)"
            python -c "import jsonschema; print('✅ jsonschema:', jsonschema.__version__)"
            ;;
        6)
            echo -e "${BLUE}Available documentation:${NC}"
            echo ""
            echo "  📄 SETUP_COMPLETE.md  - Quick reference"
            echo "  📄 README_NEW.md      - Full documentation"
            echo "  📄 PROJECT_SUMMARY.md - Project overview"
            echo "  📄 QUICK_START.md     - Quick start guide"
            echo ""
            echo -n "View which file? (filename or press Enter to skip): "
            read docfile
            if [ -n "$docfile" ]; then
                if [ -f "$docfile" ]; then
                    less "$docfile"
                else
                    echo "❌ File not found: $docfile"
                fi
            fi
            ;;
        7)
            echo -e "${BLUE}Directory structure:${NC}"
            echo ""
            tree -L 2 -I '__pycache__|*.pyc' || find . -maxdepth 2 -not -path '*/\.*' -type d
            ;;
        8)
            echo "Goodbye! 👋"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 1-8."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
    clear
done
