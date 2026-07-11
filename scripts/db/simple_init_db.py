"""
Simple database initialization - creates all tables
"""
from database.config import init_db

print("🗄️  Initializing database...")
init_db()
print("✅ Database initialized successfully")
print("\nTables created:")
print("   - clients")
print("   - portfolios")
print("   - daily_files")
print("   - transactions")
print("   - monthly_calculations")
