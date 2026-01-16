"""
Scheduling Report (SCH) Parser for IEX Trading Reports - FIXED VERSION
Handles scheduling data with regional periphery and interface point data
"""

import pandas as pd
import re
import uuid
import os
import subprocess
import tempfile
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
import json


class SCHTemplateParser:
    """
    Parser for IEX Scheduling Reports (SCH format)
    Template ID: SCH_IEX_V1
    """
    
    def __init__(self, client_id: str = None):
        self.template_id = "SCH_IEX_V1"
        self.template_version = "1.0.0"
        self.client_id = client_id or str(uuid.uuid4())
        
    def parse_excel(self, file_path: str) -> Dict[str, Any]:
        """
        Parse SCH Excel file and convert to universal schema
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary matching universal schema
        """
        import warnings
        warnings.filterwarnings('ignore')
        
        print(f"DEBUG: Starting parse_excel for: {file_path}")
        
        # Handle .xls vs .xlsx
        file_ext = file_path.lower().split('.')[-1]
        if file_ext == 'xls':
            print(f"INFO: Converting .xls to .xlsx...")
            file_path = self._convert_xls_to_xlsx(file_path)
        
        try:
            df = pd.read_excel(file_path, sheet_name=0, header=None, engine='openpyxl')
            print(f"SUCCESS: Loaded SCH DataFrame with shape {df.shape}")
            
            # DEBUG: Print first 15 rows to understand structure
            print("DEBUG: First 15 rows of Excel:")
            for i in range(min(15, len(df))):
                row_data = [str(df.iloc[i, j])[:30] if pd.notna(df.iloc[i, j]) else 'NaN' 
                           for j in range(min(10, len(df.columns)))]
                print(f"  Row {i}: {row_data}")
                
        except Exception as e:
            import traceback
            print(f"ERROR: Failed to read Excel file: {traceback.format_exc()}")
            raise Exception(f"Failed to read Excel file: {str(e)}")
        
        # Extract metadata
        metadata = self._extract_metadata(df, file_path)
        print(f"DEBUG: Extracted metadata: {metadata}")
        
        # Extract scheduling transactions
        transactions = self._extract_scheduling_transactions(df, metadata.get('scheduling_date'))
        print(f"DEBUG: Extracted {len(transactions)} transactions")
        
        # Calculate summary
        summary = self._calculate_summary(transactions)
        
        # Build universal schema
        universal_data = {
            "schema_version": "1.0.0",
            "template_id": self.template_id,
            "client_id": self.client_id,
            "metadata": metadata,
            "scheduling_transactions": transactions,
            "buy_transactions": [],
            "sell_transactions": [],
            "charges": {
                "funds_payin_payout": 0.0,
                "total_charges": 0.0
            },
            "summary": summary,
            "parsed_at": datetime.now().isoformat()
        }
        
        # Validate
        self._validate(universal_data)
        
        return universal_data
    
    def _convert_xls_to_xlsx(self, xls_path: str) -> str:
        """Convert .xls to .xlsx"""
        import tempfile
        import subprocess
        import os
        
        try:
            temp_dir = tempfile.gettempdir()
            result = subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'xlsx',
                '--outdir', temp_dir, xls_path
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0:
                base_name = os.path.splitext(os.path.basename(xls_path))[0]
                xlsx_path = os.path.join(temp_dir, f"{base_name}.xlsx")
                if os.path.exists(xlsx_path):
                    return xlsx_path
        except:
            pass
        
        # Fallback: try to read with xlrd anyway
        try:
            df = pd.read_excel(xls_path, sheet_name=0, header=None)
            temp_xlsx = os.path.join(tempfile.gettempdir(), f"converted_{uuid.uuid4().hex}.xlsx")
            df.to_excel(temp_xlsx, index=False, header=False, engine='openpyxl')
            return temp_xlsx
        except Exception as e:
            raise Exception(f"Unable to convert .xls file: {str(e)}")
    
    def _extract_metadata(self, df: pd.DataFrame, file_path: str = None) -> Dict[str, Any]:
        """Extract metadata from header section"""
        metadata = {}
        
        # Detect report type from filename
        # Main categories: DOR or SCH (based on keyword in filename)
        # Sub-categories: GDAM, RTM, or DAM (DAM = no GDAM/RTM keyword)
        if file_path:
            filename = os.path.basename(file_path).upper()
            
            # Determine main type (DOR or SCH)
            if 'SCH' in filename:
                main_type = 'SCH'
            else:
                main_type = 'DOR'  # Default to DOR
            
            # Determine sub-type (GDAM, RTM, or DAM)
            if 'GDAM' in filename:
                sub_type = 'GDAM'
            elif 'RTM' in filename:
                sub_type = 'RTM'
            else:
                sub_type = 'DAM'  # No GDAM/RTM keyword means DAM
            
            # Combine for report_type
            metadata['report_type'] = f"{main_type}-{sub_type}"
            metadata['main_category'] = main_type
            metadata['sub_category'] = sub_type
        else:
            metadata['report_type'] = 'SCH-DAM'
            metadata['main_category'] = 'SCH'
            metadata['sub_category'] = 'DAM'
        
        print("DEBUG: Extracting metadata...")
        print(f"  Report Type: {metadata['report_type']} (Main: {metadata['main_category']}, Sub: {metadata['sub_category']})")
        
        # Search for "Issue Date:" in first few rows
        for row_idx in range(min(10, len(df))):
            for col_idx in range(min(5, len(df.columns))):
                cell_val = df.iloc[row_idx, col_idx]
                if pd.isna(cell_val):
                    continue
                    
                cell_str = str(cell_val).strip().lower()
                
                # Issue Date (Row 1, Col B typically)
                if 'issue date' in cell_str:
                    try:
                        date_val = df.iloc[row_idx, col_idx + 1]
                        if pd.notna(date_val):
                            if isinstance(date_val, datetime):
                                metadata['issue_date'] = date_val.date().isoformat()
                            else:
                                metadata['issue_date'] = pd.to_datetime(date_val).date().isoformat()
                            print(f"  Found issue_date: {metadata['issue_date']}")
                    except Exception as e:
                        print(f"  WARNING: Could not extract issue_date: {e}")
                
                # Issue Time
                elif 'issue time' in cell_str:
                    try:
                        time_val = df.iloc[row_idx, col_idx + 1]
                        if pd.notna(time_val):
                            metadata['issue_time'] = str(time_val)
                            print(f"  Found issue_time: {metadata['issue_time']}")
                    except Exception as e:
                        print(f"  WARNING: Could not extract issue_time: {e}")
                
                # Scheduling Date
                elif 'scheduling' in cell_str:
                    try:
                        date_val = df.iloc[row_idx, col_idx + 1]
                        if pd.notna(date_val):
                            if isinstance(date_val, datetime):
                                sched_date = date_val.date().isoformat()
                            else:
                                sched_date = pd.to_datetime(date_val).date().isoformat()
                            
                            metadata['scheduling_date'] = sched_date
                            metadata['delivery_date'] = sched_date
                            metadata['trading_date'] = sched_date
                            print(f"  Found scheduling_date: {sched_date}")
                    except Exception as e:
                        print(f"  WARNING: Could not extract scheduling_date: {e}")
                
                # Participant
                elif 'participant' in cell_str:
                    try:
                        participant_val = df.iloc[row_idx, col_idx + 1]
                        if pd.notna(participant_val):
                            metadata['entity_name'] = str(participant_val).strip()
                            metadata['participant_name'] = str(participant_val).strip()
                            print(f"  Found participant: {metadata['entity_name']}")
                    except Exception as e:
                        print(f"  WARNING: Could not extract participant: {e}")
                
                # Portfolio (look for "Portfolio" header)
                elif 'portfolio' in cell_str and col_idx == 0:
                    try:
                        portfolio_val = df.iloc[row_idx, col_idx + 1]
                        if pd.notna(portfolio_val):
                            metadata['portfolio_name'] = str(portfolio_val).strip()
                            metadata['portfolio_code'] = str(portfolio_val).strip()
                            print(f"  Found portfolio: {metadata['portfolio_name']}")
                    except Exception as e:
                        print(f"  WARNING: Could not extract portfolio: {e}")
        
        # Extract entity_id from filename if available
        if file_path:
            filename = Path(file_path).stem
            parts = filename.split('_')
            if len(parts) >= 2:
                metadata['entity_id'] = parts[1]
                if len(parts) >= 3:
                    if 'portfolio_code' not in metadata:
                        metadata['portfolio_code'] = parts[2]
        
        return metadata
    
    def _extract_scheduling_transactions(self, df: pd.DataFrame, scheduling_date: str) -> List[Dict]:
        """Extract scheduling transactions with both regional and interface data"""
        transactions = []
        
        print("DEBUG: Extracting scheduling transactions...")
        
        # Find the data start row (look for first time period like "00:00 - 00:15")
        data_start = None
        for row_idx in range(len(df)):
            cell_val = df.iloc[row_idx, 0]
            if pd.notna(cell_val) and re.match(r'\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', str(cell_val)):
                data_start = row_idx
                print(f"  Found data start at row {data_start}")
                break
        
        if data_start is None:
            print("ERROR: Could not find data start row")
            return transactions
        
        # Parse scheduling date
        if not scheduling_date:
            print("WARNING: No scheduling_date provided, using today")
            base_date = datetime.now()
        else:
            base_date = datetime.fromisoformat(scheduling_date)
        
        print(f"  Using base_date: {base_date.date()}")
        
        # Determine column structure by looking at header row
        # Typical structure from your image:
        # Col A: Time Period (Regional)
        # Col B: Injection at Regional periphery  
        # Col C: Drawal at Regional periphery
        # Col D-E: (gap or empty)
        # Col F: Portfolio (Interface section start)
        # Col G: Time Period (Interface) 
        # Col H: Injection at Interface point
        # Col I: Drawal at Interface point
        
        # Let's auto-detect by checking row before data_start
        header_row_idx = data_start - 1
        print(f"  Checking header row {header_row_idx}:")
        header_info = []
        for col_idx in range(min(10, len(df.columns))):
            val = df.iloc[header_row_idx, col_idx]
            header_info.append(f"Col{col_idx}:{str(val)[:20]}" if pd.notna(val) else f"Col{col_idx}:NaN")
        print(f"    {' | '.join(header_info)}")
        
        # Based on your image, the structure is:
        # Regional: Cols 0 (time), 1 (injection), 2 (drawal)
        # Interface: Cols 5 (portfolio), 6 (time), 7 (injection), 8 (drawal)
        # BUT let's detect dynamically
        
        regional_time_col = 0
        regional_injection_col = 1
        regional_drawal_col = 2
        interface_injection_col = None
        interface_drawal_col = None
        
        # Find interface columns by looking for "Injection at Interface" header
        for col_idx in range(5, min(10, len(df.columns))):
            header_val = df.iloc[header_row_idx, col_idx]
            if pd.notna(header_val):
                header_str = str(header_val).lower()
                if 'injection' in header_str and 'interface' in header_str:
                    interface_injection_col = col_idx
                    interface_drawal_col = col_idx + 1  # Usually next column
                    print(f"  Found interface columns: injection={interface_injection_col}, drawal={interface_drawal_col}")
                    break
        
        # If not found, use default from image
        if interface_injection_col is None:
            interface_injection_col = 7
            interface_drawal_col = 8
            print(f"  Using default interface columns: injection={interface_injection_col}, drawal={interface_drawal_col}")
        
        # Extract data rows
        for idx in range(data_start, min(data_start + 96, len(df))):
            row = df.iloc[idx]
            
            # Get time block from column 0
            time_block = row[regional_time_col]
            
            if pd.isna(time_block):
                continue
                
            time_block_str = str(time_block).strip()
            
            # Check if we've reached the end (Total row or empty)
            if not time_block_str or 'total' in time_block_str.lower():
                print(f"  Reached end at row {idx}")
                break
            
            # Validate time format
            if not re.match(r'\d{2}:\d{2}\s*-\s*\d{2}:\d{2}', time_block_str):
                print(f"  Skipping invalid time format at row {idx}: {time_block_str}")
                continue
            
            try:
                # Extract regional data
                regional_injection = float(row[regional_injection_col]) if pd.notna(row[regional_injection_col]) else 0.0
                regional_drawal = float(row[regional_drawal_col]) if pd.notna(row[regional_drawal_col]) else 0.0
                
                # Extract interface data
                interface_injection = float(row[interface_injection_col]) if pd.notna(row[interface_injection_col]) else 0.0
                interface_drawal = float(row[interface_drawal_col]) if pd.notna(row[interface_drawal_col]) else 0.0
                
                # Parse time
                time_parts = time_block_str.split('-')[0].strip().split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                
                time_block_start = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                time_block_end = time_block_start + timedelta(minutes=15)
                
                # Calculate losses
                injection_losses = regional_injection - interface_injection
                drawal_losses = regional_drawal - interface_drawal
                
                transaction = {
                    'date': base_date.date().isoformat(),
                    'time_slot': time_block_str,
                    'time_block_start': time_block_start.isoformat(),
                    'time_block_end': time_block_end.isoformat(),
                    # Regional periphery (without losses - traded quantity)
                    'regional_injection_mw': regional_injection,
                    'regional_drawal_mw': regional_drawal,
                    'regional_net_mw': regional_injection - regional_drawal,
                    # Interface point (after losses - final quantity)
                    'interface_injection_mw': interface_injection,
                    'interface_drawal_mw': interface_drawal,
                    'interface_net_mw': interface_injection - interface_drawal,
                    # Losses breakdown
                    'injection_losses_mw': injection_losses,
                    'drawal_losses_mw': drawal_losses,
                    'total_losses_mw': injection_losses + drawal_losses,
                    # Net scheduled (after losses)
                    'net_scheduled_mw': (interface_injection - interface_drawal)
                }
                
                transactions.append(transaction)
                
                # Debug first few
                if len(transactions) <= 3:
                    print(f"  Transaction {len(transactions)}: {time_block_str} -> Regional: {regional_injection}/{regional_drawal}, Interface: {interface_injection}/{interface_drawal}")
                
            except (ValueError, IndexError, AttributeError) as e:
                print(f"  WARNING: Error parsing row {idx}: {e}")
                continue
        
        print(f"SUCCESS: Extracted {len(transactions)} scheduling transactions")
        
        return transactions
    
    def _calculate_summary(self, transactions: List[Dict]) -> Dict[str, float]:
        """Calculate summary statistics for scheduling data"""
        
        if not transactions:
            return {
                'total_scheduling_slots': 0,
                'total_regional_injection_mwh': 0.0,
                'total_regional_drawal_mwh': 0.0,
                'total_interface_injection_mwh': 0.0,
                'total_interface_drawal_mwh': 0.0,
                'net_regional_mwh': 0.0,
                'net_interface_mwh': 0.0,
                'total_buy_quantity_mwh': 0.0,
                'total_sell_quantity_mwh': 0.0,
                'total_buy_amount': 0.0,
                'total_sell_amount': 0.0,
                'net_amount': 0.0,
                'funds_payin_payout': 0.0
            }
        
        total_regional_injection = sum(t['regional_injection_mw'] for t in transactions)
        total_regional_drawal = sum(t['regional_drawal_mw'] for t in transactions)
        total_interface_injection = sum(t['interface_injection_mw'] for t in transactions)
        total_interface_drawal = sum(t['interface_drawal_mw'] for t in transactions)
        total_losses = sum(t['total_losses_mw'] for t in transactions)
        
        return {
            'total_scheduling_slots': len(transactions),
            'total_regional_injection_mwh': total_regional_injection * 0.25,
            'total_regional_drawal_mwh': total_regional_drawal * 0.25,
            'total_interface_injection_mwh': total_interface_injection * 0.25,
            'total_interface_drawal_mwh': total_interface_drawal * 0.25,
            'net_regional_mwh': (total_regional_injection - total_regional_drawal) * 0.25,
            'net_interface_mwh': (total_interface_injection - total_interface_drawal) * 0.25,
            'total_losses_mwh': total_losses * 0.25,
            'total_buy_quantity_mwh': total_interface_drawal * 0.25,
            'total_sell_quantity_mwh': total_interface_injection * 0.25,
            'total_buy_amount': 0.0,
            'total_sell_amount': 0.0,
            'net_amount': 0.0,
            'funds_payin_payout': 0.0
        }
    
    def _validate(self, data: Dict[str, Any]) -> bool:
        """Validate parsed data against schema rules"""
        assert 'metadata' in data, "Missing metadata"
        assert 'scheduling_transactions' in data, "Missing scheduling_transactions"
        assert 'summary' in data, "Missing summary"
        
        meta = data['metadata']
        assert 'scheduling_date' in meta or 'trading_date' in meta, "Missing scheduling_date"
        
        return True
    
    def save_to_json(self, data: Dict[str, Any], output_path: str):
        """Save parsed data to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_template_info(self) -> Dict[str, str]:
        """Get template information"""
        return {
            "template_id": self.template_id,
            "version": self.template_version,
            "description": "IEX Scheduling Report Parser",
            "supported_formats": "SCH (Scheduling Reports)"
        }