import requests
import json

print("=" * 50)
print("API TESTING")
print("=" * 50)

# Test 1: Health Check
print("\n1. Testing Health Check Endpoint...")
try:
    r = requests.get('http://localhost:8000/')
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Search
print("\n2. Testing Search Endpoint (query='milk')...")
try:
    r = requests.get('http://localhost:8000/search?query=milk')
    print(f"   Status: {r.status_code}")
    results = r.json()
    print(f"   Results: {len(results)} products found")
    if results:
        print(f"   First result: {results[0]['name']} - Rs.{results[0]['price']} ({results[0]['store_name']})")
        print(f"   Similarity score: {results[0].get('similarity_score', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Stores
print("\n3. Testing Stores Endpoint...")
try:
    r = requests.get('http://localhost:8000/stores')
    print(f"   Status: {r.status_code}")
    stores = r.json()
    print(f"   Stores: {len(stores)} stores found")
    for store in stores:
        print(f"     - {store['name']}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("API TESTING COMPLETE")
print("=" * 50)
