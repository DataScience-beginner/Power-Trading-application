# Power Trading Application - Parsers Guide

## Supported File Formats

The application now supports **4 different IEX trading report formats**:

### 1. GDAM (Day-Ahead Market) Format
**Parser:** `GDAMTemplateParser` (parsers/gdam_template_parser.py)

**Features:**
- Separate Buy and Sell transaction sections
- 96 time slots (15-minute intervals)
- Complete charge breakdown with formulas
- Trading date and delivery date metadata

**File Pattern:** `GDAM_IEX*.xls` or `*GDAM*.xls*`

**Data Structure:**
- Buy Transactions: Quantity, Rate, Amount
- Sell Transactions: Solar/Non-Solar/Hydro breakdown
- Charges: NLDC, CTU, STU, SLDC, Taxes (IGST, SGST, CGST, UTGST)
- Funds Payin/Payout calculation

---

### 2. RTM (Real-Time Market) Format
**Parser:** `GDAMTemplateParser` (same as GDAM)

**Features:**
- Daily Obligation Summary format
- Single delivery date (no separate trading date)
- Combined transaction section
- All 96 time slots with zero-quantity inclusion

**File Pattern:** `RTM_IEX*.xls` or `*RTM*.xls*`

**Data Structure:**
- Transactions: Period, Quantity, Rate, Amount
- Supports multiple column groups (left and right sections)
- Chronologically sorted time series

---

### 3. DOR (Daily Obligation Report) Format
**Parser:** `GDAMTemplateParser` (same as GDAM)

**Features:**
- Similar to RTM format
- Daily Trade Report structure
- Regional and interface data

**File Pattern:** `*DOR*.xls*` or `IEX*DOR*.xls*`

**Data Structure:**
- Same as RTM format
- Combined transaction listing
- Complete charge breakdown

---

### 4. SCH (Scheduling Report) Format ⭐ NEW
**Parser:** `SCHTemplateParser` (parsers/sch_template_parser.py)

**Features:**
- Scheduling data with dual perspectives
- Regional periphery vs Interface point data
- Injection and Drawal quantities
- Issue date/time tracking

**File Pattern:** `*SCH*.xlsx` or `IEX*SCH*.xlsx`

**Data Structure:**
```json
{
  "scheduling_transactions": [
    {
      "date": "2026-01-14",
      "time_slot": "00:00 - 00:15",
      "regional_injection_mw": 0.0,
      "regional_drawal_mw": 0.2,
      "regional_net_mw": -0.2,
      "interface_injection_mw": 0.0,
      "interface_drawal_mw": 0.18,
      "interface_net_mw": -0.18,
      "net_scheduled_mw": -0.18
    }
  ]
}
```

**Summary Fields:**
- `total_scheduling_slots`: Total time slots (96)
- `total_regional_injection_mwh`: Regional injection total
- `total_regional_drawal_mwh`: Regional drawal total
- `total_interface_injection_mwh`: Interface injection total
- `total_interface_drawal_mwh`: Interface drawal total
- `net_regional_mwh`: Net regional position
- `net_interface_mwh`: Net interface position

---

## Parser Selection Logic

The API automatically selects the correct parser based on filename:

```python
if 'SCH' in filename.upper():
    parser = SCHTemplateParser()
else:
    parser = GDAMTemplateParser()  # Handles GDAM, RTM, DOR
```

The `GDAMTemplateParser` internally detects:
- GDAM format: Looks for "G-DAM Purchase" section
- Daily Obligation (RTM/DOR): Looks for "Daily Trade Report" section

---

## File Compatibility

### Excel Version Support
- ✅ `.xls` (Excel 97-2003) - Auto-converted via LibreOffice
- ✅ `.xlsx` (Excel 2007+) - Direct parsing with openpyxl
- ✅ Case-insensitive extensions (`.XLS`, `.XLSX`, `.xls`, `.xlsx`)

### Conversion Pipeline
1. Detect file extension (case-insensitive)
2. If `.xls` → Convert to `.xlsx` using LibreOffice
3. Parse with openpyxl engine
4. Extract data based on detected format

---

## Web UI Display

### GDAM/RTM/DOR Reports
**Tabs:**
- 📊 Metadata
- 🔵 Buy Transactions
- 🔴 Sell Transactions
- 💰 Charges

