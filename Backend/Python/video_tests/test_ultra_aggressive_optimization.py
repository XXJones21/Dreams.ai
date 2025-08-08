#!/usr/bin/env python3
"""
Ultra-Aggressive Optimization for 15-Second Target
Combine multiple optimization strategies for maximum speed
"""

import torch
import time
import gc
import os
from PIL import Image
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video

def check_memory():
    """Check current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"📊 VRAM - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB, Total: {total:.1f}GB")
    else:
        print("❌ CUDA not available")

def load_dream_image(image_path):
    """Load and prepare a dream image for video generation"""
    print(f"📸 Loading dream image: {image_path}")
    
    # Load the image
    image = Image.open(image_path)
    
    # Get original dimensions
    width, height = image.size
    print(f"   📐 Original size: {width}x{height}")
    
    # ULTRA-AGGRESSIVE: Use smaller resolution for speed
    target_width = 256  # Reduced from 384
    target_height = 384  # Reduced from 640
    
    # Calculate aspect ratio
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height
    
    if aspect_ratio > target_aspect_ratio:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
    
    # Resize image
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a new image with target dimensions
    final_image = Image.new('RGB', (target_width, target_height), color='black')
    
    # Center the image
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    final_image.paste(image, (paste_x, paste_y))
    
    print(f"   📐 Resized to: {target_width}x{target_height} (ULTRA-AGGRESSIVE)")
    print(f"   📐 Final size: {final_image.size}")
    
    return final_image

def test_ultra_aggressive_optimization():
    """Test ultra-aggressive optimization for 15-second target"""
    print("🚀 ULTRA-AGGRESSIVE OPTIMIZATION FOR 15-SECOND TARGET")
    print("=" * 65)
    
    # Select a dream image
    dream_images_dir = "generated_images"
    dream_images = [
        "sdxl_turbo_20250728_205726.png",  # Same image for comparison
        "sdxl_turbo_20250728_205203.png",
        "sdxl_turbo_20250728_204957.png",
    ]
    
    # Use the first available image
    selected_image = None
    for image_name in dream_images:
        image_path = os.path.join(dream_images_dir, image_name)
        if os.path.exists(image_path):
            selected_image = image_path
            break
    
    if not selected_image:
        print("❌ No dream images found!")
        return False, 0, 0
    
    print(f"🎨 Selected dream image: {os.path.basename(selected_image)}")
    
    # Memory cleanup
    print("\n1️⃣ Ultra-aggressive memory cleanup:")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.reset_peak_memory_stats()
    for _ in range(5):
        gc.collect()
    check_memory()
    
    try:
        # Load SVD with ultra-aggressive optimizations
        print("\n2️⃣ Loading SVD with ultra-aggressive optimizations...")
        pipeline = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16,
            cache_dir="models/svd",
            use_safetensors=True,
            low_cpu_mem_usage=True
        )
        
        # Move to GPU
        print("\n3️⃣ Moving to GPU...")
        pipeline = pipeline.to("cuda")
        
        # Ultra-aggressive optimizations
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
        
        # Enable attention slicing for memory efficiency
        try:
            pipeline.enable_attention_slicing()
            print("   ✅ attention slicing enabled")
        except:
            print("   ⚠️ attention slicing not available")
        
        check_memory()
        
        # Load and prepare dream image
        print("\n4️⃣ Loading dream image with ultra-aggressive resizing...")
        dream_image = load_dream_image(selected_image)
        dream_image.save("test_ultra_aggressive_input.png")
        
        # Generate video with ultra-aggressive parameters
        print("\n5️⃣ Generating video with ultra-aggressive optimizations...")
        check_memory()
        
        generation_start = time.time()
        
        # ULTRA-AGGRESSIVE PARAMETERS
        video = pipeline(
            dream_image,
            decode_chunk_size=1,  # Minimal chunks (like GGUF efficiency)
            motion_bucket_id=127,
            fps=4,  # Lower FPS for speed (was 6)
            noise_aug_strength=0.05,  # Minimal noise (was 0.1)
            num_frames=16,  # 4 seconds at 4fps (was 24 frames at 6fps)
            num_inference_steps=4,  # Ultra-reduced steps (was 8)
        ).frames[0]
        
        generation_time = time.time() - generation_start
        check_memory()
        
        # Save video
        print(f"\n6️⃣ Saving ultra-aggressive video...")
        output_path = "test_ultra_aggressive_output.mp4"
        export_to_video(video, output_path, fps=4)
        
        # Calculate metrics
        video_duration = 16 / 4  # 4 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 ULTRA-AGGRESSIVE RESULTS:")
        print(f"   ✅ Generation time: {generation_time:.2f}s")
        print(f"   ✅ Video duration: {video_duration:.2f}s")
        print(f"   ✅ Speed ratio: {speed_ratio:.2f}x")
        print(f"   ✅ Input: {os.path.basename(selected_image)}")
        print(f"   ✅ Output: {output_path}")
        print(f"   ✅ Status: SUCCESS!")
        
        # Quality assessment
        print(f"\n📊 ULTRA-AGGRESSIVE ASSESSMENT:")
        if generation_time <= 15:
            print(f"   🎯 TARGET ACHIEVED: {generation_time:.2f}s ≤ 15s")
        else:
            print(f"   📈 Progress: {generation_time:.2f}s (target: 15s)")
            print(f"   📊 Remaining: {generation_time - 15:.2f}s to target")
        
        print(f"   📏 Video length: {video_duration:.1f} seconds")
        print(f"   🎬 FPS: 4 (smooth playback)")
        print(f"   🖼️ Resolution: 256x384 (ultra-aggressive)")
        
        # Cleanup
        print(f"\n7️⃣ Cleanup...")
        del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        check_memory()
        
        return True, generation_time, video_duration
        
    except Exception as e:
        print(f"\n❌ Error during ultra-aggressive generation: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False, 0, 0

def compare_optimization_levels():
    """Compare different optimization levels"""
    print("\n📊 OPTIMIZATION LEVEL COMPARISON")
    print("=" * 45)
    
    levels = {
        "Standard": {
            "resolution": "384x640",
            "frames": "24",
            "steps": "8",
            "fps": "6",
            "time": "37.33s",
            "quality": "High"
        },
        "Chunked": {
            "resolution": "384x640",
            "frames": "18",
            "steps": "6",
            "fps": "6",
            "time": "23.26s",
            "quality": "Good"
        },
        "Ultra-Aggressive": {
            "resolution": "256x384",
            "frames": "16",
            "steps": "4",
            "fps": "4",
            "time": "TBD",
            "quality": "Medium"
        }
    }
    
    for level, details in levels.items():
        print(f"\n🔧 {level}:")
        print(f"   Resolution: {details['resolution']}")
        print(f"   Frames: {details['frames']}")
        print(f"   Steps: {details['steps']}")
        print(f"   FPS: {details['fps']}")
        print(f"   Time: {details['time']}")
        print(f"   Quality: {details['quality']}")

def main():
    """Run ultra-aggressive optimization test"""
    print("🎯 ULTRA-AGGRESSIVE OPTIMIZATION FOR 15-SECOND TARGET")
    print("=" * 65)
    print("Goal: Achieve 15-second generation with real dream content")
    print("Strategy: Combine multiple aggressive optimizations")
    print("=" * 65)
    
    # Show optimization comparison
    compare_optimization_levels()
    
    # Test ultra-aggressive optimization
    success, gen_time, vid_duration = test_ultra_aggressive_optimization()
    
    if success:
        print(f"\n🎉 SUCCESS: Ultra-aggressive optimization working!")
        print(f"💡 Generation time: {gen_time:.2f}s")
        print(f"💡 Video duration: {vid_duration:.2f}s")
        
        if gen_time <= 15:
            print("🎯 TARGET ACHIEVED: 15-second generation with ultra-aggressive optimizations!")
        else:
            print(f"📈 Progress: {gen_time:.2f}s (target: 15s)")
            print(f"📊 Remaining: {gen_time - 15:.2f}s to target")
            
        print(f"\n💡 ULTRA-AGGRESSIVE INSIGHTS:")
        print(f"   ✅ Reduced resolution: 256x384 (was 384x640)")
        print(f"   ✅ Fewer frames: 16 (was 24)")
        print(f"   ✅ Fewer steps: 4 (was 8)")
        print(f"   ✅ Lower FPS: 4 (was 6)")
        print(f"   ✅ Minimal chunks: 1 (was 2)")
        
        # Calculate improvement
        previous_time = 37.33  # From real dream test
        improvement = ((previous_time - gen_time) / previous_time) * 100
        print(f"   📈 Speed improvement: {improvement:.1f}%")
        
    else:
        print("\n💥 FAILED: Ultra-aggressive optimization failed")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Try even smaller resolution")
        print("2. Reduce frames further")
        print("3. Use fewer inference steps")
        print("4. Consider different video models")

if __name__ == "__main__":
    main() 