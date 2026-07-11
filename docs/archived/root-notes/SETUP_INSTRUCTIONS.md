# Power Trading Application - Quick Start Guide

## 🚀 One-Command Setup

This application can be set up and run with **just one command**!

---

## For Windows Users

### Prerequisites (One-time Setup)
1. **Install Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation
   
2. **Install Node.js 16+**
   - Download from: https://nodejs.org/
   - Use the LTS (Long Term Support) version

3. **Install Git Bash** (Optional but recommended)
   - Download from: https://git-scm.com/downloads
   - Provides bash terminal for Windows

### Run the Application

**Option 1: Using Git Bash (Recommended)**
```bash
./bootstrap.sh
```

**Option 2: Using PowerShell**
```powershell
# Coming soon - use Git Bash for now
```

**Option 3: Using Windows CMD**
```cmd
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
# In another terminal:
cd frontend-react
npm run dev
```

---

## For macOS/Linux Users

### Prerequisites
1. **Python 3.8+** (usually pre-installed)
   ```bash
   python3 --version
   ```

2. **Node.js 16+**
   - macOS: `brew install node`
   - Linux: `sudo apt install nodejs npm`

### Run the Application

**One command to rule them all:**
```bash
chmod +x bootstrap.sh
./bootstrap.sh
```

That's it! The script will:
- Install all dependencies
- Set up the database
- Load sample data
- Start both servers
- Open at http://localhost:3000

---

## What Happens When You Run Bootstrap?

```
1. Checks Python & Node.js installation ✓
2. Installs Python packages (FastAPI, SQLAlchemy, etc.) ✓
3. Installs Node.js packages (React, Material-UI, etc.) ✓
4. Creates database and loads 2,072 sample transactions ✓
5. Starts Backend API on port 8000 ✓
6. Starts Frontend Dashboard on port 3000 ✓
```

⏱️ **First-time setup: ~2-3 minutes**  
⏱️ **Subsequent runs: ~10 seconds**

---

## Accessing the Dashboard

Once bootstrap completes, open your browser:

```
http://localhost:3000
```

You'll see the **Power Trading Dashboard** with:
- Dashboard tab (Statistics & Transactions)
- Energy Schedule tab (Hourly/Daily/Weekly/Monthly)
- Analytics tab (Market trends & Charts)
- Reports tab (Download PDF/Excel)

---

## Sample Data Included

The application comes with realistic sample data:

- **Client**: Mellbro Sugars Pvt Ltd (NPT0027_KA0)
- **Date Range**: January 1-15, 2026
- **Total Transactions**: 2,072 records
- **Markets**: GDAM, DAM, RTM
- **Report Types**: DOR (Daily Obligation), SCH (Scheduling)

This lets you test all features immediately without uploading files.

---

## Stopping the Application

To stop both servers:
```bash
./shutdown.sh
```

Or manually:
```bash
# Find and kill processes
lsof -ti:8000 | xargs kill -9  # Kill backend
lsof -ti:3000 | xargs kill -9  # Kill frontend
```

---

## Troubleshooting

### "Command not found: python3"
- **Windows**: Use `python` instead of `python3`
- **Solution**: Make sure Python is in your PATH

### "Port 8000 already in use"
- **Solution**: Run `./shutdown.sh` first, or manually kill the process:
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```

### "Port 3000 already in use"
- **Solution**: Same as above for port 3000

### "npm: command not found"
- **Solution**: Install Node.js from https://nodejs.org

### Database errors
- **Solution**: Delete `power_trading.db` and run bootstrap again

### Dependencies installation fails
- **Solution**: 
  ```bash
  # For Python
  pip install --upgrade pip
  pip install -r requirements.txt
  
  # For Node.js
  cd frontend-react
  rm -rf node_modules package-lock.json
  npm install
  ```

---

## Manual Setup (If Bootstrap Fails)

### Backend
```bash
# Install Python packages
pip install -r requirements.txt

# Initialize database
python init_database.py

# Load sample data
python upload_mock_reports.py

# Start backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (In another terminal)
```bash
cd frontend-react

# Install packages
npm install

# Start frontend
npm run dev
```

Then open http://localhost:3000

---

## Viewing Logs

**Backend logs:**
```bash
tail -f backend.log
```

**Frontend logs:**
```bash
tail -f frontend.log
```

**Check if servers are running:**
```bash
# Backend
curl http://localhost:8000/api/health

# Frontend
curl http://localhost:3000
```

---

## System Requirements

**Minimum:**
- Python 3.8+
- Node.js 16+
- 2 GB RAM
- 500 MB disk space

**Recommended:**
- Python 3.10+
- Node.js 18+
- 4 GB RAM
- 1 GB disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## Next Steps After Setup

1. **Explore the Dashboard**
   - Try different filters (client, market type, date range)
   - Switch between view modes (Hourly/Daily/Weekly/Monthly)
   - Download PDF and Excel reports

2. **Upload Your Own Data**
   - Use the upload feature to parse IEX Excel reports
   - Supports DOR (Daily Obligation) and SCH (Scheduling) formats

3. **Customize**
   - Add more clients/portfolios
   - Modify calculations in `database/energy_schedule_service.py`
   - Customize UI in `frontend-react/src/`

---

## Files Included

```
Power-Trading-application/
├── bootstrap.sh              # One-click setup script
├── shutdown.sh               # Stop all servers
├── requirements.txt          # Python dependencies
├── init_database.py          # Database setup
├── upload_mock_reports.py    # Load sample data
├── api/
│   ├── main.py              # FastAPI backend
│   └── report_generator.py  # PDF/Excel generation
├── database/
│   ├── models.py            # Database schema
│   └── services.py          # Business logic
├── frontend-react/
│   ├── package.json         # Node.js dependencies
│   └── src/                 # React application
└── parsers/
    ├── DOR_Parser.py        # DOR file parser
    └── SCH_Parser.py        # SCH file parser
```

---

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review log files (`backend.log`, `frontend.log`)
3. Ensure all prerequisites are installed
4. Try manual setup if bootstrap fails

---

## Summary

**For the impatient:**
```bash
# One command setup and run:
./bootstrap.sh

# Open browser:
http://localhost:3000

# Stop when done:
./shutdown.sh
```

That's it! Enjoy your Power Trading Dashboard! 🚀
