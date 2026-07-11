"""
SCH Energy Schedule Parser
Extracts "Consumption After Losses" data for Energy Schedule calculations
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import re


class SCH_EnergyScheduleParser:
    """
    Parse SCH files specifically for Energy Schedule sheet
    Extracts:
    - 96 time-slot consumption after losses (Interface point drawal)
    - Total consumption
    - Regional and State loss percentages
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.issue_date = None
        self.scheduling_date = None
        self.portfolio_name = None
        
    def parse(self) -> Dict:
        """
        Parse SCH file and extract Energy Schedule data
        
        Returns:
            Dict with:
            - metadata: {issue_date, scheduling_date, portfolio}
            - consumption_after_losses: List of 96 time slots with MW values
            - total_consumption: Total MWh
            - losses: {regional_pct, state_pct, combined_pct}
        """
        try:
            # Read Excel file
            self.df = pd.read_excel(self.file_path, header=None, engine='openpyxl')
            
            # Extract metadata
            metadata = self._extract_metadata()
            
            # Extract consumption after losses (96 time slots)
            consumption_data = self._extract_consumption_after_losses()
            
            # Extract loss percentages
            loss_data = self._extract_losses()
            
            # Calculate totals
            total_mwh = self._extract_total()
            
            return {
                "success": True,
                "metadata": metadata,
                "consumption_after_losses": consumption_data,
                "total_consumption_mwh": total_mwh,
                "losses": loss_data,
                "file_path": self.file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": self.file_path
            }
    
    def _extract_metadata(self) -> Dict:
        """Extract issue date, scheduling date, portfolio name"""
        metadata = {}
        
        # Row 0: Issue Date
        if len(self.df) > 0:
            row_0 = str(self.df.iloc[0, 1]) if pd.notna(self.df.iloc[0, 1]) else ""
            metadata['issue_date'] = row_0
        
        # Row 1: Issue Time
        if len(self.df) > 1:
            row_1 = str(self.df.iloc[1, 1]) if pd.notna(self.df.iloc[1, 1]) else ""
            metadata['issue_time'] = row_1
        
        # Row 2: Scheduling Request for (delivery date)
        if len(self.df) > 2:
            row_2 = str(self.df.iloc[2, 1]) if pd.notna(self.df.iloc[2, 1]) else ""
            metadata['scheduling_date'] = row_2
            self.scheduling_date = row_2
        
        # Row 3: Participant Name
        if len(self.df) > 3:
            row_3 = str(self.df.iloc[3, 1]) if pd.notna(self.df.iloc[3, 1]) else ""
            metadata['participant_name'] = row_3
        
        # Row 7: Portfolio Name (extract from long string)
        if len(self.df) > 7:
            portfolio_raw = str(self.df.iloc[7, 1]) if pd.notna(self.df.iloc[7, 1]) else ""
            metadata['portfolio_name'] = portfolio_raw.strip()
            self.portfolio_name = portfolio_raw.strip()
        
        return metadata
    
    def _extract_consumption_after_losses(self) -> List[Dict]:
        """
        Extract 96 time slots of consumption after losses
        This is the "Drawal at Interface point" column (rightmost)
        
        Returns:
            List of dicts with: {time_slot, consumption_mw}
        """
        consumption_list = []
        
        # Data starts at row 9, ends at row 104 (96 slots)
        # Column structure: Time | Regional Injection | Regional Drawal | Time | Interface Injection | Interface Drawal
        # We need the last column (Interface Drawal) = Consumption After Losses
        
        for row_idx in range(9, 105):  # Rows 9-104 (96 time slots)
            if row_idx < len(self.df):
                row_data = self.df.iloc[row_idx]
                
                # Time slot is in column 4 (duplicate of column 0)
                time_slot = str(row_data[4]) if pd.notna(row_data[4]) else ""
                
                # Consumption after losses is in column 6 (Interface Drawal)
                consumption_mw = row_data[6] if pd.notna(row_data[6]) else 0
                
                try:
                    consumption_mw = float(consumption_mw)
                except:
                    consumption_mw = 0.0
                
                consumption_list.append({
                    "time_slot": time_slot,
                    "consumption_mw": consumption_mw,
                    "row_number": row_idx
                })
        
        return consumption_list
    
    def _extract_total(self) -> float:
        """Extract total consumption in MWh from row 105"""
        try:
            if len(self.df) > 105:
                # Row 105: Total(In MWh) | ... | ... | Total(In MWh) | ... | <value>
                total_value = self.df.iloc[105, 6]  # Column 6 = Interface Drawal total
                return float(total_value) if pd.notna(total_value) else 0.0
        except:
            return 0.0
    
    def _extract_losses(self) -> Dict:
        """
        Extract loss percentages from rows 108-109
        
        Returns:
            {
                'regional_injection_pct': float,
                'regional_drawal_pct': float,
                'state_injection_pct': float,
                'state_drawal_pct': float,
                'combined_loss_pct': float (regional drawal + state drawal)
            }
        """
        losses = {
            'regional_injection_pct': 0.0,
            'regional_drawal_pct': 0.0,
            'state_injection_pct': 0.0,
            'state_drawal_pct': 0.0,
            'combined_loss_pct': 0.0
        }
        
        try:
            # Row 108: Regional losses | SR->Injection: 0.00% Drawal: 4.81%
            if len(self.df) > 108:
                regional_text = str(self.df.iloc[108, 1]) if pd.notna(self.df.iloc[108, 1]) else ""
                
                # Extract percentages using regex
                injection_match = re.search(r'Injection:\s*(\d+\.?\d*)%', regional_text)
                drawal_match = re.search(r'Drawal:\s*(\d+\.?\d*)%', regional_text)
                
                if injection_match:
                    losses['regional_injection_pct'] = float(injection_match.group(1))
                if drawal_match:
                    losses['regional_drawal_pct'] = float(drawal_match.group(1))
            
            # Row 109: State losses | TAMILNADU->Injection: 3.06% Drawal: 3.06%
            if len(self.df) > 109:
                state_text = str(self.df.iloc[109, 1]) if pd.notna(self.df.iloc[109, 1]) else ""
                
                injection_match = re.search(r'Injection:\s*(\d+\.?\d*)%', state_text)
                drawal_match = re.search(r'Drawal:\s*(\d+\.?\d*)%', state_text)
                
                if injection_match:
                    losses['state_injection_pct'] = float(injection_match.group(1))
                if drawal_match:
                    losses['state_drawal_pct'] = float(drawal_match.group(1))
            
            # Combined loss = Regional Drawal + State Drawal
            losses['combined_loss_pct'] = losses['regional_drawal_pct'] + losses['state_drawal_pct']
            
        except Exception as e:
            print(f"Warning: Could not extract losses: {e}")
        
        return losses


