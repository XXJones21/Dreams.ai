#!/usr/bin/env python3
"""
Test script to verify GGUF model setup is working correctly.
Run this to ensure the Llama 3.1 GGUF model is properly configured.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import core modules
sys.path.append(str(Path(__file__).parent))

def test_gguf_model():
    """Test that the GGUF model loads and responds correctly."""
    
    print("🔧 Testing GGUF Model Setup...")
    print("=" * 50)
    
    # Check if model file exists
    model_path = "models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    print(f"📁 Checking model file: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ ERROR: Model file not found at {model_path}")
        print("   Please ensure the GGUF model is in the correct location.")
        return False
    
    print(f"✅ Model file found ({os.path.getsize(model_path) / (1024**3):.1f} GB)")
    
    # Test importing dependencies
    print("\n📦 Testing dependencies...")
    try:
        from langchain_community.llms import LlamaCpp
        print("✅ langchain-community imported successfully")
    except ImportError as e:
        print(f"❌ ERROR importing langchain-community: {e}")
        print("   Run: pip install langchain-community")
        return False
    
    try:
        import filelock
        print("✅ filelock imported successfully")
    except ImportError as e:
        print(f"❌ ERROR importing filelock: {e}")
        print("   Run: pip install filelock")
        return False
    
    # Test loading the model
    print("\n🤖 Testing model loading...")
    try:
        from langchain_community.chat_models import ChatLlamaCpp
        llm = ChatLlamaCpp(
            model_path=model_path,
            temperature=0.7,
            max_tokens=100,  # Reduced for testing
            top_p=0.9,
            verbose=False,
            n_ctx=2048,  # Reduced for testing
            n_threads=8,  # Conservative for testing
            n_batch=64,
            use_mmap=True,
            f16_kv=True,
        )
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ ERROR loading model: {e}")
        print("   This might be due to insufficient RAM or incompatible model format.")
        return False
    
    # Test a simple prompt
    print("\n💬 Testing model response...")
    try:
        test_prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nSay hello in exactly 3 words.<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        response = llm.invoke(test_prompt)
        print(f"✅ Model response: '{response.strip()}'")
        
        if len(response.strip()) > 0:
            print("✅ Model is responding correctly")
        else:
            print("⚠️  WARNING: Model returned empty response")
            
    except Exception as e:
        print(f"❌ ERROR getting model response: {e}")
        return False
    
    # Test the helper functions
    print("\n🔧 Testing helper functions...")
    try:
        from core.agents import format_prompt_for_llama, invoke_llm
        
        test_messages = [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "Say 'test successful' and nothing else."}
        ]
        
        formatted = format_prompt_for_llama(test_messages)
        print("✅ format_prompt_for_llama working")
        
        response = invoke_llm(test_messages)
        print(f"✅ invoke_llm working: '{response.strip()}'")
        
    except Exception as e:
        print(f"❌ ERROR testing helper functions: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 GGUF Model Setup Test PASSED!")
    print("✅ Ready to use local Llama 3.1 model instead of Ollama")
    return True

if __name__ == "__main__":
    success = test_gguf_model()
    sys.exit(0 if success else 1) 