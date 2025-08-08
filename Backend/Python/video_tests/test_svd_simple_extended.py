#!/usr/bin/env python3
"""
Simple Extended SVD Test
Reliable approach for longer, better quality videos
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

def create_simple_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (384, 640), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Simple shapes for testing
    draw.rectangle([50, 50, 100, 100], fill='red', outline='darkred', width=2)
    draw.ellipse([150, 75, 200, 125], fill='green', outline='darkgreen', width=2)
    
    return img

def test_simple_extended_svd():
    """Test simple extended SVD generation"""
    print("🚀 SIMPLE EXTENDED SVD TEST")
    print("=" * 40)
    
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
        
        # Enable CPU offloading for memory efficiency
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
        
        check_memory()
        
        # Create test image
        print("\n4️⃣ Creating test image...")
        test_image = create_simple_test_image()
        test_image.save("test_svd_simple_input.png")
        
        # Generate video with simple parameters
        print("\n5️⃣ Generating extended video...")
        check_memory()
        
        generation_start = time.time()
        
        # SIMPLE EXTENDED PARAMETERS
        video = pipeline(
            test_image,
            decode_chunk_size=4,  # Small chunks to avoid memory issues
            motion_bucket_id=127,
            fps=6,  # Lower FPS for stability
            noise_aug_strength=0.1,
            num_frames=48,  # 8 seconds at 6fps
            num_inference_steps=8,  # Moderate steps for speed
        ).frames[0]
        
        generation_time = time.time() - generation_start
        check_memory()
        
        # Save video
        print(f"\n6️⃣ Saving extended video...")
        output_path = "test_svd_simple_extended_output.mp4"
        export_to_video(video, output_path, fps=6)
        
        # Calculate metrics
        video_duration = 48 / 6  # 8 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 SIMPLE EXTENDED RESULTS:")
        print(f"   ✅ Generation time: {generation_time:.2f}s")
        print(f"   ✅ Video duration: {video_duration:.2f}s")
        print(f"   ✅ Speed ratio: {speed_ratio:.2f}x")
        print(f"   ✅ Output: {output_path}")
        print(f"   ✅ Status: SUCCESS!")
        
        # Cleanup
        print(f"\n7️⃣ Cleanup...")
        del pipeline
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        check_memory()
        
        return True, generation_time, video_duration
        
    except Exception as e:
        print(f"\n❌ Error during simple extended SVD generation: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False, 0, 0

def test_medium_quality():
    """Test medium quality with reasonable duration"""
    print("\n🎬 MEDIUM QUALITY TEST")
    print("=" * 30)
    
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
        test_image = create_simple_test_image()
        
        print("\nGenerating 5-second video (30 frames at 6fps)...")
        generation_start = time.time()
        
        # Medium quality parameters
        video = pipeline(
            test_image,
            decode_chunk_size=6,  # Medium chunks
            motion_bucket_id=127,
            fps=6,
            noise_aug_strength=0.1,
            num_frames=30,  # 5 seconds at 6fps
            num_inference_steps=10,  # More steps for quality
        ).frames[0]
        
        generation_time = time.time() - generation_start
        
        # Save video
        output_path = "test_svd_medium_quality_output.mp4"
        export_to_video(video, output_path, fps=6)
        
        video_duration = 30 / 6  # 5 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 MEDIUM QUALITY RESULTS:")
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
        print(f"\n❌ Error during medium quality test: {e}")
        return False, 0, 0

def main():
    """Run simple extended tests"""
    print("🎯 SIMPLE EXTENDED SVD TESTING")
    print("=" * 45)
    print("Goal: Longer, better quality videos")
    print("Strategy: Simple, reliable approach")
    print("=" * 45)
    
    # Test simple extended
    success, gen_time, vid_duration = test_simple_extended_svd()
    
    if success:
        print(f"\n🎉 SUCCESS: Simple extended working!")
        print(f"💡 Generation time: {gen_time:.2f}s")
        print(f"💡 Video duration: {vid_duration:.2f}s")
        
        # Test medium quality
        print(f"\n🔍 Testing medium quality...")
        med_success, med_gen_time, med_vid_duration = test_medium_quality()
        
        if med_success:
            print(f"\n🎉 MEDIUM QUALITY SUCCESS!")
            print(f"💡 Generation time: {med_gen_time:.2f}s")
            print(f"💡 Video duration: {med_vid_duration:.2f}s")
            
            print(f"\n📊 COMPARISON:")
            print(f"   Extended (8s): {gen_time:.2f}s generation")
            print(f"   Medium (5s): {med_gen_time:.2f}s generation")
            
            if gen_time <= 60:  # 1 minute target for 8-second video
                print("🎯 TARGET ACHIEVED: 8-second video in under 1 minute!")
            else:
                print(f"📈 Progress: {gen_time:.2f}s for 8-second video")
        else:
            print("\n💥 FAILED: Medium quality test failed")
    else:
        print("\n💥 FAILED: Simple extended test failed")

if __name__ == "__main__":
    main() 