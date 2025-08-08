#!/usr/bin/env python3
"""
Test Stable Video Diffusion (SVD) as LTX Alternative
SVD is much more stable and widely tested than LTX
"""

import torch
import time
import gc
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video
from PIL import Image, ImageDraw

def check_memory():
    """Check current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"📊 VRAM - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB, Total: {total:.1f}GB")
    else:
        print("❌ CUDA not available")

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (576, 1024), color='lightblue')  # SVD uses 576x1024
    draw = ImageDraw.Draw(img)
    
    # Add simple shapes for motion testing
    draw.rectangle([100, 100, 200, 200], fill='red', outline='darkred', width=3)
    draw.ellipse([300, 150, 400, 250], fill='green', outline='darkgreen', width=3)
    
    return img

def test_svd_performance():
    """Test SVD performance"""
    print("🚀 Stable Video Diffusion (SVD) Performance Test")
    print("=" * 60)
    
    # Step 1: Initial memory state
    print("\n1️⃣ Initial memory state:")
    check_memory()
    
    # Step 2: Memory cleanup
    print("\n2️⃣ Memory cleanup:")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    for _ in range(3):
        gc.collect()
    check_memory()
    
    try:
        # Step 3: Load SVD model
        print("\n3️⃣ Loading SVD model...")
        pipeline = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16,
            cache_dir="models/svd"
        )
        
        # Step 4: Move to GPU
        print("\n4️⃣ Moving model to GPU...")
        pipeline = pipeline.to("cuda")
        check_memory()
        
        # Step 5: Create test image
        print("\n5️⃣ Creating test image...")
        test_image = create_test_image()
        test_image.save("test_svd_input.png")
        
        # Step 6: Generate video
        print("\n6️⃣ Generating video with SVD...")
        check_memory()
        
        generation_start = time.time()
        
        # SVD generation parameters
        video = pipeline(
            test_image,
            decode_chunk_size=8,  # Process in chunks for memory efficiency
            motion_bucket_id=127,  # Motion intensity
            fps=7,  # Frames per second
            noise_aug_strength=0.1,  # Noise augmentation
            num_frames=25,  # Number of frames to generate
        ).frames[0]
        
        generation_time = time.time() - generation_start
        check_memory()
        
        # Step 7: Save video
        print(f"\n7️⃣ Saving video...")
        output_path = "test_svd_output.mp4"
        export_to_video(video, output_path, fps=7)
        
        # Step 8: Calculate performance metrics
        video_duration = 25 / 7  # ~3.6 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 SVD PERFORMANCE RESULTS:")
        print(f"   ✅ Generation time: {generation_time:.2f}s")
        print(f"   ✅ Video duration: {video_duration:.2f}s")
        print(f"   ✅ Speed ratio: {speed_ratio:.2f}x (lower is better)")
        print(f"   ✅ Output: {output_path}")
        print(f"   ✅ Status: SUCCESS!")
        
        # Step 9: Cleanup
        print(f"\n8️⃣ Cleanup...")
        del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        check_memory()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during SVD generation: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

def compare_models():
    """Compare SVD vs LTX characteristics"""
    print("\n📊 MODEL COMPARISON: SVD vs LTX")
    print("=" * 50)
    
    comparison = {
        "Stable Video Diffusion (SVD)": {
            "pros": [
                "✅ Much more stable and tested",
                "✅ Better memory management",
                "✅ Faster inference",
                "✅ Active community support",
                "✅ Works with standard diffusers",
                "✅ Good documentation"
            ],
            "cons": [
                "❌ Lower quality than LTX",
                "❌ Limited motion control",
                "❌ Shorter video lengths"
            ]
        },
        "LTX Video": {
            "pros": [
                "✅ Higher quality output",
                "✅ Better motion control",
                "✅ Longer video generation",
                "✅ Advanced features"
            ],
            "cons": [
                "❌ Very unstable/incompatible",
                "❌ Memory issues",
                "❌ Poor documentation",
                "❌ Limited community support",
                "❌ Inference gets stuck"
            ]
        }
    }
    
    for model, details in comparison.items():
        print(f"\n{model}:")
        for pro in details["pros"]:
            print(f"  {pro}")
        for con in details["cons"]:
            print(f"  {con}")

if __name__ == "__main__":
    # Show model comparison
    compare_models()
    
    # Run SVD test
    success = test_svd_performance()
    
    if success:
        print("\n🎉 SUCCESS: SVD video generation working!")
        print("💡 RECOMMENDATION: Use SVD instead of LTX for now")
    else:
        print("\n💥 FAILED: SVD also has issues") 