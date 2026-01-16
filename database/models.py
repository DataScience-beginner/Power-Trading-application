"""
Database Models for Power Trading Application

These are the TABLE DEFINITIONS. Each class represents a database table.
SQLAlchemy ORM automatically converts these Python classes into SQL tables.

Hierarchy:
  CLIENT (e.g., "Grasim Industries")
    └─> PORTFOLIO (e.g., "NPT0019_TN0")
          └─> DAILY_FILE (6 files per day: 3 DOR + 3 SCH)
                └─> TRANSACTION (96 time slots each)
                
  MONTHLY_CALCULATION (stores calculation results, 31 days per month)
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from database.config import Base
from datetime import datetime
import enum

# ==================== ENUMS ====================
# Enums define allowed values for certain fields

class ReportMainCategory(str, enum.Enum):
    """Main report categories"""
    DOR = "DOR"  # Daily Obligation Report
    SCH = "SCH"  # Scheduling Report

class ReportSubCategory(str, enum.Enum):
    """Sub report categories"""
    GDAM = "GDAM"  # Green Day-Ahead Market
    RTM = "RTM"    # Real-Time Market
    DAM = "DAM"    # Day-Ahead Market (no GDAM/RTM keyword)

class TransactionType(str, enum.Enum):
    """Transaction types"""
    BUY = "buy"
    SELL = "sell"
    SCHEDULING = "scheduling"


# ==================== TABLE 1: CLIENTS ====================
class Client(Base):
    """
    Stores client/entity information
    Example: Grasim Industries, Mellbro Sugars
    """
    __tablename__ = "clients"
    
    # Primary key - unique ID for each client
    id = Column(Integer, primary_key=True, index=True)
    
    # Client details
    entity_id = Column(String, unique=True, index=True)  # e.g., "NPT0019"
    entity_name = Column(String, index=True)              # e.g., "Grasim Industries Limited"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships - one client has many portfolios
    portfolios = relationship("Portfolio", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name={self.entity_name})>"


# ==================== TABLE 2: PORTFOLIOS ====================
class Portfolio(Base):
    """
    Stores portfolio information for each client
    Example: NPT0019_TN0, NPT0027_KA0
    One client can have multiple portfolios
    """
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key linking to clients table
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Portfolio details
    portfolio_code = Column(String, unique=True, index=True)  # e.g., "NPT0019_TN0"
    portfolio_name = Column(String)                           # e.g., "Tamil Nadu Portfolio"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    client = relationship("Client", back_populates="portfolios")
    daily_files = relationship("DailyFile", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, code={self.portfolio_code})>"


# ==================== TABLE 3: DAILY FILES ====================
class DailyFile(Base):
    """
    Stores information about uploaded files
    Each portfolio gets 6 files per day:
      - 3 DOR files: DOR-GDAM, DOR-RTM, DOR-DAM
      - 3 SCH files: SCH-GDAM, SCH-RTM, SCH-DAM
    """
    __tablename__ = "daily_files"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key linking to portfolios
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    # File details
    trading_date = Column(Date, index=True, nullable=False)
    delivery_date = Column(Date, index=True)
    main_category = Column(String)  # DOR or SCH
    sub_category = Column(String)   # GDAM, RTM, or DAM
    report_type = Column(String, index=True)  # Combined: "DOR-GDAM", "SCH-RTM", etc.
    
    # Original file info
    original_filename = Column(String)
    file_path = Column(String)  # Where the Excel file is stored
    
    # Parsed data summary (stored as JSON for flexibility)
    summary = Column(JSON)  # Stores the summary dict from parser
    charges = Column(JSON)  # Stores charges dict (for DOR files)
    file_metadata = Column(JSON) # Stores full metadata (renamed from 'metadata' which is reserved)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.now)
    parsed_at = Column(DateTime)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="daily_files")
    transactions = relationship("Transaction", back_populates="daily_file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DailyFile(id={self.id}, type={self.report_type}, date={self.trading_date})>"


# ==================== TABLE 4: TRANSACTIONS ====================
class Transaction(Base):
    """
    Stores individual transaction data (time slot level)
    Each file has 96 transactions (one per 15-minute time slot)
    
    For DOR files: stores buy/sell transactions
    For SCH files: stores scheduling data (regional + interface)
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key linking to daily_files
    daily_file_id = Column(Integer, ForeignKey("daily_files.id"), nullable=False)
    
    # Time slot information
    date = Column(Date, index=True, nullable=False)
    time_slot = Column(String)  # "00:00 - 00:15"
    time_block_start = Column(DateTime, index=True)
    time_block_end = Column(DateTime)
    
    # Transaction type
    transaction_type = Column(String)  # "buy", "sell", "scheduling"
    
    # === BUY TRANSACTION FIELDS ===
    quantity_mw = Column(Float, default=0.0)
    rate_per_mwh = Column(Float, default=0.0)
    amount = Column(Float, default=0.0)
    
    # === SELL TRANSACTION FIELDS ===
    solar_quantity_mw = Column(Float, default=0.0)
    non_solar_quantity_mw = Column(Float, default=0.0)
    hydro_quantity_mw = Column(Float, default=0.0)
    total_quantity_mw = Column(Float, default=0.0)
    
    # === SCHEDULING TRANSACTION FIELDS ===
    # Regional (without losses)
    regional_injection_mw = Column(Float, default=0.0)
    regional_drawal_mw = Column(Float, default=0.0)
    regional_net_mw = Column(Float, default=0.0)
    
    # Interface (after losses)
    interface_injection_mw = Column(Float, default=0.0)
    interface_drawal_mw = Column(Float, default=0.0)
    interface_net_mw = Column(Float, default=0.0)
    
    # Losses
    injection_losses_mw = Column(Float, default=0.0)
    drawal_losses_mw = Column(Float, default=0.0)
    total_losses_mw = Column(Float, default=0.0)
    net_scheduled_mw = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    daily_file = relationship("DailyFile", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, slot={self.time_slot})>"


