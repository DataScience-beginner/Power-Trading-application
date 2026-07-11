-- Energy Schedule Daily Summary Table
CREATE TABLE IF NOT EXISTS energy_schedule_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calculation_date DATE UNIQUE NOT NULL,
    dor_date DATE NOT NULL,
    sch_date DATE NOT NULL,
    month_year TEXT NOT NULL,  -- 'JAN_2026'
    year TEXT NOT NULL,  -- '2026'
    files_used TEXT,  -- '2+2: GDAM,DAM'
    
    -- Summary values from Excel
    total_energy_savings REAL,
    total_cost REAL,
    total_deviation REAL,
    ctu_losses_pct REAL,
    ctu_charges REAL,
    nldc_app_fee REAL,
    
    -- Excel reference
    excel_file_path TEXT,
    calculation_status TEXT DEFAULT 'pending',  -- pending, calculating, completed, error
    error_message TEXT,
    calculated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Energy Schedule Hourly Breakdown Table (96 time slots)
CREATE TABLE IF NOT EXISTS energy_schedule_hourly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daily_schedule_id INTEGER NOT NULL,
    time_slot TEXT NOT NULL,  -- '00:00 - 00:15'
    slot_number INTEGER,  -- 1-96
    
    -- SCH data
    consumption_after_losses REAL,
    scheduled_value REAL,
    
    -- DOR data (if applicable)
    actual_value REAL,
    
    -- Calculated
    deviation REAL,
    deviation_pct REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (daily_schedule_id) REFERENCES energy_schedule_daily(id) ON DELETE CASCADE
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_energy_schedule_date ON energy_schedule_daily(calculation_date);
CREATE INDEX IF NOT EXISTS idx_energy_schedule_month ON energy_schedule_daily(month_year);
CREATE INDEX IF NOT EXISTS idx_energy_schedule_year ON energy_schedule_daily(year);
CREATE INDEX IF NOT EXISTS idx_hourly_schedule ON energy_schedule_hourly(daily_schedule_id);