**Summary Cards:**
- Trading Date (with remarks tooltip)
- Buy Transactions count
- Sell Transactions count
- Funds Payin/Payout (color-coded)

### SCH Reports
**Tabs:**
- 📊 Metadata
- 📅 Scheduling Transactions (Regional & Interface)

**Summary Cards:**
- Scheduling Date
- Total Slots
- Net Interface (MWh)
- Portfolio Name

**Transaction Table Columns:**
1. Date
2. Time Slot
3. Regional Injection (MW)
4. Regional Drawal (MW)
5. Regional Net (MW) - Color-coded
6. Interface Injection (MW)
7. Interface Drawal (MW)
8. Interface Net (MW) - Color-coded

---

## API Usage

### Upload Endpoint
```
POST /api/upload
```

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (Excel file)
- Optional: `client_id` (string)

**Response:**
```json
{
  "success": true,
  "message": "File parsed successfully",
  "filename": "parsed_file_name.json",
  "data": { ... },
  "summary": {
    "trading_date": "2026-01-14",
    "delivery_date": "2026-01-14",
    "entity": "NEFA Power Trading Private Limited",
    "buy_transactions": 96,
    "sell_transactions": 0
  }
}
```

### List Files
```
GET /api/files
```

Returns all parsed JSON files in the output directory.

### Get Parsed Data
```
GET /api/data/{filename}
```

Returns the full parsed data for a specific file.

---

## Testing

### Test GDAM File
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@Data/GDAM_IEX120126DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xls"
```

### Test RTM File
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@Data/RTM_IEX130126DOR_NPT0019_TN0_Grasim_Industries_Limited.XLS"
```

### Test SCH File
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@Data/IEX260114SCH_NPT0019_TN0_Grasim_Industries_Limited.xlsx"
```

---

## Server Logs

Detailed logging for every upload:

```
============================================================
📥 UPLOAD REQUEST: IEX260114SCH_NPT0019_TN0_Grasim_Industries_Limited.xlsx
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Size: 45232
============================================================

✅ File type validation passed
💾 Saving to temp location: /output/temp_file.xlsx
✅ File saved successfully (45232 bytes)
📋 Detected SCH (Scheduling) report format
🔍 Starting parser
✅ Parsing completed successfully
   - Format: Scheduling Report
   - Scheduling Transactions: 96
💾 Saving parsed data to: output_file.json
✅ Data saved successfully
🗑️  Temp file cleaned up
```

---

## Troubleshooting

### Issue: "Invalid file type" error
**Solution:** File extension must be `.xls` or `.xlsx` (case-insensitive)

### Issue: RTM file not parsing
**Solution:** Ensure filename contains "RTM" - auto-detected from filename

### Issue: SCH file showing wrong format
**Solution:** Filename must contain "SCH" for proper parser selection

### Issue: Transactions not in chronological order
**Solution:** ✅ Already fixed - all parsers now sort by `time_block_start`

### Issue: Zero-quantity slots missing
**Solution:** ✅ Already fixed - all 96 slots included regardless of quantity

---

## Developer Notes

### Adding New Format

1. Create new parser class in `parsers/` directory
2. Implement required methods:
   - `parse_excel(file_path)` - Main entry point
   - `_extract_metadata()` - Extract header info
   - `_extract_transactions()` - Extract transaction data
   - `_calculate_summary()` - Calculate summaries
   - `_validate()` - Validate output
3. Update `api/main.py` to import and route to new parser
4. Update `frontend/index.html` to display new format
5. Add tests and update documentation

### Universal Schema Compliance

All parsers must return:
```python
{
    "schema_version": "1.0.0",
    "template_id": "PARSER_ID_V1",
    "client_id": "...",
    "metadata": { ... },
    "buy_transactions": [ ... ],  # or scheduling_transactions
    "sell_transactions": [ ... ],
    "charges": { ... },
    "summary": { ... },
    "parsed_at": "ISO8601 datetime"
}
```

---

## Version History

- **v1.0.0** - Initial GDAM parser
- **v1.1.0** - Added RTM/DOR support, LibreOffice conversion
- **v1.2.0** - Fixed chronological sorting, zero-quantity inclusion
- **v1.3.0** - Added charge formulas, tooltips
- **v1.4.0** - ⭐ Added SCH (Scheduling) parser

---

**Last Updated:** January 14, 2026
**Server:** http://localhost:8000
