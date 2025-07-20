#!/usr/bin/env python3
"""
Direct test of error handling.
"""

import requests
import json

def test_error_handling():
    """Test error handling directly."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing error handling directly...")
    
    # Test 404 endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/invalid/endpoint", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            print("Response data:")
            print(json.dumps(data, indent=2))
            
            # Check required fields
            required_fields = ['success', 'error_code', 'trace_id', 'support_link']
            missing_or_null = [field for field in required_fields if field not in data or data[field] is None]
            
            if missing_or_null:
                print(f"❌ Missing or null fields: {missing_or_null}")
                return False
            else:
                print("✅ All required error fields present and not null")
                return True
        else:
            print(f"❌ Expected 404 status code, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting direct error test...")
    success = test_error_handling()
    
    if success:
        print("\n✅ Test passed! Error responses include trace_id, error_code, and support_link.")
    else:
        print("\n❌ Test failed. Check the error response implementation.") 