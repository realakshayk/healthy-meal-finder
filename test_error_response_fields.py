#!/usr/bin/env python3
"""
Test script to verify that error responses include trace_id, error_code, and support_link fields.
"""

import requests
import json
import sys

def test_error_response_fields():
    """Test that error responses include the required fields."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing error response fields...")
    
    # Test 1: Invalid API key (should return 401 with structured error)
    print("\n1. Testing invalid API key...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/meals/find",
            headers={"X-API-Key": "invalid_key"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            data = response.json()
            print("   ✅ Error response includes:")
            print(f"      - success: {data.get('success')}")
            print(f"      - error_code: {data.get('error_code')}")
            print(f"      - trace_id: {data.get('trace_id')}")
            print(f"      - support_link: {data.get('support_link')}")
            
            # Verify all required fields are present
            required_fields = ['success', 'error_code', 'trace_id', 'support_link']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            else:
                print("   ✅ All required error fields present")
        else:
            print("   ❌ Expected 401 status code")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test 2: Invalid endpoint (should return 404 with structured error)
    print("\n2. Testing invalid endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/invalid/endpoint",
            headers={"X-API-Key": "test_key"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            print("   ✅ 404 response includes:")
            print(f"      - success: {data.get('success')}")
            print(f"      - error_code: {data.get('error_code')}")
            print(f"      - trace_id: {data.get('trace_id')}")
            print(f"      - support_link: {data.get('support_link')}")
            
            # Verify all required fields are present
            required_fields = ['success', 'error_code', 'trace_id', 'support_link']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            else:
                print("   ✅ All required error fields present")
        else:
            print("   ❌ Expected 404 status code")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Test 3: Invalid request data (should return 422 with structured error)
    print("\n3. Testing invalid request data...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/meals/find",
            headers={"X-API-Key": "test_key", "Content-Type": "application/json"},
            json={"invalid": "data"},  # Invalid request body
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 422:
            data = response.json()
            print("   ✅ 422 response includes:")
            print(f"      - success: {data.get('success')}")
            print(f"      - error_code: {data.get('error_code')}")
            print(f"      - trace_id: {data.get('trace_id')}")
            print(f"      - support_link: {data.get('support_link')}")
            
            # Verify all required fields are present
            required_fields = ['success', 'error_code', 'trace_id', 'support_link']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            else:
                print("   ✅ All required error fields present")
        else:
            print("   ❌ Expected 422 status code")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    print("\n🎉 All error response field tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting error response field tests...")
    print("   Make sure the API server is running on http://localhost:8000")
    print()
    
    success = test_error_response_fields()
    
    if success:
        print("\n✅ All tests passed! Error responses include trace_id, error_code, and support_link.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the error response implementation.")
        sys.exit(1) 