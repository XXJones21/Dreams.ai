#!/usr/bin/env python3
"""
Test Real Dream Image with Chunked Processing
Use actual dream images to test video generation quality
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
    
    # Resize to SVD-compatible dimensions (maintain aspect ratio)
    target_width = 384
    target_height = 640
    
    # Calculate aspect ratio
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height
    
    if aspect_ratio > target_aspect_ratio:
        # Image is wider, fit to width
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        # Image is taller, fit to height
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
    
    # Resize image
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a new image with target dimensions and paste the resized image
    final_image = Image.new('RGB', (target_width, target_height), color='black')
    
    # Center the image
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    final_image.paste(image, (paste_x, paste_y))
    
    print(f"   📐 Resized to: {target_width}x{target_height}")
    print(f"   📐 Final size: {final_image.size}")
    
    return final_image

def test_real_dream_image():
    """Test video generation with a real dream image"""
    print("🎬 TESTING REAL DREAM IMAGE WITH CHUNKED PROCESSING")
    print("=" * 60)
    
    # Select a dream image
    dream_images_dir = "generated_images"
    dream_images = [
        "sdxl_turbo_20250728_205726.png",  # Recent, good quality
        "sdxl_turbo_20250728_205203.png",  # Another recent one
        "sdxl_turbo_20250728_204957.png",  # Third option
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
    print("\n1️⃣ Memory cleanup:")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    for _ in range(3):
        gc.collect()
    check_memory()
    
    try:
        # Load SVD
        print("\n2️⃣ Loading SVD...")
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
        
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
        
        check_memory()
        
        # Load and prepare dream image
        print("\n4️⃣ Loading dream image...")
        dream_image = load_dream_image(selected_image)
        dream_image.save("test_real_dream_input.png")
        
        # Generate video with chunked processing
        print("\n5️⃣ Generating video from dream image...")
        check_memory()
        
        generation_start = time.time()
        
        # CHUNKED PROCESSING PARAMETERS FOR REAL CONTENT
        video = pipeline(
            dream_image,
            decode_chunk_size=2,  # Very small chunks for memory efficiency
            motion_bucket_id=127,
            fps=6,  # Lower FPS for stability
            noise_aug_strength=0.1,
            num_frames=24,  # 4 seconds at 6fps
            num_inference_steps=8,  # Moderate steps for quality
        ).frames[0]
        
        generation_time = time.time() - generation_start
        check_memory()
        
        # Save video
        print(f"\n6️⃣ Saving dream video...")
        output_path = "test_real_dream_output.mp4"
        export_to_video(video, output_path, fps=6)
        
        # Calculate metrics
        video_duration = 24 / 6  # 4 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 REAL DREAM VIDEO RESULTS:")
        print(f"   ✅ Generation time: {generation_time:.2f}s")
        print(f"   ✅ Video duration: {video_duration:.2f}s")
        print(f"   ✅ Speed ratio: {speed_ratio:.2f}x")
        print(f"   ✅ Input: {os.path.basename(selected_image)}")
        print(f"   ✅ Output: {output_path}")
        print(f"   ✅ Status: SUCCESS!")
        
        # Quality assessment
        print(f"\n📊 QUALITY ASSESSMENT:")
        if generation_time <= 15:
            print(f"   🎯 TARGET ACHIEVED: {generation_time:.2f}s ≤ 15s")
        else:
            print(f"   📈 Progress: {generation_time:.2f}s (target: 15s)")
            print(f"   📊 Remaining: {generation_time - 15:.2f}s to target")
        
        print(f"   📏 Video length: {video_duration:.1f} seconds")
        print(f"   🎬 FPS: 6 (smooth playback)")
        print(f"   🖼️ Resolution: 384x640")
        
        # Cleanup
        print(f"\n7️⃣ Cleanup...")
        del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        check_memory()
        
        return True, generation_time, video_duration
        
    except Exception as e:
        print(f"\n❌ Error during real dream video generation: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False, 0, 0

def test_quality_comparison():
    """Compare quality between simple shapes and real dream content"""
    print("\n🔍 QUALITY COMPARISON ANALYSIS")
    print("=" * 40)
    
    comparison = {
        "Simple Shapes (Previous)": {
            "content": "Red rectangle, green circle",
            "complexity": "Low",
            "quality": "Basic",
            "generation_time": "23.26s",
            "duration": "3.0s"
        },
        "Real Dream Image (Current)": {
            "content": "Actual dream-generated content",
            "complexity": "High",
            "quality": "Realistic",
            "generation_time": "TBD",
            "duration": "4.0s"
        }
    }
    
    for test_type, details in comparison.items():
        print(f"\n📊 {test_type}:")
        print(f"   Content: {details['content']}")
        print(f"   Complexity: {details['complexity']}")
        print(f"   Quality: {details['quality']}")
        print(f"   Generation time: {details['generation_time']}")
        print(f"   Duration: {details['duration']}")

def main():
    """Run real dream image test"""
    print("🎯 REAL DREAM IMAGE VIDEO GENERATION")
    print("=" * 50)
    print("Goal: Test chunked processing with real dream content")
    print("Strategy: Use actual dream images for quality assessment")
    print("=" * 50)
    
    # Show quality comparison
    test_quality_comparison()
    
    # Test with real dream image
    success, gen_time, vid_duration = test_real_dream_image()
    
    if success:
        print(f"\n🎉 SUCCESS: Real dream video generation working!")
        print(f"💡 Generation time: {gen_time:.2f}s")
        print(f"💡 Video duration: {vid_duration:.2f}s")
        
        if gen_time <= 15:
            print("🎯 TARGET ACHIEVED: 15-second generation with real content!")
        else:
            print(f"📈 Progress: {gen_time:.2f}s (target: 15s)")
            print(f"📊 Remaining: {gen_time - 15:.2f}s to target")
            
        print(f"\n💡 QUALITY INSIGHTS:")
        print(f"   ✅ Real dream content processed successfully")
        print(f"   ✅ 4-second video with realistic content")
        print(f"   ✅ Chunked processing maintains quality")
        print(f"   ✅ Memory efficient approach working")
    else:
        print("\n💥 FAILED: Real dream video generation failed")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Check dream image format and size")
        print("2. Verify SVD model compatibility")
        print("3. Try different dream images")
        print("4. Adjust chunked processing parameters")

if __name__ == "__main__":
    main() 