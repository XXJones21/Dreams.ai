#!/usr/bin/env python3
"""
Test GGUF Integration with LTX Models
Explore if we can use GGUF optimization for LTX video generation
"""

import torch
import time
from pathlib import Path

def test_gguf_availability():
    """Test if GGUF libraries are available"""
    print("🔍 Testing GGUF Availability")
    print("=" * 40)
    
    try:
        import llama_cpp
        print("✅ llama-cpp-python available")
        print(f"   Version: {llama_cpp.__version__}")
    except ImportError:
        print("❌ llama-cpp-python not available")
        print("   Install with: pip install llama-cpp-python")
    
    try:
        import ctransformers
        print("✅ ctransformers available")
        print(f"   Version: {ctransformers.__version__}")
    except ImportError:
        print("❌ ctransformers not available")
        print("   Install with: pip install ctransformers")
    
    try:
        import transformers
        print("✅ transformers available")
        print(f"   Version: {transformers.__version__}")
    except ImportError:
        print("❌ transformers not available")

def test_ltx_model_variants():
    """Test different LTX model variants"""
    print("\n🔍 Testing LTX Model Variants")
    print("=" * 40)
    
    model_variants = [
        "Lightricks/LTX-Video",
        "Lightricks/LTX-Video-0.9.7-distilled",
        "Lightricks/LTX-Video-2B",
        "Lightricks/LTX-Video-base",
    ]
    
    for model_id in model_variants:
        print(f"\nTesting: {model_id}")
        try:
            from diffusers import LTXImageToVideoPipeline
            
            # Quick test - just try to load the model
            pipeline = LTXImageToVideoPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                cache_dir="models/ltx_video",
                local_files_only=False  # Allow download
            )
            print(f"   ✅ {model_id} - Loaded successfully")
            
            # Test GPU move
            pipeline = pipeline.to("cuda")
            print(f"   ✅ {model_id} - Moved to GPU")
            
            del pipeline
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"   ❌ {model_id} - Failed: {str(e)[:100]}...")

def test_alternative_video_models():
    """Test alternative video generation models"""
    print("\n🔍 Testing Alternative Video Models")
    print("=" * 40)
    
    alternatives = [
        ("Stable Video Diffusion", "stabilityai/stable-video-diffusion-img2vid-xt"),
        ("AnimateDiff", "runwayml/stable-diffusion-v1-5"),  # Base for AnimateDiff
        ("ModelScope", "damo-vilab/text-to-video-ms-1.7b"),
    ]
    
    for name, model_id in alternatives:
        print(f"\nTesting: {name} ({model_id})")
        try:
            if "stable-video-diffusion" in model_id:
                from diffusers import StableVideoDiffusionPipeline
                pipeline = StableVideoDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    cache_dir="models/alternative_video"
                )
                print(f"   ✅ {name} - Loaded successfully")
                
            elif "text-to-video" in model_id:
                from diffusers import DiffusionPipeline
                pipeline = DiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    cache_dir="models/alternative_video"
                )
                print(f"   ✅ {name} - Loaded successfully")
            
            # Test GPU move
            pipeline = pipeline.to("cuda")
            print(f"   ✅ {name} - Moved to GPU")
            
            del pipeline
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"   ❌ {name} - Failed: {str(e)[:100]}...")

def test_environment_optimization():
    """Test different environment configurations"""
    print("\n🔍 Environment Optimization Tests")
    print("=" * 40)
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Test different precision modes
    precision_modes = [
        ("FP32", torch.float32),
        ("FP16", torch.float16),
        ("BF16", torch.bfloat16),
    ]
    
    for name, dtype in precision_modes:
        try:
            # Create a test tensor
            test_tensor = torch.randn(1, 3, 512, 512, dtype=dtype).cuda()
            print(f"   ✅ {name} - Tensor creation successful")
            del test_tensor
        except Exception as e:
            print(f"   ❌ {name} - Failed: {str(e)[:50]}...")

def main():
    """Run all tests"""
    print("🚀 GGUF + LTX Integration Testing")
    print("=" * 60)
    
    # Test 1: GGUF availability
    test_gguf_availability()
    
    # Test 2: LTX model variants
    test_ltx_model_variants()
    
    # Test 3: Alternative video models
    test_alternative_video_models()
    
    # Test 4: Environment optimization
    test_environment_optimization()
    
    print("\n📋 RECOMMENDATIONS:")
    print("1. If GGUF available: Try converting LTX to GGUF format")
    print("2. If not: Test alternative video models (SVD, AnimateDiff)")
    print("3. Environment: Consider downgrading PyTorch/CUDA versions")
    print("4. Model variants: Try distilled or smaller LTX models")

if __name__ == "__main__":
    main() 