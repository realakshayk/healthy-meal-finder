#!/usr/bin/env python3
"""
Simple test to verify error handling works correctly.
"""

import requests
import json

def test_simple_error():
    """Test basic error handling."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing simple error handling...")
    
    # Test 404 endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/invalid/endpoint", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 404:
            data = response.json()
            print("✅ 404 response includes:")
            print(f"   - success: {data.get('success')}")
            print(f"   - error_code: {data.get('error_code')}")
            print(f"   - trace_id: {data.get('trace_id')}")
            print(f"   - support_link: {data.get('support_link')}")
            
            # Check if all required fields are present and not null
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
    print("🚀 Starting simple error test...")
    print("   Make sure the API server is running on http://localhost:8000")
    print()
    
    success = test_simple_error()
    
    if success:
        print("\n✅ Test passed! Error responses include trace_id, error_code, and support_link.")
    else:
        print("\n❌ Test failed. Check the error response implementation.") 