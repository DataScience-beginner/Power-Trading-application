#!/usr/bin/env python
"""
Power Trading Desktop App - Launcher
Run this script to start the desktop application.
"""

import os
import sys
import subprocess
import platform

def main():
    # Check dependencies
    try:
        import customtkinter
        import requests
        import matplotlib
        import pandas
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Installing required packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "customtkinter", "requests", "matplotlib", "pandas", "pillow"
        ])
        print("Dependencies installed. Starting application...")
    
    # Run the main application
    app_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.check_call([sys.executable, app_path])

if __name__ == "__main__":
    main()