import requests
import json

print("Testing Backend Search Endpoint")
print("=" * 50)

try:
    url = 'http://localhost:8000/search'
    params = {'query': 'milk'}
    
    print(f"\nRequest: GET {url}?query={params['query']}")
    
    response = requests.get(url, params=params)
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
    print(f"Response Length: {len(response.text)} bytes")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n✓ Valid JSON Response")
            print(f"Number of results: {len(data)}")
            if data:
                print(f"\nFirst result:")
                print(json.dumps(data[0], indent=2))
        except json.JSONDecodeError as e:
            print(f"\n✗ Invalid JSON Response")
            print(f"Error: {e}")
            print(f"Raw response: {response.text[:500]}")
    else:
        print(f"\n✗ Error Response")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n✗ Request Failed")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
