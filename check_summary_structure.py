"""Check what's in the summary field"""
import sys
sys.path.insert(0, '.')

from database.config import SessionLocal
from database.models import DailyFile
import json

db = SessionLocal()

# Get one DOR file
dor_file = db.query(DailyFile).filter(DailyFile.report_type == 'DOR_GDAM').first()

if dor_file:
    print("DOR Summary:")
    summary = json.loads(dor_file.summary) if isinstance(dor_file.summary, str) else dor_file.summary
    print(json.dumps(summary, indent=2))
else:
    print("No DOR file found")

# Get one SCH file  
sch_file = db.query(DailyFile).filter(DailyFile.report_type.like('SCH%')).first()

if sch_file:
    print("\nSCH Summary:")
    summary = json.loads(sch_file.summary) if isinstance(sch_file.summary, str) else sch_file.summary
    print(json.dumps(summary, indent=2))
else:
    print("No SCH file found")

db.close()
