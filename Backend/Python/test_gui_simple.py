"""
Simple test script for the GUI test suite
"""

import requests
import json
import time

def test_gui_functionality():
    """Test the GUI test suite functionality"""
    
    base_url = "http://localhost:5000"
    
    print("Testing Dreams.ai GUI Test Suite...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start it with: python test_gui.py")
        return
    
    # Test 2: Run a pipeline test
    print("\nRunning pipeline test...")
    test_data = {
        "prompt": "A magical forest with glowing mushrooms",
        "user_id": "test-user-123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/test",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Test started: {result}")
            
            # Wait for test to complete
            print("Waiting for test to complete...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                
                status_response = requests.get(f"{base_url}/api/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    
                    if status.get('current_test', {}).get('status') == 'completed':
                        print("✅ Test completed successfully!")
                        break
                    elif status.get('current_test', {}).get('status') == 'error':
                        print(f"❌ Test failed: {status.get('current_test', {}).get('error')}")
                        break
                else:
                    print(f"❌ Failed to get status: {status_response.status_code}")
                    break
            else:
                print("⏰ Test timed out")
        else:
            print(f"❌ Failed to start test: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
    
    # Test 3: Get test results
    print("\nGetting test results...")
    try:
        response = requests.get(f"{base_url}/api/dreams")
        if response.status_code == 200:
            dreams = response.json()
            print(f"✅ Found {len(dreams)} test dreams")
            
            if dreams:
                dream = dreams[0]
                print(f"  - Title: {dream.get('title')}")
                print(f"  - Duration: {dream.get('test_duration', 0):.2f}s")
                print(f"  - Scenes: {len(dream.get('scenes', []))}")
                print(f"  - Has image: {'Yes' if dream.get('generated_image') else 'No'}")
        else:
            print(f"❌ Failed to get dreams: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting results: {e}")
    
    # Test 4: Test image generation
    print("\nTesting image generation...")
    try:
        image_data = {
            "prompt": "A beautiful sunset over mountains",
            "service": "placeholder"
        }
        
        response = requests.post(
            f"{base_url}/api/generate-image",
            json=image_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image generated successfully!")
            print(f"  - Service: {result.get('service')}")
            print(f"  - Filename: {result.get('filename')}")
            print(f"  - Has image data: {'Yes' if result.get('image_data') else 'No'}")
        else:
            print(f"❌ Image generation failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error generating image: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print(f"Open {base_url} in your browser to see the GUI")

if __name__ == "__main__":
    test_gui_functionality() 