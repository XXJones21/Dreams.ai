#!/usr/bin/env python3
"""
Quality-Speed Final Push
Build on quality-speed balance (21.11s) with minimal quality sacrifices
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
    
    # QUALITY-SPEED FINAL PUSH: Maintain quality resolution
    target_width = 384  # Same as quality-speed balance
    target_height = 640  # Same as quality-speed balance
    
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
    
    print(f"   📐 Resized to: {target_width}x{target_height} (QUALITY-SPEED FINAL PUSH)")
    print(f"   📐 Final size: {final_image.size}")
    
    return final_image

def test_quality_speed_final_push():
    """Test final push based on quality-speed balance with minimal quality sacrifices"""
    print("🚀 QUALITY-SPEED FINAL PUSH")
    print("=" * 45)
    print("Goal: 15-second generation with minimal quality loss")
    print("Strategy: Build on quality-speed balance (21.11s)")
    print("=" * 45)
    
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
    print("\n1️⃣ Quality-speed final push memory cleanup:")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        torch.cuda.reset_peak_memory_stats()
    for _ in range(5):
        gc.collect()
    check_memory()
    
    try:
        # Load SVD with quality-speed final push optimizations
        print("\n2️⃣ Loading SVD with quality-speed final push optimizations...")
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
        
        # Quality-speed final push optimizations
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
        print("\n4️⃣ Loading dream image with quality-speed final push resizing...")
        dream_image = load_dream_image(selected_image)
        dream_image.save("test_quality_speed_final_push_input.png")
        
        # Generate video with quality-speed final push parameters
        print("\n5️⃣ Generating video with quality-speed final push optimizations...")
        check_memory()
        
        generation_start = time.time()
        
        # QUALITY-SPEED FINAL PUSH PARAMETERS
        # Based on quality-speed balance but with minimal optimizations
        video = pipeline(
            dream_image,
            decode_chunk_size=1,  # Minimal chunks for speed
            motion_bucket_id=127,
            fps=6,  # Same as quality-speed balance
            noise_aug_strength=0.1,  # Same as quality-speed balance
            num_frames=16,  # 2.67 seconds at 6fps (reduced from 18 for speed)
            num_inference_steps=6,  # Same as quality-speed balance (maintain quality)
        ).frames[0]
        
        generation_time = time.time() - generation_start
        check_memory()
        
        # Save video
        print(f"\n6️⃣ Saving quality-speed final push video...")
        output_path = "test_quality_speed_final_push_output.mp4"
        export_to_video(video, output_path, fps=6)
        
        # Calculate metrics
        video_duration = 16 / 6  # 2.67 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 QUALITY-SPEED FINAL PUSH RESULTS:")
        print(f"   ✅ Generation time: {generation_time:.2f}s")
        print(f"   ✅ Video duration: {video_duration:.2f}s")
        print(f"   ✅ Speed ratio: {speed_ratio:.2f}x")
        print(f"   ✅ Input: {os.path.basename(selected_image)}")
        print(f"   ✅ Output: {output_path}")
        print(f"   ✅ Status: SUCCESS!")
        
        # Quality assessment
        print(f"\n📊 QUALITY-SPEED FINAL PUSH ASSESSMENT:")
        if generation_time <= 15:
            print(f"   🎯 TARGET ACHIEVED: {generation_time:.2f}s ≤ 15s")
            print(f"   🏆 MISSION ACCOMPLISHED!")
        else:
            print(f"   📈 Progress: {generation_time:.2f}s (target: 15s)")
            print(f"   📊 Remaining: {generation_time - 15:.2f}s to target")
        
        print(f"   📏 Video length: {video_duration:.1f} seconds")
        print(f"   🎬 FPS: 6 (same as quality-speed balance)")
        print(f"   🖼️ Resolution: 384x640 (same as quality-speed balance)")
        
        # Cleanup
        print(f"\n7️⃣ Cleanup...")
        del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        check_memory()
        
        return True, generation_time, video_duration
        
    except Exception as e:
        print(f"\n❌ Error during quality-speed final push generation: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False, 0, 0

def compare_quality_approaches():
    """Compare different quality approaches"""
    print("\n📊 QUALITY APPROACHES COMPARISON")
    print("=" * 45)
    
    approaches = {
        "Gold Standard (Original)": {
            "resolution": "384x640",
            "frames": "24",
            "steps": "8",
            "fps": "6",
            "time": "37.33s",
            "quality": "Gold Standard",
            "duration": "4.0s"
        },
        "Quality-Speed Balance": {
            "resolution": "384x640",
            "frames": "18",
            "steps": "6",
            "fps": "6",
            "time": "21.11s",
            "quality": "Very High",
            "duration": "3.0s"
        },
        "Final Gold Standard Push": {
            "resolution": "384x640",
            "frames": "15",
            "steps": "5",
            "fps": "6",
            "time": "16.52s",
            "quality": "Lower",
            "duration": "2.5s"
        },
        "Quality-Speed Final Push": {
            "resolution": "384x640",
            "frames": "16",
            "steps": "6",
            "fps": "6",
            "time": "TBD",
            "quality": "High",
            "duration": "2.67s"
        }
    }
    
    for approach, details in approaches.items():
        print(f"\n🔧 {approach}:")
        print(f"   Resolution: {details['resolution']}")
        print(f"   Frames: {details['frames']}")
        print(f"   Steps: {details['steps']}")
        print(f"   FPS: {details['fps']}")
        print(f"   Time: {details['time']}")
        print(f"   Quality: {details['quality']}")
        print(f"   Duration: {details['duration']}")

def analyze_quality_strategy():
    """Analyze the quality preservation strategy"""
    print("\n💡 QUALITY PRESERVATION STRATEGY")
    print("=" * 45)
    
    strategy = [
        "✅ Maintain 384x640 resolution (gold standard quality)",
        "✅ Keep 6 FPS (smooth motion like gold standard)",
        "✅ Keep noise_aug_strength: 0.1 (same as gold standard)",
        "✅ Keep steps: 6 (same as quality-speed balance)",
        "✅ Reduce frames: 18 → 16 (11% reduction only)",
        "✅ Use decode_chunk_size: 1 (minimal chunks)",
        "✅ Expected time savings: ~2-3 seconds",
        "✅ Expected quality: Very close to quality-speed balance"
    ]
    
    print("Strategy to achieve 15-second target while preserving quality:")
    for item in strategy:
        print(f"   {item}")
    
    print(f"\n🎯 TARGET CALCULATION:")
    print(f"   Quality-speed balance time: 21.11s")
    print(f"   Target time: 15.00s")
    print(f"   Required reduction: 6.11s")
    print(f"   Strategy: Minimal frame reduction (11%) + chunk optimization")

def main():
    """Run quality-speed final push test"""
    print("🎯 QUALITY-SPEED FINAL PUSH FOR 15-SECOND TARGET")
    print("=" * 60)
    print("Goal: Achieve 15-second generation with minimal quality loss")
    print("Strategy: Build on quality-speed balance (21.11s)")
    print("=" * 60)
    
    # Analyze quality strategy
    analyze_quality_strategy()
    
    # Show quality approaches comparison
    compare_quality_approaches()
    
    # Test quality-speed final push
    success, gen_time, vid_duration = test_quality_speed_final_push()
    
    if success:
        print(f"\n🎉 SUCCESS: Quality-speed final push working!")
        print(f"💡 Generation time: {gen_time:.2f}s")
        print(f"💡 Video duration: {vid_duration:.2f}s")
        
        if gen_time <= 15:
            print("🎯 TARGET ACHIEVED: 15-second generation with minimal quality loss!")
            print("🏆 MISSION ACCOMPLISHED!")
        else:
            print(f"📈 Progress: {gen_time:.2f}s (target: 15s)")
            print(f"📊 Remaining: {gen_time - 15:.2f}s to target")
            
        print(f"\n💡 QUALITY-SPEED FINAL PUSH INSIGHTS:")
        print(f"   ✅ Maintained 384x640 resolution (gold standard)")
        print(f"   ✅ Kept 6 FPS for smooth motion")
        print(f"   ✅ Kept steps: 6 (same as quality-speed balance)")
        print(f"   ✅ Reduced frames: 18 → 16 (11% reduction only)")
        print(f"   ✅ Preserved noise_aug_strength: 0.1")
        print(f"   ✅ Used decode_chunk_size: 1")
        
        # Calculate improvement from quality-speed balance
        previous_time = 21.11  # From quality-speed balance test
        improvement = ((previous_time - gen_time) / previous_time) * 100
        print(f"   📈 Speed improvement: {improvement:.1f}%")
        
        # Calculate total improvement from gold standard
        gold_standard_time = 37.33  # From original gold standard
        total_improvement = ((gold_standard_time - gen_time) / gold_standard_time) * 100
        print(f"   📈 Total improvement: {total_improvement:.1f}%")
        
        print(f"\n🎨 QUALITY ASSESSMENT:")
        print(f"   ✅ Same resolution as gold standard")
        print(f"   ✅ Same FPS as gold standard")
        print(f"   ✅ Same steps as quality-speed balance")
        print(f"   ✅ Same noise settings as gold standard")
        print(f"   ✅ Reduced duration: 3s → 2.67s")
        print(f"   ✅ Expected quality: Very close to quality-speed balance")
        
    else:
        print("\n💥 FAILED: Quality-speed final push failed")
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Stick with quality-speed balance (21.11s)")
        print("2. Accept 21.11s as the optimal quality-speed balance")
        print("3. Consider hardware upgrades for further optimization")
        print("4. Explore alternative video models")

if __name__ == "__main__":
    main() 