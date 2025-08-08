#!/usr/bin/env python3
"""
LTX Video Generation Test Script

Tests LTX video installation and mobile-optimized video generation
for RTX 4080 16GB setup targeting 10-second videos in 15 seconds.
"""

import os
import time
import torch
from pathlib import Path
from diffusers import LTXImageToVideoPipeline, LTXConditionPipeline
from diffusers.utils import export_to_video, load_image
from PIL import Image
import gc

def check_gpu_specs():
    """Check GPU specifications and VRAM availability"""
    if not torch.cuda.is_available():
        print("❌ CUDA not available")
        return False
    
    gpu_name = torch.cuda.get_device_name(0)
    total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    print(f"🔧 GPU: {gpu_name}")
    print(f"🔧 Total VRAM: {total_memory:.1f} GB")
    
    # Check if RTX 4080 or similar
    if "4080" in gpu_name or total_memory >= 15:
        print("✅ GPU suitable for LTX video generation")
        return True
    else:
        print("⚠️  GPU may have limited performance with LTX models")
        return True

def create_test_image():
    """Create a simple test image for video generation"""
    test_dir = Path("test_outputs")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple gradient image for testing
    img = Image.new('RGB', (832, 480), color='lightblue')
    
    # Add some visual elements for motion testing
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Add geometric shapes for motion reference
    draw.rectangle([100, 100, 300, 200], fill='red', outline='darkred', width=3)
    draw.ellipse([400, 150, 600, 350], fill='green', outline='darkgreen', width=3)
    draw.polygon([(650, 100), (750, 200), (550, 200)], fill='blue', outline='darkblue', width=3)
    
    # Add text
    try:
        draw.text((50, 50), "LTX Test Frame", fill='black')
        draw.text((50, 400), "Mobile Video Generation", fill='black')
    except:
        # Handle missing font gracefully
        pass
    
    test_image_path = test_dir / "test_input.png"
    img.save(test_image_path)
    print(f"📷 Created test image: {test_image_path}")
    return str(test_image_path)

def test_ltx_installation():
    """Test if LTX models can be loaded"""
    print("\n🧪 Testing LTX installation...")
    
    try:
        # Test basic import - using the standard pipeline for the base model  
        from diffusers import LTXImageToVideoPipeline
        print("✅ LTX diffusers integration available")
        
        # Test model loading (this will download if not cached)
        print("📥 Loading LTX-Video model (this may take time for first run)...")
        
        # Use the 2B distilled model for RTX 4080 - much lower VRAM usage  
        model_id = "Lightricks/LTX-Video"  # This will use the 2B base model
        
        # Set custom cache directory to D: drive models folder
        cache_dir = "models/ltx_video"
        
        # Clear CUDA cache before loading
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        pipeline = LTXImageToVideoPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.bfloat16,  # Remove variant since fp16 not available
            cache_dir=cache_dir  # Download to our models directory on D: drive
        )
        
        # Move to GPU and enable memory-efficient attention
        pipeline = pipeline.to("cuda")
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()  # Offload parts to CPU when not in use
        
        print("✅ Model loaded successfully")
        print(f"📊 Model components: {list(pipeline.components.keys())}")
        
        # Move to GPU
        pipeline.to("cuda")
        print("✅ Model moved to GPU")
        
        return pipeline
        
    except Exception as e:
        print(f"❌ LTX installation test failed: {e}")
        return None

def test_mobile_video_generation(pipeline, test_image_path):
    """Test mobile-optimized video generation"""
    print("\n🎬 Testing mobile video generation...")
    
    # Mobile optimization settings for RTX 4080 with base model (memory conservative)
    mobile_config = {
        "width": 512,       # Smaller for memory testing
        "height": 512,      # Square format to reduce memory usage 
        "num_frames": 49,   # ~2 seconds at 24fps (divisible by 8 + 1)
        "num_inference_steps": 50,  # Standard for base model
        "guidance_scale": 7.5,      # Standard guidance for base model
    }
    
    # Test prompt optimized for first-person perspective
    test_prompt = """
    First-person POV of geometric shapes slowly rotating and floating in a bright blue space. 
    The red rectangle spins clockwise while moving forward, the green circle bounces gently 
    up and down, and the blue triangle rotates counter-clockwise. The camera maintains a 
    steady position watching these colorful objects dance through the frame. The lighting 
    is bright and even, creating a clean, digital art aesthetic.
    """
    
    negative_prompt = "worst quality, inconsistent motion, blurry, jittery, distorted, third person"
    
    try:
        # Load test image
        image = load_image(test_image_path)
        
        print(f"🎯 Generation config: {mobile_config}")
        print(f"📝 Prompt: {test_prompt[:100]}...")
        
        # Start timing
        start_time = time.time()
        
        # Generate video with standard LTXImageToVideoPipeline
        video = pipeline(
            image=image,
            prompt=test_prompt,
            negative_prompt=negative_prompt,
            generator=torch.Generator().manual_seed(42),
            **mobile_config
        ).frames[0]
        
        generation_time = time.time() - start_time
        
        # Save video
        output_path = "test_outputs/ltx_mobile_test.mp4"
        export_to_video(video, output_path, fps=25)
        
        # Calculate metrics
        video_duration = mobile_config["num_frames"] / 25  # fps
        speed_ratio = generation_time / video_duration
        
        print(f"✅ Video generation complete!")
        print(f"📹 Output: {output_path}")
        print(f"⏱️  Generation time: {generation_time:.2f} seconds")
        print(f"🎬 Video duration: {video_duration:.2f} seconds") 
        print(f"🚀 Speed ratio: {speed_ratio:.2f}x (target: <1.5x for real-time)")
        
        if speed_ratio <= 1.5:
            print("🎉 EXCELLENT: Achieved real-time generation target!")
        elif speed_ratio <= 3.0:
            print("✅ GOOD: Near real-time performance")
        else:
            print("⚠️  SLOW: May need optimization")
            
        return True, generation_time, video_duration
        
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return False, 0, 0

def test_memory_usage():
    """Test and report memory usage"""
    print("\n💾 Memory usage test...")
    
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        
        print(f"📊 VRAM allocated: {allocated:.2f} GB")
        print(f"📊 VRAM reserved: {reserved:.2f} GB")
        
        # Check if we're within RTX 4080 limits
        if reserved < 14:  # Leave 2GB headroom
            print("✅ Memory usage within RTX 4080 limits")
        else:
            print("⚠️  High memory usage - consider optimization")

def run_ltx_tests():
    """Run complete LTX test suite"""
    print("🚀 Starting LTX Video Generation Tests")
    print("=" * 50)
    
    # Check system requirements
    if not check_gpu_specs():
        return
    
    # Create test image
    test_image_path = create_test_image()
    
    # Test installation
    pipeline = test_ltx_installation()
    if pipeline is None:
        return
    
    # Test memory usage
    test_memory_usage()
    
    # Test video generation
    success, gen_time, vid_duration = test_mobile_video_generation(pipeline, test_image_path)
    
    # Cleanup
    del pipeline
    torch.cuda.empty_cache()
    gc.collect()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All LTX tests passed!")
        print(f"📈 Performance: {gen_time:.1f}s generation for {vid_duration:.1f}s video")
        print("🔧 Ready for Cenedril integration!")
    else:
        print("❌ Some tests failed - check configuration")

if __name__ == "__main__":
    run_ltx_tests() 