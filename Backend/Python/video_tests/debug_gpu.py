#!/usr/bin/env python3
"""
Simple GPU debug script to check what's happening with CUDA
"""

import sys
import traceback

def check_imports():
    """Check all required imports"""
    try:
        import torch
        print(f"✅ PyTorch imported successfully: {torch.__version__}")
        
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU count: {torch.cuda.device_count()}")
            print(f"GPU name: {torch.cuda.get_device_name(0)}")
            print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        
        return True
    except Exception as e:
        print(f"❌ PyTorch import failed: {e}")
        return False

def check_nvidia_ml():
    """Check nvidia-ml-py"""
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        print(f"✅ nvidia-ml-py working: {info.used / 1024**3:.2f}GB used")
        return True
    except Exception as e:
        print(f"❌ nvidia-ml-py failed: {e}")
        return False

def check_diffusers():
    """Check diffusers import"""
    try:
        from diffusers import LTXImageToVideoPipeline
        print("✅ Diffusers LTX import successful")
        return True
    except Exception as e:
        print(f"❌ Diffusers import failed: {e}")
        return False

def main():
    print("🔧 GPU Debug Check")
    print("=" * 40)
    
    # Check imports step by step
    if not check_imports():
        return False
    
    if not check_nvidia_ml():
        print("⚠️ Will use torch memory monitoring instead")
    
    if not check_diffusers():
        return False
    
    print("✅ All checks passed!")
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Debug script failed: {e}")
        traceback.print_exc() 