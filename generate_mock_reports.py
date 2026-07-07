"""Generate parser-compatible mock DOR and SCH reports for upload testing."""

from datetime import datetime, timedelta
from pathlib import Path
import random

from openpyxl import Workbook


START_DATE = datetime(2026, 1, 1)
NUM_DAYS = 30
OUTPUT_DIR = Path(__file__).parent / "Data" / "mock_reports"
CLIENT_CODE = "NPT0027_KA0"
CLIENT_NAME = "Mellbro_Sugars_Pvt"
ENTITY_ID = "A2AR0NPT0000"
ENTITY_NAME = "Mellbro Sugars Pvt Ltd"


def create_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created output directory: {OUTPUT_DIR}")


def _time_block(slot: int) -> tuple[str, str, str]:
    start = (datetime(2026, 1, 1) + timedelta(minutes=(slot - 1) * 15)).time()
    end = (datetime(2026, 1, 1) + timedelta(minutes=slot * 15)).time()
    start_s = f"{start.hour:02d}:{start.minute:02d}"
    end_s = f"{end.hour:02d}:{end.minute:02d}"
    return f"{start_s} - {end_s}", start_s, end_s


def create_dor_report(trading_date: datetime, market_type: str = "GDAM") -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "DOR"

    # Metadata rows expected by parser
    ws.cell(row=8, column=3, value="Delivery Date")
    ws.cell(row=8, column=9, value=trading_date)
    ws.cell(row=9, column=9, value=ENTITY_ID)
    ws.cell(row=9, column=19, value=ENTITY_NAME)
    ws.cell(row=10, column=9, value=CLIENT_CODE)
    ws.cell(row=10, column=19, value=CLIENT_NAME.replace("_", " "))

    # Charges section (rows 12-30 scanned by parser)
    ws.cell(row=13, column=2, value="Funds Payin/Payout")
    ws.cell(row=13, column=6, value=round(random.uniform(-12000, 22000), 2))
    ws.cell(row=14, column=2, value="NLDC Application Fee")
    ws.cell(row=14, column=6, value=round(random.uniform(100, 500), 2))
    ws.cell(row=15, column=2, value="STU Transmission Charges")
    ws.cell(row=15, column=6, value=round(random.uniform(1000, 4000), 2))
    ws.cell(row=16, column=2, value="Total")
    ws.cell(row=16, column=6, value=round(random.uniform(2000, 7000), 2))

    # Marker for Daily Obligation transaction extraction
    ws.cell(row=45, column=2, value="Daily Trade Report")

    # Data starts 2 rows after marker => row 47 (1-based)
    start_row = 47
    for slot in range(1, 97):
        block, _, _ = _time_block(slot)
        qty = round(random.uniform(0.1, 5.0), 3)
        rate = round(random.uniform(3200, 7600), 2)
        amount = round(qty * rate, 2)

        # Group 1 expected columns: period=2, qty=4, rate=8, amount=9 (0-based)
        ws.cell(row=start_row + slot - 1, column=3, value=block)
        ws.cell(row=start_row + slot - 1, column=5, value=qty)
        ws.cell(row=start_row + slot - 1, column=9, value=rate)
        ws.cell(row=start_row + slot - 1, column=10, value=amount)

        # Group 2 expected columns: period=11, qty=15, rate=19, amount=22 (0-based)
        ws.cell(row=start_row + slot - 1, column=12, value=block)
        ws.cell(row=start_row + slot - 1, column=16, value=round(qty * random.uniform(0.8, 1.2), 3))
        ws.cell(row=start_row + slot - 1, column=20, value=round(rate * random.uniform(0.95, 1.05), 2))
        ws.cell(row=start_row + slot - 1, column=23, value=round(amount * random.uniform(0.95, 1.05), 2))

    ws.cell(row=start_row + 98, column=3, value="Total")

    date_str = trading_date.strftime("%d%m%y")
    filename = f"{market_type}_IEX{date_str}DOR_{CLIENT_CODE}_{CLIENT_NAME}.xlsx"
    filepath = OUTPUT_DIR / filename
    wb.save(filepath)
    return str(filepath)


def create_sch_report(trading_date: datetime) -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "SCH"

    # Metadata tokens expected by parser
    ws.cell(row=3, column=1, value="Scheduling Date")
    ws.cell(row=3, column=2, value=trading_date)
    ws.cell(row=4, column=1, value="Participant")
    ws.cell(row=4, column=2, value=ENTITY_NAME)
    ws.cell(row=5, column=1, value="Portfolio")
    ws.cell(row=5, column=2, value=CLIENT_CODE)

    # Header row directly above data start
    ws.cell(row=8, column=1, value="Time Period")
    ws.cell(row=8, column=2, value="Injection at Regional periphery")
    ws.cell(row=8, column=3, value="Drawal at Regional periphery")
    ws.cell(row=8, column=8, value="Injection at Interface point")
    ws.cell(row=8, column=9, value="Drawal at Interface point")

    # Data row starts at row 9; parser expects col0 time block pattern
    for slot in range(1, 97):
        block, _, _ = _time_block(slot)
        regional_inj = round(random.uniform(0, 10), 3)
        regional_drw = round(random.uniform(0, 10), 3)
        interface_inj = round(regional_inj * random.uniform(0.96, 1.0), 3)
        interface_drw = round(regional_drw * random.uniform(0.96, 1.0), 3)

        row = 8 + slot
        ws.cell(row=row, column=1, value=block)
        ws.cell(row=row, column=2, value=regional_inj)
        ws.cell(row=row, column=3, value=regional_drw)
        ws.cell(row=row, column=8, value=interface_inj)
        ws.cell(row=row, column=9, value=interface_drw)

    ws.cell(row=106, column=1, value="Total")

    date_str = trading_date.strftime("%d%m%y")
    filename = f"IEX{date_str}SCH_{CLIENT_CODE}_{CLIENT_NAME}.xlsx"
    filepath = OUTPUT_DIR / filename
    wb.save(filepath)
    return str(filepath)


def generate_all_mock_reports() -> list[str]:
    create_output_dir()

    print(f"\n🔧 Generating {NUM_DAYS} days of parser-compatible mock reports...")
    print(
        f"📅 Date range: {START_DATE.strftime('%Y-%m-%d')} "
        f"to {(START_DATE + timedelta(days=NUM_DAYS - 1)).strftime('%Y-%m-%d')}\n"
    )

    generated_files: list[str] = []

    for day in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day)
        print(f"Day {day + 1}/{NUM_DAYS}: {current_date.strftime('%Y-%m-%d')}")

        for market_type in ["GDAM", "DAM", "RTM"]:
            filepath = create_dor_report(current_date, market_type)
            generated_files.append(filepath)
            print(f"  ✓ Created DOR-{market_type}: {Path(filepath).name}")

        filepath = create_sch_report(current_date)
        generated_files.append(filepath)
        print(f"  ✓ Created SCH: {Path(filepath).name}")

    print(f"\n✅ Generated {len(generated_files)} mock report files")
    print(f"📁 Location: {OUTPUT_DIR}")

    return generated_files


if __name__ == "__main__":
    print("=" * 80)
    print("MOCK DATA GENERATOR - Parser Compatible Reports")
    print("=" * 80)

    generate_all_mock_reports()

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Upload these files to the database using: .venv\\Scripts\\python.exe upload_mock_reports.py")
    print("2. Test calculation engine with the uploaded data")
    print("3. Verify energy schedule calculations in dashboard")
    print("=" * 80)
