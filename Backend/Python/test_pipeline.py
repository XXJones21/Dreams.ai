#!/usr/bin/env python3
"""
Simple test script for the main pipeline
Tests the graph.invoke() functionality to ensure it works correctly
"""

import sys
import os
import time

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pipeline():
    """Test the main pipeline"""
    print("Testing Dreams.ai Pipeline...")
    print("=" * 50)
    
    try:
        # Import the graph
        from main import graph
        print("✅ Successfully imported graph")
        
        # Test state
        test_state = {
            "messages": [{"role": "user", "content": "A magical forest with glowing mushrooms"}],
            "user_id": "test-user-123"
        }
        
        print(f"✅ Test state created with prompt: {test_state['messages'][0]['content']}")
        
        # Run the pipeline
        print("Running pipeline...")
        start_time = time.time()
        
        result = graph.invoke(test_state)
        
        duration = time.time() - start_time
        print(f"✅ Pipeline completed in {duration:.2f} seconds")
        
        # Check results
        dream_id = result.get("id")
        if dream_id:
            print(f"✅ Dream ID generated: {dream_id}")
            
            # Check if IMN file was created
            imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
            if os.path.exists(imn_file_path):
                print(f"✅ IMN file created: {imn_file_path}")
                
                # Try to read the IMN file
                from core.imn_utils import read_imn
                imn_data = read_imn(imn_file_path)
                if imn_data:
                    print("✅ IMN file can be read successfully")
                    print(f"   Dream name: {imn_data.get('pre_production', {}).get('dream_name', 'Unknown')}")
                    print(f"   Scenes generated: {len(imn_data.get('in_production', []))}")
                    print(f"   Has image prompt: {'Yes' if imn_data.get('pre_production', {}).get('first_frame_prompt') else 'No'}")
                else:
                    print("❌ Failed to read IMN file")
            else:
                print(f"❌ IMN file not found: {imn_file_path}")
        else:
            print("❌ No dream ID generated")
            return False
        
        print("\n" + "=" * 50)
        print("Pipeline test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1) 