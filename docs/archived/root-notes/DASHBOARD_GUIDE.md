# 📊 Power Trading Analytics Dashboard

## Overview

A comprehensive web-based analytics dashboard for Power Trading clients with admin management features.

## 🎯 Features

### For End Users (Clients)

#### 1. **Multi-Portfolio Navigation**
- View all portfolios in one place
- Switch between different portfolios easily
- Sidebar navigation for quick access

#### 2. **Time-Scale Analysis**
- **Daily View**: Day-by-day breakdown
- **Weekly View**: Week-over-week trends
- **Monthly View**: Month analysis (default)
- **Quarterly View**: Quarter-by-quarter comparison
- **Yearly View**: Year-over-year analysis

#### 3. **DOR vs SCH Comparison** (Lead vs Lag Indicators)
- **DOR (Lead Indicator)**: Planned/Traded data
  - Shows what was intended/planned
  - Forward-looking metrics
  - Trading commitments
  
- **SCH (Lag Indicator)**: Scheduled/Actual data
  - Shows what actually happened
  - Historical execution
  - Real scheduled amounts

- **Visual Comparison Charts**:
  - Side-by-side hourly comparison
  - Variance analysis
  - Deviation tracking

#### 4. **Analytics Dashboards**

**Summary Cards:**
- DOR Files count (planned trades)
- SCH Files count (actual schedules)
- Total transactions (96 time slots/day)
- Net amount (revenue/cost)

**Interactive Charts:**
- **DOR vs SCH Timeline**: Line chart showing planned vs actual
- **Buy vs Sell Distribution**: Doughnut chart of transaction types
- **Peak Hours Analysis**: Bar chart of peak trading hours
- **Hourly Distribution**: Average MW by time period

#### 5. **Transaction Explorer**
- Full transaction table with filters
- Search by date, portfolio, type
- Sort by any column
- Export to CSV capability

#### 6. **Date Range Selection**
- Month picker for quick monthly view
- Custom date range selector
- Pre-defined periods (MTD, QTD, YTD)

### For Admins Only

#### 7. **Admin Mode Toggle**
- Hidden toggle in top-right corner
- Enable to access admin features
- Warning notification when enabled

#### 8. **Edit Transaction Values**
- Click "Edit" button on any transaction
- Modify:
  - Quantity (MW)
  - Rate (₹/MWh)
  - Amount (₹)
- Instant database update
- Audit trail maintained

#### 9. **File Upload Management**
- Drag & drop interface
- Bulk file upload
- Report type selection (DOR/SCH)
- Sub-type selection (GDAM/RTM/DAM)
- Upload progress tracking
- Success/failure notifications

## 🚀 Getting Started

### 1. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8000/frontend/dashboard.html
```

### 2. Default View

You'll see:
- **Sidebar**: Navigation and portfolio list
- **Top Bar**: Filters and admin toggle
- **Main Area**: Dashboard with stats and charts
- **Bottom**: Transaction table

### 3. Navigating Portfolios

**Option 1 - Dropdown:**
- Use "Portfolio" dropdown in top bar
- Select specific portfolio or "All Portfolios"

**Option 2 - Sidebar:**
- Click portfolio name in sidebar
- Instant filtering

### 4. Changing Time Periods

**Monthly View:**
1. Select "Monthly" from "View Type" dropdown
2. Choose month from month picker
3. Click "Apply Filters"

**Custom Range:**
1. Select start date
2. Select end date
3. Click "Apply Filters"

**Quick Views:**
- Daily: See today's data
- Weekly: Current week
- Quarterly: Current quarter
- Yearly: Current year

### 5. Understanding DOR vs SCH

**Reading the Charts:**
- **Purple Line** = DOR (what was planned)
- **Pink Line** = SCH (what was scheduled)
- **Gap between lines** = Variance/Deviation

**Interpretation:**
- DOR higher than SCH = Over-planned (couldn't execute all)
- SCH higher than DOR = Over-scheduled (scheduled more than planned)
- Lines matching = Perfect execution

### 6. Using Admin Features

**Enable Admin Mode:**
1. Click the toggle switch in top-right (off by default)
2. Switch turns orange when enabled
3. Alert confirms admin mode active

**Edit a Transaction:**
1. Ensure admin mode is ON
2. Find transaction in table
3. Click "Edit" button (visible only in admin mode)
4. Modal opens with editable fields
5. Modify values
6. Click "Save Changes"
7. Database updates instantly

**Upload Files:**
1. Click "Upload Files" in sidebar
2. Select Report Type (DOR or SCH)
3. Select Sub Type (GDAM, RTM, or DAM)
4. Drag files or click to browse
5. Watch upload progress
6. Success confirmation per file

## 📈 Analytics Explained

### Summary Metrics

| Metric | Description | Insight |
|--------|-------------|---------|
| DOR Files | Count of DOR reports | Trading activity planned |
| SCH Files | Count of SCH reports | Actual schedules executed |
| Total Transactions | 96 time slots × days × files | Overall trading volume |
| Net Amount | Sum of all amounts | Revenue/Cost balance |

### Charts

#### 1. DOR vs SCH Comparison (Line Chart)
- **X-axis**: Time (hourly)
- **Y-axis**: Quantity (MW)
- **Purpose**: Compare planned vs actual execution
- **Use**: Identify execution gaps

#### 2. Buy vs Sell Distribution (Doughnut Chart)
- **Red**: Buy transactions
- **Green**: Sell transactions
- **Purpose**: Transaction type split
- **Use**: Portfolio balance analysis

#### 3. Peak Hours Analysis (Bar Chart)
- **X-axis**: Time blocks (4-hour intervals)
- **Y-axis**: Average MW
- **Purpose**: Identify peak trading hours
- **Use**: Resource planning

## 🔍 Use Cases

### Scenario 1: Monthly Performance Review
```
1. Select your portfolio
2. Choose "Monthly" view
3. Select last month
4. Click "Apply Filters"
5. Review:
   - DOR vs SCH variance
   - Net amount achieved
   - Peak hours pattern