def test_parser():
    """Test the parser with sample file"""
    import json
    
    file_path = "/workspaces/Power-Trading-application/Data/IEX260114SCH_NPT0019_TN0_Grasim_Industries_Limited.xlsx"
    
    parser = SCH_EnergyScheduleParser(file_path)
    result = parser.parse()
    
    if result['success']:
        print("=" * 80)
        print("SCH ENERGY SCHEDULE PARSER - TEST RESULTS")
        print("=" * 80)
        
        print("\n📋 METADATA:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
        
        print(f"\n📊 TOTAL CONSUMPTION: {result['total_consumption_mwh']} MWh")
        
        print("\n📉 LOSSES:")
        for key, value in result['losses'].items():
            print(f"  {key}: {value}%")
        
        print(f"\n⏰ TIME SLOTS: {len(result['consumption_after_losses'])} slots extracted")
        print("\nFirst 5 time slots:")
        for slot in result['consumption_after_losses'][:5]:
            print(f"  {slot['time_slot']}: {slot['consumption_mw']} MW")
        
        print("\nLast 5 time slots:")
        for slot in result['consumption_after_losses'][-5:]:
            print(f"  {slot['time_slot']}: {slot['consumption_mw']} MW")
        
        # Count non-zero slots
        non_zero = [s for s in result['consumption_after_losses'] if s['consumption_mw'] > 0]
        print(f"\n✅ Non-zero slots: {len(non_zero)} / 96")
        
        # Save to JSON
        output_file = "/workspaces/Power-Trading-application/output/SCH_energy_schedule_parsed.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Saved to: {output_file}")
        
    else:
        print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    test_parser()
