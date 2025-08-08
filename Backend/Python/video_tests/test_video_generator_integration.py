#!/usr/bin/env python3
"""
Test script for video_generator.py integration
Tests the updated video generator with working LTX configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.video_generator import get_video_generator, initialize_video_generator
import torch

def test_video_generator():
    """Test the updated video generator"""
    print("🧪 Testing updated video_generator.py...")
    
    # Check GPU
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return False
    
    gpu_name = torch.cuda.get_device_name(0)
    total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"🔧 GPU: {gpu_name}")
    print(f"🔧 Total VRAM: {total_memory:.1f} GB")
    
    # Test video generator initialization
    try:
        print("📥 Initializing video generator...")
        generator = get_video_generator()
        print(f"✅ Generator created with model: {generator.model_id}")
        print(f"✅ Cache directory: {generator.cache_dir}")
        print(f"✅ Mobile config: {generator.mobile_config}")
        
        # Test model loading
        print("🔄 Loading LTX model...")
        success = initialize_video_generator()
        
        if success:
            print("✅ Video generator loaded successfully!")
            
            # Check memory usage
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                reserved = torch.cuda.memory_reserved(0) / 1024**3
                print(f"📊 VRAM allocated: {allocated:.2f} GB")
                print(f"📊 VRAM reserved: {reserved:.2f} GB")
            
            return True
        else:
            print("❌ Failed to load video generator")
            return False
            
    except Exception as e:
        print(f"❌ Video generator test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Video Generator Integration Test")
    print("=" * 50)
    
    success = test_video_generator()
    
    print("=" * 50)
    if success:
        print("🎉 Video generator integration test passed!")
        print("✅ Ready for Dreams.ai pipeline integration")
    else:
        print("❌ Video generator integration test failed")
        sys.exit(1) 