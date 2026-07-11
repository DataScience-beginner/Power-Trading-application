# ⚡ Power Trading Application

Professional power trading data parser and analytics platform for the Indian Energy Exchange (IEX).

## 🎯 Overview

This application converts client-specific Excel trading reports into a standardized universal JSON schema, enabling:

- ✅ **Standardization**: All client data in one universal format
- ✅ **Scalability**: Easy to add new clients with different Excel formats
- ✅ **Data Quality**: Automatic validation and error checking
- ✅ **Analytics Ready**: Prepared for ML/forecasting features

## 📁 Project Structure

```
Power-Trading-application/
├── parsers/                    # Excel parsers for different formats
│   ├── __init__.py
│   └── gdam_template_parser.py # GDAM format parser
│
├── schemas/                    # Universal schema definitions
│   └── universal_trading_schema_v1.json
│
├── output/                     # Parsed JSON outputs
│   └── mellbro_parsed_data.json
│
├── templates/                  # Future: Template registry
├── validation/                 # Future: Schema validators
├── tests/                      # Future: Unit tests
│
├── run_parser.py               # Main CLI application
├── demo.py                     # Demo script
├── setup.py                    # Package setup
└── requirements.txt            # Dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Run Demo

```bash
python demo.py
```

### 3. Parse Your Own File

```bash
python run_parser.py <path_to_excel_file> [client_id]
```

**Example:**
```bash
python run_parser.py data/trading_report.xls mellbro-001
```

## 💻 Usage

### Command Line

```bash
# Basic usage
python run_parser.py input.xls

# With custom client ID
python run_parser.py input.xls my-client-123
```

### Python Code

```python
from parsers import GDAMTemplateParser

# Initialize parser
parser = GDAMTemplateParser(client_id="mellbro-001")

# Parse Excel file
data = parser.parse_excel("trading_report.xls")

# Access parsed data
print(f"Trading Date: {data['metadata']['trading_date']}")
print(f"Total Buy Transactions: {data['summary']['total_buy_transactions']}")
print(f"Net Amount: ₹{data['summary']['net_amount']:,.2f}")

# Save to file
import json
with open('output.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## 📊 Data Schema

### Metadata
- Trading date, delivery date
- Entity information (ID, name)
- Portfolio details (code, name)

### Buy Transactions
- 96 time blocks (15-minute intervals)
- Quantity (MW), Rate (₹/MWh), Amount (₹)

### Sell Transactions
- Solar, Non-solar, Hydro quantities
- Time blocks and rates

### Charges
- NLDC, CTU, STU transmission charges
- Scheduling charges
- GST (IGST, SGST, CGST)

### Summary
- Total quantities and amounts
- Transaction counts
- Net position

## 🔧 Supported Formats

Currently supported:
- **GDAM (Green Day-Ahead Market)** - IEX Format

Coming soon:
- Regular DAM (Day-Ahead Market)
- TAM (Term-Ahead Market)
- RTM (Real-Time Market)

## 📈 Next Steps

1. **API Layer** - FastAPI backend for file uploads
2. **Database Integration** - InfluxDB (time-series) + PostgreSQL (metadata)
3. **Frontend** - C# WPF Desktop application
4. **ML Features** - Price forecasting, demand prediction
5. **Validation** - Enhanced schema validation
6. **Testing** - Comprehensive unit tests

## 🛠️ Development

### Adding New Templates

1. Create parser in `parsers/` (e.g., `dam_parser.py`)
2. Inherit from base template pattern
3. Implement required methods
4. Output to universal schema

### Running Tests

```bash
# Coming soon
pytest tests/
```

## 📝 License

See LICENSE file for details.

## 👤 Author

DataScience-beginner

---

**Status**: ✅ Production Ready - Core parsing functionality complete
