#!/usr/bin/env python3
"""
Test GPU Memory Usage for LTX Models
"""

import torch
import time
from diffusers import LTXImageToVideoPipeline

def check_memory():
    """Check current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        print(f"📊 VRAM - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")
    else:
        print("❌ CUDA not available")

def test_gpu_usage():
    """Test GPU memory usage with LTX model"""
    print("🚀 Testing GPU Memory Usage")
    print("=" * 50)
    
    # Check initial memory
    print("\n1. Initial memory state:")
    check_memory()
    
    # Load model
    print("\n2. Loading LTX model...")
    check_memory()
    
    try:
        pipeline = LTXImageToVideoPipeline.from_pretrained(
            "Lightricks/LTX-Video",
            torch_dtype=torch.bfloat16,
            cache_dir="models/ltx_video"
        )
        
        print("\n3. Model loaded, moving to GPU...")
        check_memory()
        
        # Move to GPU
        pipeline = pipeline.to("cuda")
        print("\n4. Model moved to GPU:")
        check_memory()
        
        # Test without CPU offloading
        print("\n5. Testing generation WITHOUT CPU offloading:")
        check_memory()
        
        # Create a simple test tensor to verify GPU is working
        test_tensor = torch.randn(1, 3, 512, 512).cuda()
        print(f"\n6. Test tensor created on GPU: {test_tensor.device}")
        check_memory()
        
        # Now test with CPU offloading
        print("\n7. Enabling CPU offloading...")
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
            print("✅ CPU offloading enabled")
        check_memory()
        
        # Clean up
        del test_tensor
        del pipeline
        torch.cuda.empty_cache()
        
        print("\n8. After cleanup:")
        check_memory()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gpu_usage() 