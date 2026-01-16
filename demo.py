#!/usr/bin/env python3
"""
Quick demo - Shows how to use the parser
"""

import json
from pathlib import Path
from parsers.DOR_Parser import GDAMTemplateParser


def demo():
    """Run a quick demo"""
    print("=" * 70)
    print("⚡ POWER TRADING DATA PARSER - DEMO")
    print("=" * 70)
    
    # Check if we have example data
    example_file = Path("output/mellbro_parsed_data.json")
    
    if example_file.exists():
        print("\n📊 Loading example parsed data...")
        with open(example_file, 'r') as f:
            data = json.load(f)
        
        print("\n" + "=" * 70)
        print("📋 PARSED DATA SUMMARY")
        print("=" * 70)
        
        metadata = data.get('metadata', {})
        summary = data.get('summary', {})
        
        print(f"\n🏢 Client: {data.get('client_id', 'N/A')}")
        print(f"📄 Template: {data.get('template_id', 'N/A')}")
        print(f"🔖 Schema Version: {data.get('schema_version', 'N/A')}")
        
        print(f"\n📅 Trading Date: {metadata.get('trading_date', 'N/A')}")
        print(f"📅 Delivery Date: {metadata.get('delivery_date', 'N/A')}")
        print(f"🏢 Entity: {metadata.get('entity_name', 'N/A')}")
        print(f"📁 Portfolio: {metadata.get('portfolio_name', 'N/A')}")
        
        print(f"\n📊 TRANSACTIONS:")
        print(f"  📈 Buy: {summary.get('total_buy_transactions', 0)} transactions")
        print(f"  📉 Sell: {summary.get('total_sell_transactions', 0)} transactions")
        print(f"  ⚡ Total Energy Bought: {summary.get('total_buy_quantity_mw', 0):.2f} MW")
        print(f"  ⚡ Total Energy Sold: {summary.get('total_sell_quantity_mw', 0):.2f} MW")
        
        print(f"\n💰 FINANCIAL SUMMARY:")
        print(f"  💵 Buy Amount: ₹{summary.get('total_buy_amount', 0):,.2f}")
        print(f"  💵 Sell Amount: ₹{summary.get('total_sell_amount', 0):,.2f}")
        print(f"  💸 Charges: ₹{summary.get('total_charges', 0):,.2f}")
        print(f"  {'💰' if summary.get('net_amount', 0) >= 0 else '📉'} Net Amount: ₹{summary.get('net_amount', 0):,.2f}")
        
        # Show sample transactions
        buy_trans = data.get('buy_transactions', [])
        if buy_trans:
            print(f"\n📈 SAMPLE BUY TRANSACTIONS (first 3):")
            for i, trans in enumerate(buy_trans[:3]):
                print(f"  {i+1}. {trans['time_block_start'][:16]} → "
                      f"{trans['quantity_mw']:.2f} MW @ ₹{trans['rate_per_mwh']:.2f}/MWh = "
                      f"₹{trans['amount']:,.2f}")
        
        sell_trans = data.get('sell_transactions', [])
        if sell_trans:
            print(f"\n📉 SAMPLE SELL TRANSACTIONS (first 3):")
            for i, trans in enumerate(sell_trans[:3]):
                total_qty = trans.get('total_quantity_mw', 0)
                print(f"  {i+1}. {trans['time_block_start'][:16]} → "
                      f"{total_qty:.2f} MW (Solar: {trans.get('solar_quantity_mw', 0):.2f}, "
                      f"Non-Solar: {trans.get('non_solar_quantity_mw', 0):.2f}) = "
                      f"₹{trans['amount']:,.2f}")
        
        print("\n" + "=" * 70)
        print("✅ Demo complete!")
        print("=" * 70)
        
    else:
        print("\n❌ No example data found.")
        print("\nTo parse a new Excel file, use:")
        print("  python run_parser.py <your_excel_file.xls>")
    
    print("\n📚 USAGE EXAMPLES:")
    print("  1. Parse Excel file:")
    print("     python run_parser.py data/trading_report.xls")
    print("\n  2. Parse with custom client ID:")
    print("     python run_parser.py data/trading_report.xls my-client-123")
    print("\n  3. Use in Python code:")
    print("     from parsers import GDAMTemplateParser")
    print("     parser = GDAMTemplateParser(client_id='my-client')")
    print("     data = parser.parse_excel('file.xls')")
    print()


if __name__ == "__main__":
    demo()
