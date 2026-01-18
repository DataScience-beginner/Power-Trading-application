"""
Add missing columns to clients table
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL, check for Railway's individual PostgreSQL variables
if not DATABASE_URL:
    pg_host = os.getenv("PGHOST")
    pg_user = os.getenv("PGUSER", os.getenv("PGUSERNAME"))
    pg_password = os.getenv("PGPASSWORD")
    pg_database = os.getenv("PGDATABASE")
    pg_port = os.getenv("PGPORT", "5432")
    
    if all([pg_host, pg_user, pg_password, pg_database]):
        DATABASE_URL = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    else:
        DATABASE_URL = "sqlite:///./power_trading.db"

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🔧 Connecting to database: {'PostgreSQL' if 'postgresql' in DATABASE_URL else 'SQLite'}")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if columns exist
        print("🔍 Checking existing columns...")
        
        # Add lat column
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN lat FLOAT DEFAULT 12.97"))
            conn.commit()
            print("✅ Added 'lat' column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("⏭️  'lat' column already exists")
            else:
                print(f"⚠️  Error adding 'lat': {e}")
        
        # Add lon column
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN lon FLOAT DEFAULT 80.22"))
            conn.commit()
            print("✅ Added 'lon' column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("⏭️  'lon' column already exists")
            else:
                print(f"⚠️  Error adding 'lon': {e}")
        
        # Add capacity_kw column
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN capacity_kw INTEGER DEFAULT 5000"))
            conn.commit()
            print("✅ Added 'capacity_kw' column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("⏭️  'capacity_kw' column already exists")
            else:
                print(f"⚠️  Error adding 'capacity_kw': {e}")
        
        # Add farm_type column
        try:
            conn.execute(text("ALTER TABLE clients ADD COLUMN farm_type VARCHAR DEFAULT 'solar'"))
            conn.commit()
            print("✅ Added 'farm_type' column")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("⏭️  'farm_type' column already exists")
            else:
                print(f"⚠️  Error adding 'farm_type': {e}")
        
        print("\n✅ Migration complete!")
        
except Exception as e:
    print(f"❌ Error: {e}")
