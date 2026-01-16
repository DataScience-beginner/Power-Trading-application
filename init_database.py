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

# Add parent directory to path so we can import database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.config import init_db, DATABASE_FILE

def main():
    print("=" * 60)
    print("🗄️  INITIALIZING POWER TRADING DATABASE")
    print("=" * 60)
    
    print(f"\n📍 Database Location: {DATABASE_FILE}")
    
    # Check if database already exists
    if os.path.exists(DATABASE_FILE):
        response = input("\n⚠️  Database already exists. Recreate it? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
        else:
            os.remove(DATABASE_FILE)
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
    
    print(f"\n💡 Database ready at: {DATABASE_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