# ==================== TABLE 5: MONTHLY CALCULATIONS ====================
class MonthlyCalculation(Base):
    """
    Stores monthly calculation results
    One sheet per month can store 31 days of calculations
    
    This is where you'll store the results from your predefined calculation Excel sheet.
    The calculation_data field stores the full calculation as JSON.
    """
    __tablename__ = "monthly_calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to portfolio
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    # Month information
    year = Column(Integer, index=True, nullable=False)
    month = Column(Integer, index=True, nullable=False)  # 1-12
    day = Column(Integer, index=True, nullable=False)    # 1-31
    calculation_date = Column(Date, index=True, nullable=False)
    
    # Calculation type/name
    calculation_type = Column(String, index=True)  # e.g., "daily_summary", "variance_analysis"
    
    # Calculation results (stored as JSON for flexibility)
    # This can store complex nested calculations from your Excel sheet
    calculation_data = Column(JSON)
    
    # Summary metrics (for quick queries)
    total_buy_mwh = Column(Float, default=0.0)
    total_sell_mwh = Column(Float, default=0.0)
    total_scheduled_mwh = Column(Float, default=0.0)
    net_position = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    net_profit_loss = Column(Float, default=0.0)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship
    portfolio = relationship("Portfolio")
    
    def __repr__(self):
        return f"<MonthlyCalculation(id={self.id}, date={self.calculation_date}, type={self.calculation_type})>"


