#!/usr/bin/env python3
"""
Main application runner - Parse Excel files to Universal Schema
Usage: python run_parser.py <excel_file_path>
"""

import sys
import json
from pathlib import Path
from parsers.DOR_Parser import GDAMTemplateParser


def main():
    """Main execution function"""
    print("=" * 60)
    print("⚡ POWER TRADING DATA PARSER")
    print("=" * 60)
    
    # Check if file path provided
    if len(sys.argv) < 2:
        print("\n❌ Error: Please provide Excel file path")
        print("\nUsage:")
        print("  python run_parser.py <excel_file_path>")
        print("\nExample:")
        print("  python run_parser.py data/mellbro_report.xls")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    # Check if file exists
    if not Path(excel_file).exists():
        print(f"\n❌ Error: File not found: {excel_file}")
        sys.exit(1)
    
    # Get client ID if provided
    client_id = sys.argv[2] if len(sys.argv) > 2 else "default-client"
    
    print(f"\n📄 Input File: {excel_file}")
    print(f"👤 Client ID: {client_id}")
    print("\n🔄 Parsing Excel file...")
    
    try:
        # Initialize parser
        parser = GDAMTemplateParser(client_id=client_id)
        
        # Parse Excel
        universal_data = parser.parse_excel(excel_file)
        
        # Generate output filename
        input_name = Path(excel_file).stem
        output_file = f"output/{input_name}_parsed.json"
        
        # Save to output
        with open(output_file, 'w') as f:
            json.dump(universal_data, f, indent=2)
        
        # Display results
        print("\n✅ SUCCESS! Parsed data to universal schema")
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        
        metadata = universal_data.get('metadata', {})
        summary = universal_data.get('summary', {})
        
        print(f"\n📅 Trading Date: {metadata.get('trading_date', 'N/A')}")
        print(f"📅 Delivery Date: {metadata.get('delivery_date', 'N/A')}")
        print(f"🏢 Entity: {metadata.get('entity_name', 'N/A')}")
        print(f"📁 Portfolio: {metadata.get('portfolio_name', 'N/A')}")
        
        print(f"\n📈 Buy Transactions: {summary.get('total_buy_transactions', 0)}")
        print(f"📉 Sell Transactions: {summary.get('total_sell_transactions', 0)}")
        
        print(f"\n💰 Total Buy Amount: ₹{summary.get('total_buy_amount', 0):,.2f}")
        print(f"💰 Total Sell Amount: ₹{summary.get('total_sell_amount', 0):,.2f}")
        print(f"💰 Total Charges: ₹{summary.get('total_charges', 0):,.2f}")
        print(f"💰 Net Amount: ₹{summary.get('net_amount', 0):,.2f}")
        
        print(f"\n💾 Output saved to: {output_file}")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
