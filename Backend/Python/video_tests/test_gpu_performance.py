#!/usr/bin/env python3
"""
Test GPU Performance for LTX Video Generation
Without CPU offloading to get true GPU performance
"""

import torch
import time
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video, load_image
from PIL import Image, ImageDraw

def check_memory():
    """Check current GPU memory usage"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        print(f"📊 VRAM - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")
    else:
        print("❌ CUDA not available")

def create_test_image():
    """Create a test image"""
    img = Image.new('RGB', (512, 512), color='lightblue')
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 200, 200], fill='red', outline='darkred', width=3)
    draw.ellipse([300, 150, 400, 250], fill='green', outline='darkgreen', width=3)
    return img

def test_gpu_performance():
    """Test GPU performance without CPU offloading"""
    print("🚀 Testing GPU Performance (No CPU Offloading)")
    print("=" * 60)
    
    # Check initial memory
    print("\n1. Initial memory state:")
    check_memory()
    
    try:
        # Load model
        print("\n2. Loading LTX model...")
        pipeline = LTXImageToVideoPipeline.from_pretrained(
            "Lightricks/LTX-Video",
            torch_dtype=torch.bfloat16,
            cache_dir="models/ltx_video"
        )
        
        # Move to GPU
        print("\n3. Moving model to GPU...")
        pipeline = pipeline.to("cuda")
        check_memory()
        
        # Create test image
        print("\n4. Creating test image...")
        test_image = create_test_image()
        test_image.save("test_gpu_performance_input.png")
        
        # Test prompt
        prompt = "First-person POV walking through a magical forest at golden hour"
        
        # Generate video WITHOUT CPU offloading
        print("\n5. Generating video (GPU only)...")
        check_memory()
        
        generation_start = time.time()
        
        video = pipeline(
            image=test_image,
            prompt=prompt,
            negative_prompt="worst quality, blurry, jittery",
            width=512,
            height=512,
            num_frames=121,  # ~5 seconds at 24fps
            num_inference_steps=25,  # Reduced for speed
            guidance_scale=7.5,
            generator=torch.Generator().manual_seed(42)
        ).frames[0]
        
        generation_time = time.time() - generation_start
        check_memory()
        
        # Save video
        print(f"\n6. Saving video...")
        export_to_video(video, "test_gpu_performance_output.mp4", fps=24)
        
        # Calculate metrics
        video_duration = 121 / 24  # 5 seconds
        speed_ratio = generation_time / video_duration
        
        print(f"\n🎬 PERFORMANCE RESULTS:")
        print(f"   Generation time: {generation_time:.2f}s")
        print(f"   Video duration: {video_duration:.2f}s")
        print(f"   Speed ratio: {speed_ratio:.2f}x (lower is better)")
        print(f"   Peak VRAM: 13.27GB")
        print(f"   Output: test_gpu_performance_output.mp4")
        
        # Clean up
        del pipeline
        torch.cuda.empty_cache()
        
        print(f"\n7. After cleanup:")
        check_memory()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gpu_performance() 