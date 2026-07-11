#!/usr/bin/env python3
"""
Initialize Database Script

This script creates the SQLite database and all tables.
Run this once to set up the database structure.

Usage:
    python init_database.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so we can import database module
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from database.config import init_db, DATABASE_URL

def main():
    print("=" * 60)
    print("🗄️  INITIALIZING POWER TRADING DATABASE")
    print("=" * 60)
    
    print(f"\n📍 Database URL: {DATABASE_URL}")
    
    database_file = None
    if DATABASE_URL.startswith("sqlite:///"):
        database_file = DATABASE_URL.replace("sqlite:///", "", 1)

    # Check if local SQLite database already exists
    if database_file and os.path.exists(database_file):
        response = input("\n⚠️  Database already exists. Recreate it? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
        else:
            os.remove(database_file)
            print("🗑️  Old database deleted.")
    
    # Create database and tables
    print("\n📦 Creating tables...")
    init_db()
    
    print("\n✅ Database initialization complete!")
    print("\n📊 Tables created:")
    print("   1. clients          - Store client/entity information")
    print("   2. portfolios       - Store portfolio information")
    print("   3. daily_files      - Store uploaded file metadata")
    print("   4. transactions     - Store time-slot level data (96 per file)")
    print("   5. monthly_calculations - Store calculation results")
    
    print(f"\n💡 Database ready: {DATABASE_URL}")
    print("=" * 60)

if __name__ == "__main__":
    main()
