"""
Test Story 3.1 & 3.2 - Auto-Transfer Workflow with Single Day
Tests that uploading 4 files for one portfolio/day triggers auto-calculation
"""

import requests
import json
import os

API_BASE = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE}/api/upload"

# Use Day 1 (Jan 13, 2026) files - all same portfolio & date
TEST_FILES = {
    "GDAM": "/workspaces/Power-Trading-application/Data/mock_reports/GDAM_IEX130126DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
    "DAM": "/workspaces/Power-Trading-application/Data/mock_reports/DAM_IEX130126DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
    "RTM": "/workspaces/Power-Trading-application/Data/mock_reports/RTM_IEX130126DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
    "SCH": "/workspaces/Power-Trading-application/Data/mock_reports/IEX130126SCH_NPT0027_KA0_Mellbro_Sugars_Pvt.xlsx",
}

def upload_file(filepath, file_type):
    """Upload a file and return energy_schedule info"""
    print(f"\n📤 Uploading {file_type}: {os.path.basename(filepath)}")
    print("─" * 80)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    
    with open(filepath, 'rb') as f:
        files = {'file': (os.path.basename(filepath), f)}
        response = requests.post(UPLOAD_ENDPOINT, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Upload successful")
        
        # Show database info
        print("\n📊 Database:")
        print(f"   Client ID: {data.get('client_id')}")
        print(f"   Portfolio ID: {data.get('portfolio_id')}")
        print(f"   File ID: {data.get('file_id')}")
        print(f"   Transactions: {data.get('transaction_count')}")
        
        # Show energy schedule info
        es = data.get('energy_schedule', {})
        if es:
            print("\n⚡ Energy Schedule:")
            if es.get('auto_calculated'):
                print("   🎉 AUTO-CALCULATION TRIGGERED!")
                print(f"\n   Calculation Results:")
                print(f"      Portfolio ID: {es.get('portfolio_id')}")
                print(f"      Trading Date: {es.get('trading_date')}")
                print(f"      CTU Losses %: {es.get('ctu_losses_percentage', 0):.2f}%")
                print(f"      CTU Charges: ₹{es.get('ctu_charges', 0):.2f}")
                print(f"      NLDC Fees: ₹{es.get('nldc_fees', 0):.2f}")
                print(f"      Energy Savings: {es.get('energy_savings_mwh', 0):.2f} MWh")
            else:
                print("   ⏳ Waiting for files:")
                files_status = es.get('files_present', {})
                print(f"      GDAM: {'✅' if files_status.get('has_gdam_data') else '❌'}")
                print(f"      DAM:  {'✅' if files_status.get('has_dam_data') else '❌'}")
                print(f"      RTM:  {'✅' if files_status.get('has_rtm_data') else '❌'}")
                print(f"      SCH:  {'✅' if files_status.get('has_sch_data') else '❌'}")
        
        return es
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return None

def main():
    print("=" * 100)
    print("TESTING STORY 3.1 & 3.2 - AUTO-TRANSFER WORKFLOW (Single Day)")
    print("=" * 100)
    
    print("\n📋 Test Plan:")
    print("   Using Jan 13, 2026 files (all NPT0027_KA0)")
    print("   1. Upload GDAM DOR → Create daily entry")
    print("   2. Upload DAM DOR → Update same entry")
    print("   3. Upload RTM DOR → Update same entry")
    print("   4. Upload SCH → Should trigger AUTO-CALCULATION! 🎯")
    
    results = {}
    
    # Upload files in sequence
    print("\n" + "=" * 100)
    print("STEP 1: Upload GDAM DOR File")
    print("=" * 100)
    results['GDAM'] = upload_file(TEST_FILES['GDAM'], 'GDAM')
    
    print("\n" + "=" * 100)
    print("STEP 2: Upload DAM DOR File")
    print("=" * 100)
    results['DAM'] = upload_file(TEST_FILES['DAM'], 'DAM')
    
    print("\n" + "=" * 100)
    print("STEP 3: Upload RTM DOR File")
    print("=" * 100)
    results['RTM'] = upload_file(TEST_FILES['RTM'], 'RTM')
    
    print("\n" + "=" * 100)
    print("STEP 4: Upload SCH File (Critical - Should Trigger Auto-Calc)")
    print("=" * 100)
    results['SCH'] = upload_file(TEST_FILES['SCH'], 'SCH')
    
    # Final summary
    print("\n" + "=" * 100)
    print("TEST RESULTS")
    print("=" * 100)
    
    if results.get('SCH') and results['SCH'].get('auto_calculated'):
        print("\n✅ SUCCESS! Auto-calculation triggered on 4th file upload!")
        print("\n📊 Final Metrics:")
        es = results['SCH']
        print(f"   Portfolio ID: {es.get('portfolio_id')}")
        print(f"   Trading Date: {es.get('trading_date')}")
        print(f"   CTU Losses %: {es.get('ctu_losses_percentage', 0):.2f}%")
        print(f"   CTU Charges: ₹{es.get('ctu_charges', 0):.2f}")
        print(f"   NLDC Fees: ₹{es.get('nldc_fees', 0):.2f}")
        print(f"   Energy Savings: {es.get('energy_savings_mwh', 0):.2f} MWh")
    else:
        print("\n❌ FAILED - Calculation not triggered")
        if results.get('SCH'):
            print("\n   Files Present:")
            files = results['SCH'].get('files_present', {})
            print(f"      GDAM: {'✅' if files.get('has_gdam_data') else '❌'}")
            print(f"      DAM:  {'✅' if files.get('has_dam_data') else '❌'}")
            print(f"      RTM:  {'✅' if files.get('has_rtm_data') else '❌'}")
            print(f"      SCH:  {'✅' if files.get('has_sch_data') else '❌'}")
    
    # Query monthly status
    print("\n" + "=" * 100)
    print("ENERGY SCHEDULE STATUS (All Months)")
    print("=" * 100)
    
    try:
        response = requests.get(f"{API_BASE}/api/energy-schedule/months")
        if response.status_code == 200:
            months = response.json()
            for month in months:
                print(f"\n📅 {month['month_name']} {month['year']}:")
                print(f"   Portfolio ID: {month['portfolio_id']}")
                print(f"   Days Completed: {month['total_days_completed']}")
                print(f"   Total Energy Savings: {month['total_energy_savings']:.2f} MWh")
                print(f"   Average CTU Losses: {month['average_ctu_losses']:.2f}%")
    except Exception as e:
        print(f"❌ Error fetching monthly status: {e}")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    main()
