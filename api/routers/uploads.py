"""Upload and parsed-file management routes."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import services as db_services
from database.config import get_db
from api.security.upload_security import max_upload_bytes, scan_file, validate_workbook
from uuid import uuid4
from parsers.DOR_Parser import GDAMTemplateParser
from parsers.SCH_Parser import SCHTemplateParser


router = APIRouter(tags=["uploads"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post(
    "/api/data/bulk-upload",
    response_model=dict[str, Any],
    summary="Bulk upload parsed trading data",
    description="Uploads trading data as JSON and stores clients, portfolios, daily files, and transactions.",
)
async def bulk_upload_data(
    data: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Bulk upload parsed trading data without Excel parsing."""
    try:
        entity_id = data.get("entity_id")
        portfolio_code = data.get("portfolio_code")
        trading_date = datetime.fromisoformat(data.get("trading_date")).date()
        report_type = data.get("report_type")
        transactions = data.get("transactions", [])

        client = db_services.get_or_create_client(
            db,
            entity_id=entity_id,
            entity_name=data.get("entity_name", "Unknown"),
        )

        portfolio = db_services.get_or_create_portfolio(
            db,
            client_id=client.id,
            portfolio_code=portfolio_code,
            portfolio_name=data.get("portfolio_name", portfolio_code),
        )

        daily_file = db_services.save_daily_file(
            db,
            portfolio_id=portfolio.id,
            trading_date=trading_date,
            report_type=report_type,
            sub_category=data.get("sub_category", "DAM"),
            delivery_date=trading_date,
            filename=f"{report_type}_{trading_date}_{portfolio_code}.json",
            file_size=len(str(data)),
            parsed_data=data,
        )

        saved_count = db_services.save_transactions(db, daily_file.id, transactions)

        return {
            "success": True,
            "message": f"Uploaded {report_type} with {saved_count} transactions",
            "file_id": daily_file.id,
            "client_id": client.id,
            "portfolio_id": portfolio.id,
        }

    except Exception as e:
        import traceback

        print(f"❌ Bulk upload error: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}


@router.post(
    "/api/upload",
    response_model=dict[str, Any],
    summary="Upload trading Excel file",
    description="Uploads, parses, stores, and triggers energy schedule rebuild for a trading Excel file.",
)
async def upload_file(
    file: UploadFile = File(...),
    client_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Upload and parse an Excel trading file."""
    print(f"\n{'=' * 60}")
    print(f"📥 UPLOAD REQUEST: {file.filename}")
    print(f"Content-Type: {file.content_type}")
    print(f"Size: {file.size if hasattr(file, 'size') else 'unknown'}")
    print(f"{'=' * 60}\n")

    try:
        content = await file.read(max_upload_bytes() + 1)
        validate_workbook(file.filename, content)
        quarantine_dir = OUTPUT_DIR / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        temp_file = quarantine_dir / f"{uuid4()}{Path(file.filename).suffix.lower()}"
        print(f"💾 Saving to temp location: {temp_file}")

        with open(temp_file, "wb") as f:
            f.write(content)

        scan_file(temp_file)

        print(f"✅ File saved successfully ({len(content)} bytes)")

        filename_upper = file.filename.upper()
        if "SCH" in filename_upper:
            print("📋 Detected SCH (Scheduling) report format")
            parser = SCHTemplateParser(client_id=client_id or "default-client")
        else:
            print("📋 Detected GDAM/RTM/DOR report format")
            parser = GDAMTemplateParser(client_id=client_id or "default-client")

        print(f"🔍 Starting parser for: {temp_file.name}")
        parsed_data = parser.parse_excel(str(temp_file))

        print("✅ Parsing completed successfully")
        print(f"   - Format: {parsed_data['metadata'].get('report_type')}")

        if "scheduling_transactions" in parsed_data:
            print(f"   - Scheduling Transactions: {len(parsed_data['scheduling_transactions'])}")
        else:
            print(f"   - Buy Transactions: {len(parsed_data['buy_transactions'])}")
            print(f"   - Sell Transactions: {len(parsed_data['sell_transactions'])}")

        output_filename = f"{uuid4()}_parsed.json"
        output_file = OUTPUT_DIR / output_filename

        print(f"💾 Saving parsed data to: {output_filename}")

        with open(output_file, "w") as f:
            json.dump(parsed_data, f, indent=2)

        print("✅ Data saved successfully\n")
        print("\n🗄️  SAVING TO DATABASE...")

        metadata = parsed_data["metadata"]

        client = db_services.get_or_create_client(
            db,
            entity_id=metadata.get("entity_id", "UNKNOWN"),
            entity_name=metadata.get("entity_name", "Unknown Entity"),
        )

        portfolio = db_services.get_or_create_portfolio(
            db,
            client_id=client.id,
            portfolio_code=metadata.get("portfolio_code", metadata.get("entity_id", "DEFAULT")),
            portfolio_name=metadata.get("portfolio_name"),
        )

        trading_date = (
            datetime.fromisoformat(metadata["trading_date"]).date()
            if metadata.get("trading_date")
            else date.today()
        )
        delivery_date = (
            datetime.fromisoformat(metadata["delivery_date"]).date()
            if metadata.get("delivery_date")
            else trading_date
        )

        daily_file = db_services.save_daily_file(
            db,
            portfolio_id=portfolio.id,
            trading_date=trading_date,
            delivery_date=delivery_date,
            main_category=metadata.get("main_category", "DOR"),
            sub_category=metadata.get("sub_category", "DAM"),
            report_type=metadata.get("report_type", "DOR-DAM"),
            original_filename=file.filename,
            file_path=str(output_file),
            parsed_data=parsed_data,
        )

        transactions_to_save = []
        if "scheduling_transactions" in parsed_data and parsed_data["scheduling_transactions"]:
            transactions_to_save = [
                {**txn, "transaction_type": "scheduling"} for txn in parsed_data["scheduling_transactions"]
            ]
        else:
            for txn in parsed_data.get("buy_transactions", []):
                transactions_to_save.append({**txn, "transaction_type": "buy"})
            for txn in parsed_data.get("sell_transactions", []):
                transactions_to_save.append({**txn, "transaction_type": "sell"})

        txn_count = db_services.save_transactions(db, daily_file.id, transactions_to_save)

        print("✅ DATABASE SAVE COMPLETE:")
        print(f"   - Client: {client.entity_name}")
        print(f"   - Portfolio: {portfolio.portfolio_code}")
        print(f"   - File ID: {daily_file.id}")
        print(f"   - Transactions: {txn_count}")

        energy_schedule_result = None
        try:
            from database.energy_schedule_builder import rebuild_energy_schedule_for_day

            print("\n⚡ REBUILDING ENERGY SCHEDULE FROM SAVED DATA...")

            energy_schedule_result = rebuild_energy_schedule_for_day(
                db,
                portfolio_id=portfolio.id,
                trading_date=trading_date,
            )
            energy_schedule_result["auto_calculated"] = energy_schedule_result["is_complete"]

            print(f"   ✅ Energy schedule day: {energy_schedule_result['daily_entry_id']}")
            print(f"      Complete: {energy_schedule_result['is_complete']}")
            print(f"      Files found: {energy_schedule_result['files_found']}")
            print(f"      Total scheduled: {energy_schedule_result['total_scheduled_mwh']:.2f} MWh")
            print(
                f"      Total consumption: "
                f"{energy_schedule_result['total_consumption_after_losses_mwh']:.2f} MWh"
            )
        except Exception as e:
            print(f"\n   ⚠️  Energy Schedule rebuild skipped: {str(e)}")
            energy_schedule_result = {"auto_calculated": False, "error": str(e)}

        temp_file.unlink()
        print("\n🗑️  Temp file cleaned up")

        return {
            "success": True,
            "message": "File parsed and saved to database successfully",
            "filename": output_filename,
            "database": {
                "client_id": client.id,
                "portfolio_id": portfolio.id,
                "file_id": daily_file.id,
                "transactions_saved": txn_count,
            },
            "energy_schedule": energy_schedule_result,
            "data": parsed_data,
            "summary": {
                "trading_date": metadata.get("trading_date"),
                "delivery_date": metadata.get("delivery_date"),
                "entity": metadata.get("entity_name"),
                "portfolio": portfolio.portfolio_code,
                "report_type": metadata.get("report_type"),
                "buy_transactions": parsed_data["summary"].get("total_buy_transactions", 0),
                "sell_transactions": parsed_data["summary"].get("total_sell_transactions", 0),
                "net_amount": parsed_data["summary"].get("net_amount", 0),
            },
        }

    except Exception as e:
        if "temp_file" in locals() and temp_file.exists():
            temp_file.unlink()

        import traceback

        error_details = traceback.format_exc()
        print(f"\n{'=' * 60}")
        print(f"❌ ERROR: Failed to parse file {file.filename}")
        print(f"{'=' * 60}")
        print(error_details)
        print(f"{'=' * 60}\n")

        raise HTTPException(
            status_code=500,
            detail=(
                f"Error parsing file: {str(e)}. Please ensure you're uploading a valid "
                "GDAM IEX trading report in .xls or .xlsx format."
            ),
        ) from e


@router.get(
    "/api/files",
    response_model=dict[str, Any],
    summary="List parsed files",
    description="Lists parsed JSON files stored in the local output folder.",
)
async def list_files() -> dict[str, Any]:
    """List parsed data files."""
    try:
        files = []
        for file_path in OUTPUT_DIR.glob("*_parsed_*.json"):
            stat = file_path.stat()
            files.append(
                {
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        files.sort(key=lambda x: x["modified"], reverse=True)

        return {"success": True, "count": len(files), "files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}") from e


@router.get(
    "/api/data/{filename}",
    response_model=dict[str, Any],
    summary="Get parsed file data",
    description="Returns parsed JSON data by generated filename.",
)
async def get_data(filename: str) -> dict[str, Any]:
    """Return parsed data by filename."""
    try:
        file_path = OUTPUT_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        with open(file_path, "r") as f:
            data = json.load(f)

        return {"success": True, "filename": filename, "data": data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}") from e


@router.get(
    "/api/summary/{filename}",
    response_model=dict[str, Any],
    summary="Get parsed file summary",
    description="Returns metadata, summary, charges, and transaction counts for a parsed JSON file.",
)
async def get_summary(filename: str) -> dict[str, Any]:
    """Return parsed data summary by filename."""
    try:
        file_path = OUTPUT_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        with open(file_path, "r") as f:
            data = json.load(f)

        return {
            "success": True,
            "filename": filename,
            "metadata": data.get("metadata", {}),
            "summary": data.get("summary", {}),
            "charges": data.get("charges", {}),
            "transaction_counts": {
                "buy": len(data.get("buy_transactions", [])),
                "sell": len(data.get("sell_transactions", [])),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}") from e


@router.delete(
    "/api/data/{filename}",
    response_model=dict[str, Any],
    summary="Delete parsed file",
    description="Deletes a parsed JSON file from local output storage.",
)
async def delete_file(filename: str) -> dict[str, Any]:
    """Delete a parsed data file."""
    try:
        file_path = OUTPUT_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        file_path.unlink()

        return {"success": True, "message": f"File deleted: {filename}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}") from e
