#!/usr/bin/env python3
"""
Analyze SCH file structure to find where entity_id is located
"""

import pandas as pd
from pathlib import Path

# Use one of our SCH files as template
sch_file = Path("Data/IEX260114SCH_NPT0019_TN0_Grasim_Industries_Limited.xlsx")

if sch_file.exists():
    print(f"Analyzing: {sch_file.name}\n")
    
    df = pd.read_excel(sch_file, sheet_name=0, header=None, engine='openpyxl')
    
    print("First 10 rows of SCH file:")
    print("="*80)
    
    for i in range(min(10, len(df))):
        print(f"\nRow {i}:")
        row_data = []
        for j in range(min(8, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                row_data.append(f"  Col {j}: {str(val)[:50]}")
        
        if row_data:
            for item in row_data:
                print(item)
    
    print("\n" + "="*80)
    print("\nSearching for entity_id pattern (A2AR0NPT####)...")
    
    for i in range(min(15, len(df))):
        for j in range(min(10, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                val_str = str(val)
                if 'A2AR0NPT' in val_str or 'NPT' in val_str:
                    print(f"  Found at Row {i}, Col {j}: {val_str}")
    
else:
    print(f"❌ File not found: {sch_file}")
