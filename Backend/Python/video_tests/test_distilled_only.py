#!/usr/bin/env python3
"""
Test LTX-Video-0.9.7-distilled model in isolation to check memory usage
"""

import os
import torch
import gc
import time
from diffusers import LTXConditionPipeline

def check_memory():
    """Check current VRAM usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"VRAM - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB, Total: {total:.1f}GB")
        return allocated, reserved
    return 0, 0

def main():
    print("🧪 Testing LTX-Video-0.9.7-distilled model in isolation")
    print("=" * 60)
    
    # Set memory optimization
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
    
    # Clear any existing memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    for _ in range(3):
        gc.collect()
    
    print("📊 Initial memory state:")
    check_memory()
    
    try:
        print("\n📥 Loading LTX-Video-0.9.7-distilled...")
        start_time = time.time()
        
        pipeline = LTXConditionPipeline.from_pretrained(
            "Lightricks/LTX-Video-0.9.7-distilled",
            torch_dtype=torch.bfloat16,
            cache_dir="models/ltx_video"
        )
        
        print(f"✅ Model loaded in {time.time() - start_time:.2f}s")
        print("📊 Memory after loading (before GPU):")
        check_memory()
        
        print("\n🔄 Moving to GPU...")
        pipeline = pipeline.to("cuda")
        
        print("📊 Memory after GPU move:")
        allocated, reserved = check_memory()
        
        print("\n🔄 Enabling CPU offloading...")
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
            print("✅ CPU offloading enabled")
        
        print("📊 Memory after CPU offloading:")
        check_memory()
        
        print(f"\n✅ SUCCESS: Distilled model loaded successfully!")
        print(f"Peak VRAM usage: {max(allocated, reserved):.2f}GB")
        
        # Cleanup
        pipeline.to("cpu")
        del pipeline
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        gc.collect()
        
        print("\n📊 Memory after cleanup:")
        check_memory()
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        print("📊 Memory at failure:")
        check_memory()

if __name__ == "__main__":
    main() 