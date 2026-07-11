"""
DOR Energy Schedule Parser
--------------------------
Extracts summary data from DOR (Daily Obligation Report) files for Energy Schedule calculations.
Handles GDAM, DAM, and RTM market types.

Required fields for Energy Schedule (rows 4-6):
- NLDC Application Fee
- CTU Transmission Charges (Injection + Drawal)
- Total Cost
- Scheduled Quantity (for CTU Loss % calculation)

Author: Power Trading Application
Date: 2026-01-16
"""

import pandas as pd
import os
import re
from datetime import datetime
import json


class DOR_EnergyScheduleParser:
    """
    Parses DOR files to extract summary data for Energy Schedule calculations.
    Supports GDAM, DAM, and RTM market types.
    """
    
    def __init__(self, file_path):
        """
        Initialize parser with file path.
        
        Args:
            file_path (str): Path to the DOR Excel file (.xls or .xlsx)
        """
        self.file_path = file_path
        self.df = None
        self.market_type = None  # GDAM, DAM, or RTM
        
    def parse(self):
        """
        Main parsing method. Converts .xls to .xlsx if needed, then extracts all fields.
        
        Returns:
            dict: Structured data with summary fields and metadata
        """
        # Convert .xls/.XLS to .xlsx if needed
        if self.file_path.lower().endswith('.xls') and not self.file_path.endswith('.xlsx'):
            self.file_path = self._convert_xls_to_xlsx()
            
        # Read Excel file
        self.df = pd.read_excel(self.file_path, header=None, engine='openpyxl')
        
        # Detect market type from filename
        self.market_type = self._detect_market_type()
        
        # Extract all fields
        result = {
            "metadata": self._extract_metadata(),
            "summary": {
                "nldc_application_fee": self._extract_nldc_fee(),
                "ctu_transmission_charges": self._extract_ctu_charges(),
                "total_cost": self._extract_total_cost(),
                "scheduled_quantity": self._extract_scheduled_quantity(),
                "other_charges": self._extract_other_charges()
            },
            "rate_info": self._extract_rate_info()
        }
        
        return result
    
    def _convert_xls_to_xlsx(self):
        """
        Convert .xls file to .xlsx using LibreOffice headless mode.
        
        Returns:
            str: Path to converted .xlsx file
        """
        import subprocess
        
        output_dir = "/tmp"
        base_name = os.path.basename(self.file_path)
        
        # Run LibreOffice conversion
        result = subprocess.run([
            'soffice', '--headless', '--convert-to', 'xlsx',
            '--outdir', output_dir, self.file_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"LibreOffice conversion warning: {result.stderr}")
        
        # Return path to converted file (handle both .xls and .XLS extensions)
        converted_file = os.path.join(output_dir, base_name.replace('.xls', '.xlsx').replace('.XLS', '.xlsx'))
        
        # Verify the file exists
        if not os.path.exists(converted_file):
            raise FileNotFoundError(f"Converted file not found: {converted_file}")
        
        return converted_file
    
    def _detect_market_type(self):
        """
        Detect market type from filename.
        
        Returns:
            str: 'GDAM', 'DAM', or 'RTM'
        """
        filename = os.path.basename(self.file_path).upper()
        
        if 'GDAM' in filename:
            return 'GDAM'
        elif 'RTM' in filename:
            return 'RTM'
        elif 'DAM' in filename or 'DOR' in filename:
            return 'DAM'
        else:
            return 'UNKNOWN'
    
    def _extract_metadata(self):
        """
        Extract metadata from DOR file header.
        
        Returns:
            dict: Metadata including portfolio, entity, trading date
        """
        metadata = {
            "market_type": self.market_type,
            "file_name": os.path.basename(self.file_path),
            "parsed_at": datetime.now().isoformat()
        }
        
        # Extract from filename pattern: IEX120126DOR_NPT0027_KA0_Entity_Name
        filename = os.path.basename(self.file_path)
        
        # Extract trading date (e.g., 120126 = 12-Jan-2026)
        date_match = re.search(r'IEX(\d{6})DOR', filename)
        if date_match:
            date_str = date_match.group(1)
            # Parse DDMMYY format
            day = int(date_str[:2])
            month = int(date_str[2:4])
            year = 2000 + int(date_str[4:6])
            metadata["trading_date"] = f"{year:04d}-{month:02d}-{day:02d}"
        
        # Extract portfolio code (e.g., NPT0027_KA0)
        portfolio_match = re.search(r'_(NPT\d+_[A-Z0-9]+)_', filename)
        if portfolio_match:
            metadata["portfolio_code"] = portfolio_match.group(1)
        
        # Extract entity name from remaining filename
        entity_match = re.search(r'NPT\d+_[A-Z0-9]+_(.+?)(?:_parsed|\.xls)', filename)
        if entity_match:
            metadata["entity_name"] = entity_match.group(1).replace('_', ' ')
        
        return metadata
    
    def _extract_nldc_fee(self):
        """
        Extract NLDC Application Fee from row 14, column 12.
        
        Returns:
            float: NLDC Application Fee value
        """
        try:
            # Row 14 (0-indexed = 13), Column 12 (0-indexed = 11)
            value = self.df.iloc[14, 12]
            # Handle values with asterisks (e.g., "-200.00*")
            if pd.notna(value):
                value_str = str(value).replace('*', '').replace(',', '').strip()
                return float(value_str)
            return 0.0
        except (IndexError, ValueError):
            return 0.0
    
    def _extract_ctu_charges(self):
        """
        Extract CTU Transmission Charges from row 15, column 12.
        Also includes injection and drawal charges breakdown.
        
        Returns:
            dict: CTU charges with total, injection, and drawal components
        """
        try:
            # Row 15 (0-indexed = 14), Column 12 (0-indexed = 11)
            total_value = self.df.iloc[15, 12]
            if pd.notna(total_value):
                total = float(str(total_value).replace('*', '').replace(',', '').strip())
            else:
                total = 0.0
            
            # Extract rate info from formula section (rows 34-35)
            injection_rate = 0.0
            drawal_rate = 0.0
            
            # Row 34: Injection CTU rate
            if len(self.df) > 33:
                injection_text = str(self.df.iloc[33, 2]) if pd.notna(self.df.iloc[33, 2]) else ''
                injection_match = re.search(r'`\s*([\d.,]+)', injection_text)
                if injection_match:
                    injection_rate = float(injection_match.group(1).replace(',', ''))
            
            # Row 35: Drawal CTU rate
            if len(self.df) > 34:
                drawal_text = str(self.df.iloc[34, 2]) if pd.notna(self.df.iloc[34, 2]) else ''
                drawal_match = re.search(r'`\s*([\d.,]+)', drawal_text)
                if drawal_match:
                    drawal_rate = float(drawal_match.group(1).replace(',', ''))
            
            return {
                "total": total,
                "injection_rate_per_mw_timeblock": injection_rate,
                "drawal_rate_per_mw_timeblock": drawal_rate
            }
        except (IndexError, ValueError):
            return {
                "total": 0.0,
                "injection_rate_per_mw_timeblock": 0.0,
                "drawal_rate_per_mw_timeblock": 0.0
            }
    
    def _extract_total_cost(self):
        """
        Extract total cost from row 28, column 12.
        
        Returns:
            float: Total cost value
        """
        try:
            # Row 28 (0-indexed = 27), Column 12 (0-indexed = 11)
            value = self.df.iloc[28, 12]
            if pd.notna(value):
                return float(str(value).replace('*', '').replace(',', '').strip())
            return 0.0
        except (IndexError, ValueError):
            return 0.0
    
    def _extract_scheduled_quantity(self):
        """
        Extract total scheduled quantity (buy transactions).
        This is needed for CTU Loss % calculation.
        
        Returns:
            float: Total scheduled quantity in MWh
        """
        # In DOR files, scheduled quantity is typically in the transaction section
        # For now, we'll extract from the summary if available
        # Otherwise, this would come from the detailed transaction parsing
        
        # Check if there's a total quantity field
        # This might be in different locations depending on DOR format
        # For now, return 0 as placeholder - will be calculated from transactions
        return 0.0
    
    def _extract_other_charges(self):
        """
        Extract other charges (NLDC S&O, STU, SLDC, Fees).
        
        Returns:
            dict: Other charges breakdown
        """
        charges = {}
        
        def clean_value(val):
            """Helper to clean values with asterisks and commas"""
            if pd.notna(val):
                return float(str(val).replace('*', '').replace(',', '').strip())
            return 0.0
        
        try:
            # Row 17: NLDC Scheduling & Operating Charges - Sell
            charges["nldc_scheduling_operating_sell"] = clean_value(self.df.iloc[17, 12])
            
            # Row 18: STU Transmission Charges
            charges["stu_transmission_charges"] = clean_value(self.df.iloc[18, 12])
            
            # Row 21: SLDC Scheduling Charges
            charges["sldc_scheduling_charges"] = clean_value(self.df.iloc[21, 12])
            
            # Row 23: Fees
            charges["fees"] = clean_value(self.df.iloc[23, 12])
            
        except (IndexError, ValueError):
            pass
        
        return charges
    
    def _extract_rate_info(self):
        """
        Extract rate information from formula section (rows 33-38).
        
        Returns:
            dict: Rate information for various charges
        """
        rate_info = {}
        
        try:
            # Row 33: NLDC Application Fee formula
            if len(self.df) > 32:
                nldc_fee_text = str(self.df.iloc[32, 2]) if pd.notna(self.df.iloc[32, 2]) else ''
                nldc_match = re.search(r'`\s*([\d.,]+)', nldc_fee_text)
                if nldc_match:
                    rate_info["nldc_base_fee"] = float(nldc_match.group(1).replace(',', ''))
                
                portfolio_match = re.search(r'(\d+)\s*\)', nldc_fee_text)
                if portfolio_match:
                    rate_info["successful_portfolios"] = int(portfolio_match.group(1))
            
            # Row 36: NLDC S&O Charges - Buy
            if len(self.df) > 35:
                nldc_so_text = str(self.df.iloc[35, 2]) if pd.notna(self.df.iloc[35, 2]) else ''
                nldc_so_match = re.search(r'`([\d.]+)', nldc_so_text)
                if nldc_so_match:
                    rate_info["nldc_so_rate_per_mwh"] = float(nldc_so_match.group(1))
                    
        except (IndexError, ValueError):
            pass
        
        return rate_info


def main():
    """
    Test the parser with sample DOR files.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python DOR_EnergySchedule_Parser.py <path_to_dor_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"\n{'='*80}")
    print(f"DOR Energy Schedule Parser - Testing")
    print(f"{'='*80}\n")
    
    # Parse file
    parser = DOR_EnergyScheduleParser(file_path)
    result = parser.parse()
    
    # Print results
    print(json.dumps(result, indent=2))
    
    # Save to output directory
    output_dir = "/workspaces/Power-Trading-application/output"
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.basename(file_path).replace('.xls', '').replace('.xlsx', '')
    output_file = os.path.join(output_dir, f"{base_name}_energy_schedule_parsed.json")
    
    with open(output_file, 'w') as f:
        json.dump(result, indent=2, fp=f)
    
    print(f"\n{'='*80}")
    print(f"Output saved to: {output_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
