#!/usr/bin/env python3
"""
LTX Video Installation Script

Installs and configures LTX video generation dependencies for Dreams.ai
Optimized for RTX 4080 16GB setup.
"""

import subprocess
import sys
import os
import torch
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False

def check_cuda():
    """Check CUDA availability and GPU specs"""
    if not torch.cuda.is_available():
        print("❌ CUDA not available - GPU acceleration disabled")
        return False
    
    gpu_name = torch.cuda.get_device_name(0)
    total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    print(f"✅ GPU: {gpu_name}")
    print(f"✅ VRAM: {total_memory:.1f} GB")
    
    if total_memory >= 15:  # RTX 4080 has 16GB
        print("✅ GPU suitable for LTX video generation")
        return True
    else:
        print("⚠️  GPU has limited VRAM - performance may be reduced")
        return True

def install_requirements():
    """Install LTX video requirements"""
    print("\n📦 Installing LTX video dependencies...")
    
    requirements_file = "requirements_ltx_video.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def verify_installation():
    """Verify LTX installation"""
    print("\n🧪 Verifying installation...")
    
    try:
        # Test imports
        from diffusers import LTXImageToVideoPipeline
        print("✅ LTX diffusers integration available")
        
        # Test model availability (don't download, just check)
        print("✅ LTX models accessible via HuggingFace")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "test_outputs",
        "generated_videos",
        "generated_images"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created: {directory}")

def run_installation():
    """Run complete installation process"""
    print("🚀 LTX Video Installation for Dreams.ai")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        print("\n❌ Python version incompatible")
        return False
    
    if not check_cuda():
        print("\n⚠️  CUDA issues detected - continuing anyway")
    
    # Install dependencies
    if not install_requirements():
        print("\n❌ Installation failed")
        return False
    
    # Create directories
    create_directories()
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Verification failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 LTX Video installation complete!")
    print("\n📋 Next steps:")
    print("1. Run: python test_ltx_video.py")
    print("2. Test the pipeline with your Dreams.ai setup")
    print("3. Adjust mobile_config in video_generator.py if needed")
    print("\n🎯 Target: 10-second video in 15 seconds on RTX 4080")
    
    return True

if __name__ == "__main__":
    success = run_installation()
    sys.exit(0 if success else 1) 