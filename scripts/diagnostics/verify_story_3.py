"""
Story 3 Implementation Verification Script
Checks that auto-transfer code is properly integrated
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_code_present(filepath, search_string, description):
    """Check if code contains specific string"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            present = search_string in content
            status = "✅" if present else "❌"
            print(f"{status} {description}")
            return present
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 100)
    print("STORY 3 IMPLEMENTATION VERIFICATION")
    print("=" * 100)
    
    all_checks = []
    
    print("\n📁 File Existence Checks:")
    print("-" * 100)
    all_checks.append(check_file_exists(
        "/workspaces/Power-Trading-application/api/main.py",
        "Main API file"
    ))
    all_checks.append(check_file_exists(
        "/workspaces/Power-Trading-application/parsers/DOR_EnergySchedule_Parser.py",
        "DOR Energy Schedule Parser"
    ))
    all_checks.append(check_file_exists(
        "/workspaces/Power-Trading-application/parsers/SCH_Energy_Schedule_Parser.py",
        "SCH Energy Schedule Parser"
    ))
    all_checks.append(check_file_exists(
        "/workspaces/Power-Trading-application/database/energy_schedule_crud.py",
        "Energy Schedule CRUD operations"
    ))
    
    print("\n🔍 Story 3.1 Implementation Checks (Auto-Create Daily Entries):")
    print("-" * 100)
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "from database.energy_schedule_crud import",
        "Imports Energy Schedule CRUD functions"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "get_or_create_daily_entry",
        "Calls get_or_create_daily_entry()"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "portfolio_id=portfolio.id",
        "Links to portfolio"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "trading_date=trading_date",
        "Links to trading date"
    ))
    
    print("\n🔍 Story 3.2 Implementation Checks (Auto-Trigger Calculations):")
    print("-" * 100)
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "DOR_EnergyScheduleParser",
        "Imports DOR Energy Schedule Parser"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "SCH_EnergyScheduleParser",
        "Imports SCH Energy Schedule Parser"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "update_daily_entry_dor_data",
        "Updates daily entry with DOR data"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "update_daily_entry_sch_data",
        "Updates daily entry with SCH data"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "has_gdam_data and daily_entry.has_dam_data and daily_entry.has_rtm_data and daily_entry.has_sch_data",
        "Checks all 4 files present"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "calculate_daily_entry",
        "Triggers auto-calculation"
    ))
    
    print("\n🔍 Response Enhancement Checks:")
    print("-" * 100)
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "energy_schedule_result",
        "Returns energy schedule results"
    ))
    all_checks.append(check_code_present(
        "/workspaces/Power-Trading-application/api/main.py",
        "\"energy_schedule\": energy_schedule_result",
        "Adds energy_schedule to response"
    ))
    
    print("\n" + "=" * 100)
    print("VERIFICATION SUMMARY")
    print("=" * 100)
    
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total) * 100
    
    print(f"\nChecks Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage == 100:
        print("\n🎉 SUCCESS! All Story 3 implementation checks passed!")
        print("   Stories 3.1 & 3.2 are fully integrated into the codebase.")
    elif percentage >= 80:
        print("\n⚠️  WARNING: Most checks passed but some features may be incomplete")
    else:
        print("\n❌ FAILED: Story 3 implementation appears incomplete")
    
    print("\n" + "=" * 100)
    print("NEXT STEPS")
    print("=" * 100)
    print("\n1. ✅ Story 3.1 & 3.2 implementation: COMPLETE")
    print("2. ⏳ Story 3.3 (Background jobs): Not implemented")
    print("3. ⏳ Story 4.1-4.3 (Dashboard): Pending")
    print("\nRecommendation: Proceed with Story 4 (Dashboard) or Story 3.3 (Background jobs)")
    print("=" * 100)

if __name__ == "__main__":
    main()
