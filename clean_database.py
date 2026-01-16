"""
Clean duplicate SCH-created clients from Railway database
Keeps only the 5 main clients (Tata, Adani, TNEB, BSES, BESCOM)
"""

import requests

RAILWAY_URL = "https://power-trading-application-production.up.railway.app"

def main():
    print("="*70)
    print("DATABASE CLEANUP - Remove Duplicate SCH Clients")
    print("="*70)
    
    # Get current clients
    response = requests.get(f"{RAILWAY_URL}/api/clients")
    data = response.json()
    
    print(f"\nCurrent clients: {data['count']}")
    
    # Show which clients to keep vs delete
    keep_clients = []
    delete_clients = []
    
    for client in data['clients']:
        entity_id = client['entity_id']
        
        # Keep main clients (A2AR0NPT000X pattern and old NEFA)
        if entity_id.startswith('A2AR0NPT000') or entity_id == 'IEX260114SCH':
            keep_clients.append(client)
            print(f"✅ KEEP: {client['entity_name']} ({entity_id})")
        else:
            # These are the duplicate SCH-created clients
            delete_clients.append(client)
            print(f"❌ DELETE: {client['entity_name']} ({entity_id})")
    
    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  Keep: {len(keep_clients)} clients")
    print(f"  Delete: {len(delete_clients)} duplicate clients")
    print(f"{'='*70}")
    
    if delete_clients:
        print("\n⚠️  NOTE: Currently no DELETE endpoint in API")
        print("   Options:")
        print("   1. Add DELETE endpoint to API")
        print("   2. Manually delete from Railway PostgreSQL database")
        print("   3. Drop all tables and re-upload clean data")
        print(f"\nClient IDs to delete: {[c['id'] for c in delete_clients]}")

if __name__ == "__main__":
    main()
