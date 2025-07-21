#!/usr/bin/env python3
"""
Simple test script for the GUI test suite
Tests the API endpoints to ensure they're working correctly
"""

import requests
import json
import time
import sys

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing Dreams.ai GUI Test Suite API...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            status_data = response.json()
            print(f"   Test count: {status_data.get('test_count', 0)}")
            print(f"   Current test: {status_data.get('current_test', 'None')}")
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Get dreams
    try:
        response = requests.get(f"{base_url}/api/dreams", timeout=5)
        if response.status_code == 200:
            dreams = response.json()
            print(f"✅ Dreams endpoint working - {len(dreams)} dreams found")
        else:
            print(f"❌ Dreams endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Dreams endpoint error: {e}")
    
    # Test 3: Run a test
    print("\nRunning a test...")
    try:
        test_data = {
            "prompt": "A magical forest with glowing mushrooms",
            "user_id": "test-user-123"
        }
        response = requests.post(
            f"{base_url}/api/test",
            json=test_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test started: {result.get('message', 'Unknown')}")
            
            # Poll for completion
            print("Polling for test completion...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                try:
                    status_response = requests.get(f"{base_url}/api/status", timeout=5)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_test = status_data.get('current_test')
                        
                        if current_test:
                            status = current_test.get('status')
                            if status == 'completed':
                                print("✅ Test completed successfully!")
                                print(f"   Duration: {current_test.get('duration', 0):.2f}s")
                                break
                            elif status == 'error':
                                print(f"❌ Test failed: {current_test.get('error', 'Unknown error')}")
                                break
                            else:
                                print(f"   Test status: {status}")
                        else:
                            print("   No current test")
                except Exception as e:
                    print(f"   Error polling status: {e}")
            else:
                print("❌ Test timed out")
        else:
            print(f"❌ Test start failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 4: Get updated dreams
    try:
        response = requests.get(f"{base_url}/api/dreams", timeout=5)
        if response.status_code == 200:
            dreams = response.json()
            print(f"\n✅ Final dream count: {len(dreams)}")
            if dreams:
                latest_dream = dreams[-1]
                print(f"   Latest dream: {latest_dream.get('title', 'Untitled')}")
                print(f"   Status: {latest_dream.get('test_status', 'Unknown')}")
                print(f"   Duration: {latest_dream.get('test_duration', 0):.2f}s")
        else:
            print(f"❌ Final dreams check failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Final dreams check error: {e}")
    
    print("\n" + "=" * 50)
    print("API test completed!")
    return True

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1) 