# ==================== TABLE 6: ENERGY SCHEDULE MONTHS ====================
class EnergyScheduleMonth(Base):
    """
    Stores monthly Energy Schedule sheets
    One record per portfolio per month
    
    Each month maintains a separate sheet with day-wise DOR + SCH data
    and calculated energy savings
    """
    __tablename__ = "energy_schedule_months"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to portfolio
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    # Month information
    year = Column(Integer, index=True, nullable=False)
    month = Column(Integer, index=True, nullable=False)  # 1-12
    month_name = Column(String)  # e.g., "January 2026"
    
    # Summary metrics for the month (aggregated from daily entries)
    total_scheduled_mwh = Column(Float, default=0.0)
    total_consumption_after_losses_mwh = Column(Float, default=0.0)
    total_energy_savings_mwh = Column(Float, default=0.0)
    total_gdam_cost = Column(Float, default=0.0)
    total_dam_cost = Column(Float, default=0.0)
    total_rtm_cost = Column(Float, default=0.0)
    average_ctu_losses_percent = Column(Float, default=0.0)
    
    # Status tracking
    days_completed = Column(Integer, default=0)  # How many days have data
    is_complete = Column(Integer, default=0)  # 1 if all days in month are filled
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    portfolio = relationship("Portfolio")
    daily_entries = relationship("EnergyScheduleDay", back_populates="month_sheet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EnergyScheduleMonth(id={self.id}, portfolio={self.portfolio_id}, month={self.month_name})>"


# ==================== TABLE 7: ENERGY SCHEDULE DAILY ENTRIES ====================
class EnergyScheduleDay(Base):
    """
    Stores daily Energy Schedule data and calculations
    One record per day per month sheet
    
    Contains:
    - DOR summary data (GDAM, DAM, RTM) - rows 4, 5, 6 in Excel
    - SCH consumption data (96 time slots) - timestamped rows in Excel
    - Calculated fields (CTU Losses %, Energy Savings, etc.)
    """
    __tablename__ = "energy_schedule_days"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to month sheet
    month_sheet_id = Column(Integer, ForeignKey("energy_schedule_months.id"), nullable=False)
    
    # Date information
    trading_date = Column(Date, index=True, nullable=False)
    day_of_month = Column(Integer)  # 1-31
    
    # === DOR SUMMARY DATA (from DOR_EnergySchedule_Parser) ===
    # Row 4: GDAM data
    gdam_nldc_fee = Column(Float, default=0.0)
    gdam_ctu_charges = Column(Float, default=0.0)
    gdam_cost = Column(Float, default=0.0)
    gdam_scheduled_quantity_mwh = Column(Float, default=0.0)
    gdam_other_charges = Column(JSON)  # STU, SLDC, Fees as JSON
    
    # Row 5: DAM data
    dam_nldc_fee = Column(Float, default=0.0)
    dam_ctu_charges = Column(Float, default=0.0)
    dam_cost = Column(Float, default=0.0)
    dam_scheduled_quantity_mwh = Column(Float, default=0.0)
    dam_other_charges = Column(JSON)
    
    # Row 6: RTM data
    rtm_nldc_fee = Column(Float, default=0.0)
    rtm_ctu_charges = Column(Float, default=0.0)
    rtm_cost = Column(Float, default=0.0)
    rtm_scheduled_quantity_mwh = Column(Float, default=0.0)
    rtm_other_charges = Column(JSON)
    
    # === SCH CONSUMPTION DATA (from SCH_Energy_Schedule_Parser) ===
    # Timestamped rows: 96 time slots stored as JSON array
    consumption_after_losses_timeslots = Column(JSON)  # Array of 96 values
    total_consumption_after_losses_mwh = Column(Float, default=0.0)
    regional_loss_percent = Column(Float, default=0.0)
    state_loss_percent = Column(Float, default=0.0)
    combined_loss_percent = Column(Float, default=0.0)
    
    # === CALCULATED FIELDS (Stories 2.1-2.4) ===
    # Total scheduled quantity (sum of GDAM + DAM + RTM)
    total_scheduled_mwh = Column(Float, default=0.0)
    
    # CTU Losses % = (Scheduled - Consumption After Losses) / Scheduled * 100
    ctu_losses_percent = Column(Float, default=0.0)
    ctu_losses_mwh = Column(Float, default=0.0)
    
    # Energy Savings (MWh)
    energy_savings_mwh = Column(Float, default=0.0)
    
    # Total charges
    total_nldc_fee = Column(Float, default=0.0)
    total_ctu_charges = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Data completeness flags
    has_gdam_data = Column(Integer, default=0)  # 1 if GDAM file uploaded
    has_dam_data = Column(Integer, default=0)   # 1 if DAM file uploaded
    has_rtm_data = Column(Integer, default=0)   # 1 if RTM file uploaded
    has_sch_data = Column(Integer, default=0)   # 1 if SCH file uploaded
    is_complete = Column(Integer, default=0)     # 1 if all 4 files present and calculated
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    calculated_at = Column(DateTime)  # When calculations were performed
    
    # Relationships
    month_sheet = relationship("EnergyScheduleMonth", back_populates="daily_entries")
    
    def __repr__(self):
        return f"<EnergyScheduleDay(id={self.id}, date={self.trading_date}, complete={self.is_complete})>"
