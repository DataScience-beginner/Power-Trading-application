#!/usr/bin/env python3
"""Rebuild Energy Schedule tables from daily_files and transactions."""

from database.config import SessionLocal
from database.energy_schedule_builder import rebuild_energy_schedules


def main() -> int:
    db = SessionLocal()
    try:
        result = rebuild_energy_schedules(db)
        print(f"days_processed={result['days_processed']}")
        print(f"complete_days={result['complete_days']}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
