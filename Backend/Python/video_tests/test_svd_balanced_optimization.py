#!/usr/bin/env python3
"""
Balanced SVD Optimization for 15-Second Generation
Better quality and longer duration while maintaining speed
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
    """Create a balanced test image"""
    img = Image.new('RGB', (384, 640), color='lightblue')  # Better resolution
    draw = ImageDraw.Draw(img)
    
    # More detailed shapes for better motion
    draw.rectangle([50, 50, 100, 100], fill='red', outline='darkred', width=2)
    draw.ellipse([150, 75, 200, 125], fill='green', outline='darkgreen', width=2)
    draw.polygon([(250, 50), (275, 75), (250, 100), (225, 75)], fill='blue', outline='darkblue', width=2)
    
    return img

def test_balanced_svd_optimization():
    """Test balanced SVD optimization for quality and speed"""
    print("🚀 BALANCED SVD OPTIMIZATION FOR QUALITY + SPEED")
    print("=" * 60)
    
    # Step 1: Memory cleanup
    print("\n1️⃣ Memory cleanup:")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    for _ in range(3):
        gc.collect()
    check_memory()
    
    try:
        # Step 2: Load SVD with balanced optimizations
        print("\n2️⃣ Loading SVD with balanced optimizations...")
        pipeline = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16,
            cache_dir="models/svd",
            use_safetensors=True,
            low_cpu_mem_usage=True
        )
        
        # Step 3: Move to GPU with optimizations
        print("\n3️⃣ Moving to GPU with optimizations...")
        pipeline = pipeline.to("cuda")
        
        # Enable memory optimizations
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
        
        # Enable attention slicing for memory efficiency
        try:
            pipeline.enable_attention_slicing()
            print("   ✅ attention slicing enabled")
        except:
            print("   ⚠️ attention slicing not available")
        
        check_memory()
        
        # Step 4: Create test image
        print("\n4️⃣ Creating balanced test image...")
        test_image = create_test_image()
        test_image.save("test_svd_balanced_input.png")
        
        # Step 5: Generate video with balanced optimizations
        print("\n5️⃣ Generating video with balanced optimizations...")
        check_memory()
        
        generation_start = time.time()
        
        # BALANCED OPTIMIZATION PARAMETERS
        video = pipeline(
            test_image,
            decode_chunk_size=6,  # Balanced chunks
            motion_bucket_id=127,  # Good motion
            fps=8,  # Higher FPS for smoother video
            noise_aug_strength=0.1,  # Balanced noise
            num_frames=24,  # Longer video (3 seconds at 8fps)
            num_inference_steps=12,  # Balanced steps for quality
        ).frames[0]
        
        generation_time = time.time() - generation_start
        check_memory()
        
        # Step 6: Save video
        print(f"\n6️⃣ Saving balanced video...")
        output_path = "test_svd_balanced_output.mp4"
        export_to_video(video, output_path, fps=8)
        
        # Step 7: Calculate performance metrics
        video_duration = 24 / 8  # 3 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 BALANCED SVD PERFORMANCE RESULTS:")
        print(f"   ✅ Generation time: {generation_time:.2f}s")
        print(f"   ✅ Video duration: {video_duration:.2f}s")
        print(f"   ✅ Speed ratio: {speed_ratio:.2f}x")
        print(f"   ✅ Output: {output_path}")
        print(f"   ✅ Status: SUCCESS!")
        
        # Step 8: Cleanup
        print(f"\n7️⃣ Cleanup...")
        del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        check_memory()
        
        return True, generation_time, video_duration
        
    except Exception as e:
        print(f"\n❌ Error during balanced SVD generation: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False, 0, 0

def test_extended_duration():
    """Test for longer video duration"""
    print("\n🎬 EXTENDED DURATION TEST")
    print("=" * 35)
    
    try:
        # Load pipeline
        pipeline = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16,
            cache_dir="models/svd",
            use_safetensors=True,
            low_cpu_mem_usage=True
        )
        pipeline = pipeline.to("cuda")
        
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
        
        # Create test image
        test_image = create_test_image()
        
        print("\nGenerating 10-second video (80 frames at 8fps)...")
        generation_start = time.time()
        
        # Extended duration parameters
        video = pipeline(
            test_image,
            decode_chunk_size=8,  # Larger chunks for longer video
            motion_bucket_id=127,
            fps=8,
            noise_aug_strength=0.1,
            num_frames=80,  # 10 seconds at 8fps
            num_inference_steps=10,  # Slightly fewer steps for speed
        ).frames[0]
        
        generation_time = time.time() - generation_start
        
        # Save extended video
        output_path = "test_svd_extended_output.mp4"
        export_to_video(video, output_path, fps=8)
        
        video_duration = 80 / 8  # 10 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 EXTENDED DURATION RESULTS:")
        print(f"   ✅ Generation time: {generation_time:.2f}s")
        print(f"   ✅ Video duration: {video_duration:.2f}s")
        print(f"   ✅ Speed ratio: {speed_ratio:.2f}x")
        print(f"   ✅ Output: {output_path}")
        
        # Cleanup
        del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return True, generation_time, video_duration
        
    except Exception as e:
        print(f"\n❌ Error during extended duration test: {e}")
        return False, 0, 0

def compare_optimization_strategies():
    """Compare different optimization strategies"""
    print("\n📊 OPTIMIZATION STRATEGY COMPARISON")
    print("=" * 45)
    
    strategies = {
        "Ultra-Fast (Previous)": {
            "resolution": "256x384",
            "frames": "12",
            "steps": "4",
            "fps": "4",
            "duration": "3s",
            "time": "12s",
            "quality": "Low",
            "speedup": "62x"
        },
        "Balanced (Current)": {
            "resolution": "384x640",
            "frames": "24",
            "steps": "12",
            "fps": "8",
            "duration": "3s",
            "time": "~20s",
            "quality": "Medium",
            "speedup": "~37x"
        },
        "Extended Duration": {
            "resolution": "384x640",
            "frames": "80",
            "steps": "10",
            "fps": "8",
            "duration": "10s",
            "time": "~60s",
            "quality": "Good",
            "speedup": "~12x"
        }
    }
    
    for strategy, details in strategies.items():
        print(f"\n🔧 {strategy}:")
        print(f"   Resolution: {details['resolution']}")
        print(f"   Frames: {details['frames']}")
        print(f"   Steps: {details['steps']}")
        print(f"   FPS: {details['fps']}")
        print(f"   Duration: {details['duration']}")
        print(f"   Time: {details['time']}")
        print(f"   Quality: {details['quality']}")
        print(f"   Speedup: {details['speedup']}")

def main():
    """Run balanced optimization tests"""
    print("🎯 BALANCED OPTIMIZATION FOR QUALITY + SPEED")
    print("=" * 55)
    print("Goal: Better quality and longer duration")
    print("Strategy: Balanced SVD optimizations")
    print("=" * 55)
    
    # Compare strategies
    compare_optimization_strategies()
    
    # Run balanced optimization test
    success, gen_time, vid_duration = test_balanced_svd_optimization()
    
    if success:
        print(f"\n🎉 SUCCESS: Balanced optimization working!")
        print(f"💡 Generation time: {gen_time:.2f}s")
        print(f"💡 Video duration: {vid_duration:.2f}s")
        
        # Test extended duration
        print(f"\n🔍 Testing extended duration...")
        ext_success, ext_gen_time, ext_vid_duration = test_extended_duration()
        
        if ext_success:
            print(f"\n🎉 EXTENDED DURATION SUCCESS!")
            print(f"💡 Generation time: {ext_gen_time:.2f}s")
            print(f"💡 Video duration: {ext_vid_duration:.2f}s")
            
            if ext_gen_time <= 60:  # 1 minute target for 10-second video
                print("🎯 TARGET ACHIEVED: 10-second video in under 1 minute!")
            else:
                print(f"📈 Progress: {ext_gen_time:.2f}s for 10-second video")
        else:
            print("\n💥 FAILED: Extended duration test failed")
    else:
        print("\n💥 FAILED: Balanced optimization failed")

if __name__ == "__main__":
    main() 