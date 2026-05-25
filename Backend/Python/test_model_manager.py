"""
Test ModelManager Implementation
Quick test to verify that models are loading and being stored correctly.
"""

import time
import logging
from core.model_manager import ModelManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_manager():
    """Test ModelManager implementation"""
    print("🧪 Testing ModelManager Implementation")
    print("=" * 50)
    
    try:
        # Test 1: Get ModelManager instance
        print("1. Getting ModelManager instance...")
        model_manager = ModelManager.get_instance()
        print("✅ ModelManager instance created")
        
        # Test 2: Check initial status
        print("\n2. Checking initial status...")
        status = model_manager.get_status()
        print(f"Initial status: {status}")
        
        # Test 3: Load all models
        print("\n3. Loading all models...")
        start_time = time.time()
        model_manager.load_all_models()
        load_time = time.time() - start_time
        print(f"✅ Models loaded in {load_time:.2f}s")
        
        # Test 4: Check status after loading
        print("\n4. Checking status after loading...")
        status = model_manager.get_status()
        print(f"Status after loading: {status}")
        
        # Test 5: Test LLM access
        print("\n5. Testing LLM access...")
        llm = model_manager.get_llm()
        if llm:
            print("✅ LLM retrieved successfully")
        else:
            print("❌ Failed to retrieve LLM")
            
        # Test 6: Test image model access
        print("\n6. Testing image model access...")
        sdxl_turbo = model_manager.get_sdxl_turbo()
        if sdxl_turbo:
            print("✅ SDXL Turbo retrieved successfully")
        else:
            print("❌ Failed to retrieve SDXL Turbo")
            
        sdxl_lora = model_manager.get_sdxl_lora()
        if sdxl_lora:
            print("✅ SDXL LoRA retrieved successfully")
        else:
            print("❌ Failed to retrieve SDXL LoRA")
        
        # Test 7: Simple LLM prompt test
        print("\n7. Testing LLM with simple prompt...")
        test_prompt = [
            {"role": "system", "content": "You are a helpful assistant. Respond with exactly 'Hello, ModelManager test successful!'"},
            {"role": "user", "content": "Say hello"}
        ]
        
        try:
            response = llm.invoke(test_prompt)
            print(f"✅ LLM Response: {response.content}")
        except Exception as e:
            print(f"❌ LLM test failed: {e}")
        
        # Test 8: Memory usage
        print("\n8. Checking memory usage...")
        memory = model_manager.get_memory_usage()
        print(f"Memory usage: {memory}")
        
        print("\n" + "=" * 50)
        print("🎉 ModelManager test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_manager()
