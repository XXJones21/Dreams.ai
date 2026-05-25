"""
Test ModelManager Pipeline Integration
Comprehensive test to verify that ModelManager works properly in pipeline context.
"""

import time
import logging
from core.model_manager import ModelManager
from core.pipeline_instance import PipelineInstance
from core.agents import State

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_manager_pipeline_integration():
    """Test ModelManager integration with pipeline"""
    print("🧪 Testing ModelManager Pipeline Integration")
    print("=" * 60)
    
    try:
        # Test 1: Initialize ModelManager
        print("1. Initializing ModelManager...")
        model_manager = ModelManager.get_instance()
        print("✅ ModelManager instance created")
        
        # Test 2: Check initial status
        print("\n2. Checking initial status...")
        status = model_manager.get_status()
        print(f"Initial status: {status}")
        
        # Test 3: Preload models for pipeline
        print("\n3. Preloading models for pipeline...")
        start_time = time.time()
        model_manager.preload_for_pipeline()
        load_time = time.time() - start_time
        print(f"✅ Models preloaded in {load_time:.2f}s")
        
        # Test 4: Check status after preloading
        print("\n4. Checking status after preloading...")
        status = model_manager.get_status()
        print(f"Status after preloading: {status}")
        
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
            {"role": "system", "content": "You are a helpful assistant. Respond with exactly 'Hello, Pipeline integration test successful!'"},
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
        
        # Test 9: Pipeline integration test
        print("\n9. Testing pipeline integration...")
        test_state = State({
            "messages": [{"role": "user", "content": "A magical forest with glowing mushrooms"}],
            "user_id": "test-user"
        })
        
        try:
            pipeline_instance = PipelineInstance(test_state)
            print("✅ PipelineInstance created successfully")
            print(f"✅ Dream ID: {pipeline_instance.dream_id}")
        except Exception as e:
            print(f"❌ PipelineInstance creation failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ModelManager Pipeline Integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_manager_pipeline_integration()

