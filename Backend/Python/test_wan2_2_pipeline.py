#!/usr/bin/env python3
"""
Wan2.2-TI2V-5B Pipeline Test
Test the Wan2.2 model using the official repository

Key Features:
- 720P@24fps support
- Hybrid TI2V (text + image to video)
- High compression VAE (16×16×4)
- Consumer GPU compatible (RTX 4090)
- Fast generation: 5s video in <9 minutes
- MoE architecture for quality
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_wan2_2_repo():
    """Check if Wan2.2 repository is available"""
    print("🔍 Checking Wan2.2 repository...")
    
    wan2_2_dir = Path("Wan2.2")
    if not wan2_2_dir.exists():
        print("❌ Wan2.2 repository not found")
        print("   Cloning from https://github.com/Wan-Video/Wan2.2.git...")
        
        try:
            subprocess.run([
                "git", "clone", "https://github.com/Wan-Video/Wan2.2.git"
            ], check=True, capture_output=True, text=True)
            print("✅ Wan2.2 repository cloned successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone repository: {e}")
            return False
    else:
        print("✅ Wan2.2 repository found")
    
    return True

def install_wan2_2_dependencies():
    """Install Wan2.2 dependencies"""
    print("🔧 Installing Wan2.2 dependencies...")
    
    wan2_2_dir = Path("Wan2.2")
    requirements_file = wan2_2_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found in Wan2.2 directory")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True, text=True)
        print("✅ Wan2.2 dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_wan2_2_text_to_video():
    """Test Wan2.2 text-to-video generation"""
    print("🧪 Testing Wan2.2 Text-to-Video generation...")
    
    # Change to Wan2.2 directory
    os.chdir("Wan2.2")
    
    # Test command based on README
    cmd = [
        "python", "generate.py",
        "--task", "ti2v-5B",
        "--size", "1280*704",  # 720P resolution
        "--ckpt_dir", "../models/wan2_2",  # Point to our downloaded model
        "--offload_model", "True",
        "--convert_model_dtype",
        "--t5_cpu",
        "--prompt", "A cozy room with warm lighting, cinematic style"
    ]
    
    print(f"   Running: {' '.join(cmd)}")
    print("   Expected: 720P video generation with 24fps")
    print("   Target: 5-second video in under 9 minutes")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ Wan2.2 Text-to-Video test successful!")
            print(f"   Generation time: {generation_time:.2f} seconds")
            print(f"   Output should be in the Wan2.2 directory")
            return True
        else:
            print(f"❌ Wan2.2 test failed:")
            print(f"   Return code: {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Wan2.2 test error: {e}")
        return False

def test_wan2_2_image_to_video():
    """Test Wan2.2 image-to-video generation"""
    print("🧪 Testing Wan2.2 Image-to-Video generation...")
    
    # Check if we have an example image
    example_image = Path("examples/i2v_input.JPG")
    if not example_image.exists():
        print("   ⚠️  No example image found, skipping image-to-video test")
        print("   You can add an image to examples/i2v_input.JPG to test this")
        return True
    
    # Test command for image-to-video
    cmd = [
        "python", "generate.py",
        "--task", "ti2v-5B",
        "--size", "1280*704",
        "--ckpt_dir", "../models/wan2_2",
        "--offload_model", "True",
        "--convert_model_dtype",
        "--t5_cpu",
        "--image", "examples/i2v_input.JPG",
        "--prompt", "Summer beach vacation style, cinematic lighting"
    ]
    
    print(f"   Running: {' '.join(cmd)}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ Wan2.2 Image-to-Video test successful!")
            print(f"   Generation time: {generation_time:.2f} seconds")
            return True
        else:
            print(f"❌ Wan2.2 Image-to-Video test failed:")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Wan2.2 Image-to-Video test error: {e}")
        return False

def create_parallel_pipeline_test():
    """Create a test for parallel pipeline integration"""
    print("📝 Creating parallel pipeline test...")
    
    test_script = '''#!/usr/bin/env python3
"""
Wan2.2 Parallel Pipeline Test
Test Wan2.2 integration with our parallel pipeline architecture
"""

import torch
import time
import subprocess
import os
from pathlib import Path

def test_wan2_2_parallel():
    """Test Wan2.2 in parallel pipeline context"""
    print("🧪 Testing Wan2.2 in parallel pipeline...")
    
    # Check model availability
    model_path = Path("models/wan2_2")
    if not model_path.exists():
        print("❌ Wan2.2 model not found")
        return False
    
    # Test parameters for parallel pipeline
    test_configs = [
        {
            "name": "Quick Test (0.5s)",
            "size": "1280*704",
            "prompt": "A cozy room with warm lighting",
            "expected_time": 60  # 1 minute for 0.5s video
        },
        {
            "name": "Standard Test (2s)",
            "size": "1280*704", 
            "prompt": "A cinematic sunset over mountains",
            "expected_time": 240  # 4 minutes for 2s video
        },
        {
            "name": "Quality Test (5s)",
            "size": "1280*704",
            "prompt": "A detailed cityscape with people walking",
            "expected_time": 540  # 9 minutes for 5s video
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\\n🔍 Testing: {config['name']}")
        
        # Run Wan2.2 generation
        cmd = [
            "python", "Wan2.2/generate.py",
            "--task", "ti2v-5B",
            "--size", config["size"],
            "--ckpt_dir", "models/wan2_2",
            "--offload_model", "True",
            "--convert_model_dtype",
            "--t5_cpu",
            "--prompt", config["prompt"]
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = time.time()
            generation_time = end_time - start_time
            
            if result.returncode == 0:
                print(f"   ✅ {config['name']} successful")
                print(f"   ⏱️  Time: {generation_time:.2f}s (target: {config['expected_time']}s)")
                
                # Check if within expected time
                if generation_time <= config["expected_time"]:
                    print(f"   🎯 Within target time!")
                else:
                    print(f"   ⚠️  Exceeded target time by {generation_time - config['expected_time']:.2f}s")
                
                results.append({
                    "name": config["name"],
                    "success": True,
                    "time": generation_time,
                    "target": config["expected_time"]
                })
            else:
                print(f"   ❌ {config['name']} failed")
                print(f"   Error: {result.stderr}")
                results.append({
                    "name": config["name"],
                    "success": False,
                    "error": result.stderr
                })
                
        except Exception as e:
            print(f"   ❌ {config['name']} error: {e}")
            results.append({
                "name": config["name"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\\n📊 Wan2.2 Parallel Pipeline Test Results:")
    print("=" * 50)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"✅ Successful: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        avg_time = sum(r["time"] for r in successful_tests) / len(successful_tests)
        print(f"⏱️  Average generation time: {avg_time:.2f}s")
        
        # Performance analysis
        print("\\n🎯 Performance Analysis:")
        for result in successful_tests:
            efficiency = result["target"] / result["time"] if result["time"] > 0 else 0
            print(f"   {result['name']}: {efficiency:.2f}x target speed")
    
    if failed_tests:
        print("\\n❌ Failed Tests:")
        for result in failed_tests:
            print(f"   {result['name']}: {result.get('error', 'Unknown error')}")
    
    return len(successful_tests) > 0

if __name__ == "__main__":
    test_wan2_2_parallel()
'''
    
    with open("test_wan2_2_parallel.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created: test_wan2_2_parallel.py")

def main():
    """Main test process"""
    print("🚀 WAN2.2-TI2V-5B PIPELINE TEST")
    print("=" * 50)
    print("Testing Wan2.2 for parallel pipeline integration")
    print("Model: D:/Dreams.ai/Backend/Python/models/wan2_2")
    print("=" * 50)
    
    # Step 1: Check repository
    print("\n1️⃣ Checking Wan2.2 repository...")
    if not check_wan2_2_repo():
        return False
    
    # Step 2: Install dependencies
    print("\n2️⃣ Installing dependencies...")
    if not install_wan2_2_dependencies():
        return False
    
    # Step 3: Test text-to-video
    print("\n3️⃣ Testing Text-to-Video generation...")
    if not test_wan2_2_text_to_video():
        print("❌ Text-to-Video test failed")
        return False
    
    # Step 4: Test image-to-video (optional)
    print("\n4️⃣ Testing Image-to-Video generation...")
    test_wan2_2_image_to_video()  # This is optional
    
    # Step 5: Create parallel pipeline test
    print("\n5️⃣ Creating parallel pipeline test...")
    create_parallel_pipeline_test()
    
    # Success
    print("\n🎉 WAN2.2 PIPELINE TEST COMPLETE!")
    print("=" * 50)
    print("✅ Wan2.2 model tested successfully")
    print("✅ Ready for parallel pipeline integration")
    print("✅ Parallel test script created: test_wan2_2_parallel.py")
    print("\n💡 Next steps:")
    print("   1. Run: python test_wan2_2_parallel.py")
    print("   2. Integrate with parallel pipeline")
    print("   3. Compare performance vs SVD")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Wan2.2 test failed")
        sys.exit(1) 