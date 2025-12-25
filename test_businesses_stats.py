"""
Test script for /api/businesses endpoint with statistics
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
# You need to replace this with a valid JWT token
# Get it by calling /api/auth/login first
JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"

def test_businesses_endpoint():
    """Test the /api/businesses endpoint"""
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    print("Testing /api/businesses endpoint...")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/businesses", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✓ Total Businesses: {data['total']}")
            
            # Statistics
            stats = data['statistics']
            print(f"\n✓ Statistics Total: {stats['total']}")
            
            # By Category
            print(f"\n✓ Top 10 Categories:")
            for item in stats['by_category'][:5]:  # Show top 5
                print(f"  - {item['category']}: {item['count']}")
            
            # By District
            print(f"\n✓ By District (Kecamatan):")
            for item in stats['by_district']:
                print(f"  - {item['district']}: {item['count']}")
            
            # By Subdistrict
            print(f"\n✓ Top 10 Subdistricts (Kelurahan):")
            for item in stats['by_subdistrict'][:5]:  # Show top 5
                print(f"  - {item['subdistrict']}: {item['count']}")
            
            # By Status
            print(f"\n✓ By Status:")
            for status, count in stats['by_status'].items():
                print(f"  - {status}: {count}")
            
            # By Source
            print(f"\n✓ By Source:")
            for source, count in stats['by_source'].items():
                print(f"  - {source}: {count}")
            
            print("\n" + "=" * 50)
            print("✓ Test PASSED - Statistics returned successfully!")
            
        elif response.status_code == 401:
            print("\n✗ Authentication failed. Please update JWT_TOKEN in the script.")
            print("  Get a token by calling POST /api/auth/login first.")
        else:
            print(f"\n✗ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Connection Error: Server is not running on http://localhost:5000")
        print("  Please start the server first with:")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_businesses_endpoint()
