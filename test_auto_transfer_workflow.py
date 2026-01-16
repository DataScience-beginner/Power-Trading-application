"""
Test Auto-Transfer Workflow (Story 3.1 & 3.2)
----------------------------------------------
Tests automatic transfer of uploaded files to Energy Schedule
and auto-calculation when all 4 files are present.
"""

import requests
import os
from pathlib import Path


BASE_URL = "http://localhost:8000/api"
DATA_DIR = Path("/workspaces/Power-Trading-application/Data")


def upload_file(file_path):
    """Upload a file and return the response"""
    print(f"\n📤 Uploading: {file_path.name}")
    print("─" * 80)
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'application/vnd.ms-excel')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful")
        
        # Show database info
        db_info = data.get('database', {})
        print(f"\n📊 Database:")
        print(f"   Client ID: {db_info.get('client_id')}")
        print(f"   Portfolio ID: {db_info.get('portfolio_id')}")
        print(f"   File ID: {db_info.get('file_id')}")
        print(f"   Transactions: {db_info.get('transactions_saved')}")
        
        # Show energy schedule info
        es_info = data.get('energy_schedule')
        if es_info:
            print(f"\n⚡ Energy Schedule:")
            if es_info.get('auto_calculated'):
                print(f"   ✅ AUTO-CALCULATED!")
                print(f"   Total Scheduled: {es_info.get('total_scheduled_mwh', 0):.2f} MWh")
                print(f"   CTU Losses: {es_info.get('ctu_losses_percent', 0):.2f}%")
                print(f"   Energy Savings: {es_info.get('energy_savings_mwh', 0):.2f} MWh")
                print(f"   Total Cost: ₹{es_info.get('total_cost', 0):.2f}")
            else:
                files_present = es_info.get('files_present', {})
                print(f"   ⏳ Waiting for files:")
                print(f"      GDAM: {'✅' if files_present.get('gdam') else '❌'}")
                print(f"      DAM:  {'✅' if files_present.get('dam') else '❌'}")
                print(f"      RTM:  {'✅' if files_present.get('rtm') else '❌'}")
                print(f"      SCH:  {'✅' if files_present.get('sch') else '❌'}")
        
        return data
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_auto_transfer_workflow():
    """
    Test the complete auto-transfer workflow
    """
    print("\n" + "="*100)
    print("TESTING STORY 3.1 & 3.2 - AUTO-TRANSFER WORKFLOW")
    print("="*100)
    
    print("\n📋 Test Plan:")
    print("   1. Upload GDAM DOR file → Should create daily entry")
    print("   2. Upload DAM DOR file → Should update same entry")
    print("   3. Upload RTM DOR file → Should update same entry")
    print("   4. Upload SCH file → Should auto-calculate!")
    
    # Test files (for Grasim Industries, Jan 13, 2026)
    files_to_upload = [
        DATA_DIR / "IEX130126DOR_NPT0019_TN0_Grasim_Industries_Limited.xls",  # DAM
        DATA_DIR / "RTM_IEX130126DOR_NPT0019_TN0_Grasim_Industries_Limited.XLS",  # RTM
        DATA_DIR / "IEX260114SCH_NPT0019_TN0_Grasim_Industries_Limited.xlsx",  # SCH
    ]
    
    # Check if GDAM file exists
    gdam_file = DATA_DIR / "GDAM_IEX130126DOR_NPT0019_TN0_Grasim_Industries_Limited.xls"
    if not gdam_file.exists():
        # Use the one we have
        gdam_file = DATA_DIR / "GDAM_IEX120126DOR_NPT0027_KA0_Mellbro_Sugars_Pvt.xls"
        print(f"\n⚠️  Using different GDAM file for demo: {gdam_file.name}")
    
    files_to_upload.insert(0, gdam_file)
    
    print(f"\n" + "="*100)
    print("STEP 1: Upload GDAM DOR File")
    print("="*100)
    result1 = upload_file(files_to_upload[0])
    
    print(f"\n" + "="*100)
    print("STEP 2: Upload DAM DOR File")
    print("="*100)
    result2 = upload_file(files_to_upload[1])
    
    print(f"\n" + "="*100)
    print("STEP 3: Upload RTM DOR File")
    print("="*100)
    result3 = upload_file(files_to_upload[2])
    
    print(f"\n" + "="*100)
    print("STEP 4: Upload SCH File (Should Trigger Auto-Calculation)")
    print("="*100)
    result4 = upload_file(files_to_upload[3])
    
    # Check if auto-calculation happened
    print(f"\n" + "="*100)
    print("TEST RESULTS")
    print("="*100)
    
    if result4 and result4.get('energy_schedule', {}).get('auto_calculated'):
        print(f"\n✅ STORY 3.1 COMPLETE: Auto-create daily entries on upload")
        print(f"✅ STORY 3.2 COMPLETE: Auto-trigger calculations when all 4 files present")
        
        es_data = result4['energy_schedule']
        print(f"\n📊 Final Calculation Results:")
        print(f"   Total Scheduled:     {es_data.get('total_scheduled_mwh', 0):.2f} MWh")
        print(f"   CTU Losses:          {es_data.get('ctu_losses_percent', 0):.2f}%")
        print(f"   Energy Savings:      {es_data.get('energy_savings_mwh', 0):.2f} MWh")
        print(f"   Total Cost:          ₹{es_data.get('total_cost', 0):,.2f}")
        
        print(f"\n🎯 AUTO-TRANSFER WORKFLOW:")
        print(f"   Upload File → Parse → Save to DB → Transfer to Energy Schedule")
        print(f"                                    ↓")
        print(f"                       Check if all 4 files present")
        print(f"                                    ↓")
        print(f"                       Auto-calculate if complete ✅")
        
    else:
        print(f"\n⏳ Calculation not triggered (missing files)")
        if result4:
            files_present = result4.get('energy_schedule', {}).get('files_present', {})
            print(f"\n   Files Present:")
            print(f"      GDAM: {'✅' if files_present.get('gdam') else '❌'}")
            print(f"      DAM:  {'✅' if files_present.get('dam') else '❌'}")
            print(f"      RTM:  {'✅' if files_present.get('rtm') else '❌'}")
            print(f"      SCH:  {'✅' if files_present.get('sch') else '❌'}")
    
    # Get final energy schedule status
    print(f"\n" + "="*100)
    print("ENERGY SCHEDULE STATUS")
    print("="*100)
    
    response = requests.get(f"{BASE_URL}/energy-schedule/months")
    if response.status_code == 200:
        data = response.json()
        if data['count'] > 0:
            for sheet in data['month_sheets']:
                print(f"\n📅 {sheet['month_name']}:")
                print(f"   Portfolio ID: {sheet['portfolio_id']}")
                print(f"   Days Completed: {sheet['days_completed']}")
                print(f"   Total Energy Savings: {sheet['total_energy_savings_mwh']:.2f} MWh")
                print(f"   Average CTU Losses: {sheet['average_ctu_losses_percent']:.2f}%")
    
    print(f"\n" + "="*100)
    print()


if __name__ == "__main__":
    test_auto_transfer_workflow()