```

### Scenario 2: Compare Q1 vs Q2
```
1. Select "Quarterly" view
2. First, select Q1 dates
3. Note key metrics
4. Then select Q2 dates
5. Compare side-by-side
```

### Scenario 3: Fix Wrong Data (Admin)
```
1. Enable Admin Mode
2. Find incorrect transaction
3. Click "Edit"
4. Correct the values
5. Save changes
6. Verify update in table
```

### Scenario 4: Year-over-Year Analysis
```
1. Select "Yearly" view
2. Choose 2025
3. Export data
4. Choose 2026
5. Export data
6. Compare in Excel/analysis tool
```

## 🎨 Color Coding

| Color | Meaning | Used For |
|-------|---------|----------|
| 🟣 Purple | DOR | Lead indicator, planned trades |
| 🩷 Pink | SCH | Lag indicator, actual schedules |
| 🔴 Red | Buy | Purchase transactions |
| 🟢 Green | Sell | Sale transactions |
| 🔵 Blue | Info | General information |
| 🟡 Orange | Admin | Admin mode active |

## 📱 Responsive Design

The dashboard adapts to different screen sizes:
- **Desktop**: Full sidebar + main content
- **Tablet**: Collapsible sidebar
- **Mobile**: Stacked layout, hamburger menu

## 🔐 Security Notes

### Admin Mode
- **Not password-protected** (add authentication if needed)
- Currently a toggle switch
- All edits are logged in database
- Consider adding:
  - User authentication
  - Role-based access control
  - Edit history/audit log

### Recommendations
1. Host behind authentication layer (OAuth, SSO)
2. Add user roles (viewer, editor, admin)
3. Enable SSL/HTTPS in production
4. Implement rate limiting on edit endpoints

## 🛠️ Technical Details

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/clients` | GET | Load all clients |
| `/api/analytics/summary` | GET | Dashboard stats |
| `/api/transactions/all` | GET | Transaction list |
| `/api/analytics/dor-vs-sch` | GET | Comparison data |
| `/api/transactions/{id}` | PUT | Update transaction |
| `/api/upload` | POST | Upload files |

### Technologies
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js 4.4.0
- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📊 Data Refresh

- **Auto-refresh**: Not enabled (manual refresh only)
- **After Upload**: Automatic reload after 1 second
- **After Edit**: Immediate reload of transaction list
- **Manual**: Click "Apply Filters" button

## 💡 Tips & Tricks

1. **Quick Month Switch**: Use keyboard to navigate month picker
2. **Multi-Portfolio Compare**: Open dashboard in multiple tabs
3. **Export Before Edit**: Download data before making admin changes
4. **Peak Hours**: Check 7-10 AM and 6-9 PM for highest activity
5. **DOR vs SCH Gap**: If gap > 10%, investigate execution issues

## 🐛 Troubleshooting

### Charts Not Loading
- Check browser console for errors
- Ensure Chart.js CDN is accessible
- Verify API endpoints returning data

### No Data Showing
- Check date range selected
- Verify portfolio has uploaded files
- Ensure database has transactions

### Admin Edit Not Working
- Confirm admin mode is ON (toggle orange)
- Check network tab for API errors
- Verify transaction ID is valid

### Upload Fails
- Check file format (.xls or .xlsx)
- Verify file size < 50MB
- Ensure report type selected correctly

## 📚 Next Steps

### Planned Enhancements
1. Real-time updates via WebSockets
2. Custom dashboard widgets
3. Email/SMS alerts for thresholds
4. Machine learning predictions
5. Multi-user collaboration
6. Mobile app version
7. Advanced filtering (regex, custom queries)
8. Bookmark favorite views
9. Scheduled reports via email
10. Data validation rules

---

## 🎓 Understanding Lead vs Lag Indicators

### Lead Indicator (DOR)
**Definition**: Predictive measures that change before the event
**Example**: DOR shows planned trades for tomorrow
**Use**: 
- Planning resources
- Forecasting revenue
- Risk management
- Strategy decisions

### Lag Indicator (SCH)
**Definition**: Measures that confirm what has happened
**Example**: SCH shows what was actually scheduled
**Use**:
- Performance evaluation
- Execution accuracy
- Historical analysis
- Variance investigation

### Why Both Matter
- **DOR** tells you where you're going
- **SCH** tells you where you've been
- **Gap** tells you how well you executed
- **Together** enable continuous improvement

---

**Built with ❤️ for Power Trading Analytics**

Need help? Contact your system administrator.
