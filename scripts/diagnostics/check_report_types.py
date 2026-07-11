"""Check report types in database"""
import sys
sys.path.insert(0, '.')

from database.config import SessionLocal
from database.models import DailyFile
from sqlalchemy import func

db = SessionLocal()

# Count by report type
report_counts = db.query(
    DailyFile.report_type,
    func.count(DailyFile.id).label('count')
).group_by(DailyFile.report_type).all()

print("Report Types in Database:")
print("=" * 40)
for report_type, count in report_counts:
    print(f"{report_type}: {count}")

db.close()
