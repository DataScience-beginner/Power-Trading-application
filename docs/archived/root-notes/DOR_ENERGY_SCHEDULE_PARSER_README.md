# DOR Energy Schedule Parser - Documentation

## Overview
The `DOR_EnergySchedule_Parser.py` extracts summary data from DOR (Daily Obligation Report) files for Energy Schedule calculations. It supports all three market types: **GDAM**, **DAM**, and **RTM**.

## Story 1.2 Completion ✅
This parser fulfills Story 1.2: "Map DOR summary data (GDAM/DAM/RTM)" from the Energy Schedule workflow.

## Features
- ✅ Auto-converts `.xls` files to `.xlsx` using LibreOffice
- ✅ Detects market type from filename (GDAM/DAM/RTM)
- ✅ Extracts all required summary fields for Energy Schedule rows 4-6
- ✅ Handles special characters (asterisks, commas) in numeric values
- ✅ Outputs structured JSON with metadata and summary charges

## Extracted Fields

### Summary Charges
- **NLDC Application Fee** (Row 14, Column 12)
- **CTU Transmission Charges** (Row 15, Column 12)
  - Includes injection and drawal rates from formula section
- **Total Cost** (Row 28, Column 12)
- **Other Charges**:
  - NLDC Scheduling & Operating Charges - Sell (Row 17)
  - STU Transmission Charges (Row 18)
  - SLDC Scheduling Charges (Row 21)
  - Fees (Row 23)

### Metadata
- Market type (GDAM/DAM/RTM)
- Trading date (extracted from filename)
- Portfolio code (e.g., NPT0027_KA0)
- Entity name

## Usage

### Command Line
```bash
python parsers/DOR_EnergySchedule_Parser.py <path_to_dor_file>
```

### Example
```bash
# GDAM file
python parsers/DOR_EnergySchedule_Parser.py Data/GDAM_IEX120126DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xls

# DAM file
python parsers/DOR_EnergySchedule_Parser.py Data/IEX130126DOR_NPT0019_TN0_Grasim_Industries_Limited.xls

# RTM file
python parsers/DOR_EnergySchedule_Parser.py Data/RTM_IEX130126DOR_NPT0019_TN0_Grasim_Industries_Limited.XLS
```

### Python Code
```python
from parsers.DOR_EnergySchedule_Parser import DOR_EnergyScheduleParser

# Initialize parser
parser = DOR_EnergyScheduleParser("path/to/dor_file.xls")

# Parse and get results
result = parser.parse()

# Access data
print(f"Market Type: {result['metadata']['market_type']}")
print(f"NLDC Fee: {result['summary']['nldc_application_fee']}")
print(f"CTU Charges: {result['summary']['ctu_transmission_charges']['total']}")
print(f"Total Cost: {result['summary']['total_cost']}")
```

## Output Format

### JSON Structure
```json
{
  "metadata": {
    "market_type": "GDAM",
    "file_name": "GDAM_IEX120126DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
    "parsed_at": "2026-01-16T05:18:28.027898",
    "trading_date": "2026-01-12",
    "portfolio_code": "NPT0027_KA0",
    "entity_name": "Mellbro Sugars Pvt"
  },
  "summary": {
    "nldc_application_fee": -5.13,
    "ctu_transmission_charges": {
      "total": 0.0,
      "injection_rate_per_mw_timeblock": 5000.0,
      "drawal_rate_per_mw_timeblock": 0.0
    },
    "total_cost": 1674432.7594,
    "scheduled_quantity": 0.0,
    "other_charges": {
      "nldc_scheduling_operating_sell": -200.0,
      "stu_transmission_charges": -25920.0,
      "sldc_scheduling_charges": -1000.0,
      "fees": -6480.0
    }
  },
  "rate_info": {}
}
```

## Energy Schedule Mapping

The extracted data maps to Energy Schedule template as follows:

| Excel Row | Market Type | NLDC Fee | CTU Charges | Cost |
|-----------|-------------|----------|-------------|------|
| Row 4 | GDAM | -5.13 | 0.00 | 1674432.76 |
| Row 5 | DAM | -4.91 | -805.73 | -6396.66 |
| Row 6 | RTM | -5.74 | -585.99 | -5556.44 |

## Test Results (Sample Data)

### GDAM File
- **Portfolio**: NPT0027_KA0 (Mellbro Sugars Pvt)
- **Trading Date**: 2026-01-12
- **NLDC Fee**: ₹-5.13
- **CTU Charges**: ₹0.00
- **Total Cost**: ₹1,674,432.76

### DAM File
- **Portfolio**: NPT0019_TN0 (Grasim Industries Limited)
- **Trading Date**: 2026-01-13
- **NLDC Fee**: ₹-4.91
- **CTU Charges**: ₹-805.73
- **Total Cost**: ₹-6,396.66

### RTM File
- **Portfolio**: NPT0019_TN0 (Grasim Industries Limited)
- **Trading Date**: 2026-01-13
- **NLDC Fee**: ₹-5.74
- **CTU Charges**: ₹-585.99
- **Total Cost**: ₹-5,556.44

## Technical Details

### File Structure
DOR files have this structure:
- **Row 13**: "Charges" header
- **Rows 14-28**: Individual charge line items (labels in column 3, values in column 12)
- **Rows 33-38**: Formula explanations with rates

### Column Indexing
- **Column 3**: Field labels
- **Column 12**: Numeric values (1-indexed display, 0-indexed in code = column 11)

### Data Cleaning
The parser handles:
- Asterisks in values (e.g., `-200.00*`)
- Comma separators in numbers (e.g., `1,674,432.76`)
- Both `.xls` and `.XLS` file extensions

## Dependencies
- `pandas` - Excel file reading
- `openpyxl` - Excel engine
- `LibreOffice` - .xls to .xlsx conversion

## Next Steps
**Story 1.3**: Create Energy Schedule data model for monthly day-wise storage in database.

## Related Files
- **SCH Parser**: `parsers/SCH_Energy_Schedule_Parser.py` - Extracts consumption after losses (96 time slots)
- **Original DOR Parser**: `parsers/DOR_Parser.py` - Extracts full transaction details
- **Energy Schedule Template**: `Data/12. IEX Purchase Data DEC 2022_Brookefields Mall.xlsx`

## Author
Power Trading Application Team  
Date: January 16, 2026
