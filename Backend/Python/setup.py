#!/usr/bin/env python3
"""
Dreams.ai Setup Script
Automates the installation and setup process for the Dreams.ai project.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_cuda_availability():
    """Check if CUDA is available on the system."""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠️  CUDA not available - will use CPU-only llama-cpp-python")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed - CUDA check skipped")
        return False

def install_requirements(cuda_available: bool):
    """Install Python requirements with appropriate CUDA support."""
    print("\n📦 Installing Python requirements...")
    
    # Install base requirements first
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Install llama-cpp-python with CUDA support if available
    if cuda_available:
        print("🔧 Installing llama-cpp-python with CUDA support...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "llama-cpp-python",
                "--force-reinstall", "--no-cache-dir",
                "--extra-index-url", "https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cu118"
            ], check=True)
            print("✅ llama-cpp-python with CUDA support installed")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to install CUDA version, falling back to CPU version")
            subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python", "--force-reinstall"], check=True)
    else:
        print("🔧 Installing llama-cpp-python (CPU version)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python", "--force-reinstall"], check=True)

def setup_models():
    """Set up AI models using the model manager."""
    print("\n🤖 Setting up AI models...")
    
    try:
        from core.model_manager import setup_mistral_model
        
        print("📥 Checking for Mistral model...")
        model_path = setup_mistral_model(auto_download=False)
        
        if model_path:
            print(f"✅ Mistral model found at: {model_path}")
        else:
            print("📥 Mistral model not found. Would you like to download it now? (13.5GB)")
            response = input("Download model? (y/N): ").lower().strip()
            
            if response in ['y', 'yes']:
                print("📥 Downloading Mistral model...")
                model_path = setup_mistral_model(auto_download=True)
                if model_path:
                    print(f"✅ Mistral model downloaded successfully!")
                else:
                    print("❌ Failed to download model")
            else:
                print("⚠️  Model not downloaded. You can download it later using:")
                print("   python -c \"from core.model_manager import setup_mistral_model; setup_mistral_model()\"")
    
    except ImportError as e:
        print(f"❌ Failed to import model manager: {e}")
        print("Make sure all requirements are installed first.")

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "models",
        "generated_images",
        "cache",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_installation():
    """Test the installation by running basic imports."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test basic imports
        import langchain
        import langgraph
        import fastapi
        import flask
        print("✅ Core dependencies imported successfully")
        
        # Test llama-cpp-python
        try:
            from llama_cpp import Llama
            print("✅ llama-cpp-python imported successfully")
        except ImportError:
            print("⚠️  llama-cpp-python not available")
        
        # Test model manager
        try:
            from core.model_manager import ModelManager
            print("✅ Model manager imported successfully")
        except ImportError as e:
            print(f"⚠️  Model manager import failed: {e}")
        
        print("✅ Installation test completed")
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True

def main():
    """Main setup function."""
    print("🚀 Dreams.ai Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check CUDA availability
    cuda_available = check_cuda_availability()
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements(cuda_available)
    
    # Set up models
    setup_models()
    
    # Test installation
    if test_installation():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the API server: python api_server.py")
        print("2. Start the GUI test: python test_gui.py")
        print("3. Download models if needed: python -c \"from core.model_manager import setup_mistral_model; setup_mistral_model()\"")
    else:
        print("\n❌ Setup completed with errors. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 