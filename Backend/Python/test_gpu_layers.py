"""
Test GPU Layer Configuration
Quick test to verify that GPU layers are being allocated correctly.
"""

import torch
from core.model_manager import ModelManager

def test_gpu_layers():
    """Test GPU layer configuration"""
    print("🧪 Testing GPU Layer Configuration")
    print("=" * 50)
    
    # Check CUDA availability
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Name: {torch.cuda.get_device_name()}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    
    # Get ModelManager instance
    model_manager = ModelManager.get_instance()
    
    # Get GPU configuration
    gpu_config = model_manager.get_gpu_config()
    print(f"\nGPU Configuration: {gpu_config}")
    
    # Test model loading with GPU layers
    print("\n🔄 Testing model loading with GPU layers...")
    try:
        model_manager.preload_for_pipeline()
        print("✅ Models loaded successfully with GPU layers")
        
        # Get status to see GPU layer allocation
        status = model_manager.get_status()
        print(f"\nModel Status: {status}")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gpu_layers()

