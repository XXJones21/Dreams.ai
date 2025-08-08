#!/usr/bin/env python3
"""
Wan2.2-TI2V-5B Installation Script
Based on official requirements from https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B

Installation Steps:
1. Clone Wan2.2 repository
2. Install dependencies (torch >= 2.4.0)
3. Download model to models/wan2_2 folder
4. Test installation
"""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✅ Python version OK")
    return True

def check_torch_version():
    """Check if PyTorch version meets requirements"""
    print("🔍 Checking PyTorch version...")
    try:
        import torch
        version = torch.__version__
        print(f"   PyTorch version: {version}")
        
        # Parse version for comparison (handle CUDA suffixes)
        version_parts = version.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])
        patch_part = version_parts[2].split('+')[0]  # Remove CUDA suffix
        patch = int(patch_part)
        
        if major < 2 or (major == 2 and minor < 4):
            print("❌ PyTorch >= 2.4.0 required")
            print("   Please upgrade PyTorch: pip install torch>=2.4.0")
            return False
        
        print("✅ PyTorch version OK")
        return True
        
    except ImportError:
        print("❌ PyTorch not installed")
        print("   Please install PyTorch: pip install torch>=2.4.0")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing Wan2.2 dependencies...")
    
    # Required packages based on webpage
    packages = [
        "torch>=2.4.0",
        "torchvision>=0.15.0",
        "diffusers>=0.21.0",
        "transformers>=4.30.0",
        "accelerate>=0.20.0",
        "opencv-python>=4.8.0",
        "pillow>=9.5.0",
        "numpy>=1.24.0",
        "huggingface_hub[cli]>=0.20.0"
    ]
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True, text=True)
            print(f"   ✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    return True

def create_models_directory():
    """Create models directory structure"""
    print("📁 Creating models directory structure...")
    
    # Create models/wan2_2 directory
    models_dir = Path("models/wan2_2")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"   ✅ Created: {models_dir.absolute()}")
    return models_dir

def download_wan2_2_model():
    """Download Wan2.2-TI2V-5B model using huggingface-cli"""
    print("📥 Downloading Wan2.2-TI2V-5B model...")
    
    models_dir = Path("models/wan2_2")
    
    try:
        # Download using huggingface-cli
        cmd = [
            "huggingface-cli", "download",
            "Wan-AI/Wan2.2-TI2V-5B",
            "--local-dir", str(models_dir),
            "--local-dir-use-symlinks", "False"
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Model downloaded successfully")
            return True
        else:
            print(f"❌ Download failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ huggingface-cli not found")
        print("   Please install: pip install huggingface_hub[cli]")
        return False
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

def verify_model_files():
    """Verify that model files were downloaded correctly"""
    print("🔍 Verifying model files...")
    
    models_dir = Path("models/wan2_2")
    expected_files = [
        "config.json",
        "model_index.json",
        "scheduler/scheduler_config.json",
        "text_encoder/config.json",
        "tokenizer/tokenizer_config.json",
        "unet/config.json",
        "vae/config.json"
    ]
    
    missing_files = []
    for file_path in expected_files:
        full_path = models_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All model files verified")
    return True

def test_model_loading():
    """Test if the model can be loaded"""
    print("🧪 Testing model loading...")
    
    try:
        import torch
        from diffusers import DiffusionPipeline
        
        # Try to load the model
        model_path = "models/wan2_2"
        pipeline = DiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
            low_cpu_mem_usage=True
        )
        
        print("✅ Model loaded successfully")
        del pipeline
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def create_test_script():
    """Create a test script for Wan2.2"""
    print("📝 Creating test script...")
    
    test_script = '''#!/usr/bin/env python3
"""
Wan2.2 Quick Test
Test the installed Wan2.2 model
"""

import torch
from diffusers import DiffusionPipeline
from diffusers.utils import export_to_video

def test_wan2_2():
    print("🧪 Testing Wan2.2 model...")
    
    try:
        # Load model
        pipeline = DiffusionPipeline.from_pretrained(
            "models/wan2_2",
            torch_dtype=torch.float16,
            use_safetensors=True,
            low_cpu_mem_usage=True
        )
        
        # Move to GPU
        pipeline = pipeline.to("cuda")
        
        # Test generation
        prompt = "A cozy room with warm lighting"
        
        video = pipeline(
            prompt=prompt,
            num_frames=12,  # 0.5 seconds at 24fps
            num_inference_steps=10,  # Quick test
            height=720,
            width=1280,
            fps=24
        ).frames[0]
        
        # Save test video
        export_to_video(video, "test_wan2_2_quick.mp4", fps=24)
        
        print("✅ Wan2.2 test successful!")
        print("   Output: test_wan2_2_quick.mp4")
        
        del pipeline
        return True
        
    except Exception as e:
        print(f"❌ Wan2.2 test failed: {e}")
        return False

if __name__ == "__main__":
    test_wan2_2()
'''
    
    with open("test_wan2_2_quick.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created: test_wan2_2_quick.py")

def main():
    """Main installation process"""
    print("🚀 WAN2.2-TI2V-5B INSTALLATION")
    print("=" * 50)
    print("Based on: https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B")
    print("Target: models/wan2_2 directory")
    print("=" * 50)
    
    # Step 1: Check requirements
    print("\n1️⃣ Checking requirements...")
    if not check_python_version():
        return False
    
    if not check_torch_version():
        return False
    
    # Step 2: Install dependencies
    print("\n2️⃣ Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Step 3: Create models directory
    print("\n3️⃣ Creating models directory...")
    models_dir = create_models_directory()
    
    # Step 4: Download model
    print("\n4️⃣ Downloading Wan2.2 model...")
    if not download_wan2_2_model():
        print("❌ Failed to download model")
        return False
    
    # Step 5: Verify files
    print("\n5️⃣ Verifying model files...")
    if not verify_model_files():
        print("❌ Model files verification failed")
        return False
    
    # Step 6: Test model loading
    print("\n6️⃣ Testing model loading...")
    if not test_model_loading():
        print("❌ Model loading test failed")
        return False
    
    # Step 7: Create test script
    print("\n7️⃣ Creating test script...")
    create_test_script()
    
    # Success
    print("\n🎉 WAN2.2 INSTALLATION COMPLETE!")
    print("=" * 50)
    print("✅ Model installed to: models/wan2_2")
    print("✅ Test script created: test_wan2_2_quick.py")
    print("✅ Ready for parallel pipeline testing")
    print("\n💡 Next steps:")
    print("   1. Run: python test_wan2_2_quick.py")
    print("   2. Test with parallel pipeline")
    print("   3. Compare performance vs SVD")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Installation failed")
        sys.exit(1) 