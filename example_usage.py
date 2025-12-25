"""
Example usage of the chatbot API
"""
import requests
import json


# Configuration
BASE_URL = "http://localhost:8000"
# GANTI DENGAN JWT TOKEN ANDA
JWT_TOKEN = "your_jwt_token_here"


def test_health():
    """Test health endpoint (no auth required)"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_chat(message: str):
    """Test chat endpoint"""
    print(f"Sending message: '{message}'")
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "message": message,
        "top_k": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json=data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nChatbot Response:")
        print("-" * 60)
        print(result["response"])
        print("-" * 60)
        print(f"\nSources used: {len(result['sources'])}")
        if result['sources']:
            print("\nTop 3 sources:")
            for i, source in enumerate(result['sources'][:3], 1):
                print(f"{i}. {source.get('nama_usaha', 'N/A')}")
                print(f"   Score: {source.get('relevance_score', 0):.3f}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "=" * 60 + "\n")


def test_get_businesses():
    """Test get all businesses endpoint"""
    print("Getting all businesses...")
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/businesses",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total businesses: {result['total']}")
        if result['businesses']:
            print(f"\nFirst business:")
            print(json.dumps(result['businesses'][0], indent=2, default=str))
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Geotags Chatbot API - Example Usage")
    print("=" * 60)
    print()
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Chat queries
    test_chat("Cari warung kopi di Balikpapan")
    test_chat("Ada usaha sembako di mana?")
    test_chat("Berapa jumlah usaha yang aktif?")
    
    # Test 3: Get all businesses
    # test_get_businesses()  # Uncomment to test
    
    print("Done!")
