"""
Model Manager for Dreams.ai
Handles automatic downloading and setup of AI models for local inference.
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from tqdm import tqdm
from huggingface_hub import hf_hub_download
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages AI model downloading, caching, and setup for local inference.
    """
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize the model manager.
        
        Args:
            models_dir: Directory to store downloaded models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Model configurations
        self.model_configs = {
            "mistral-small-3.2-24b": {
                "repo_id": "unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF",
                "filename": "mistral-small-3.2-24b-instruct-2506.Q4_K_M.gguf",
                "size_gb": 13.5,
                "description": "Mistral Small 3.2 24B Instruct (Q4_K_M quantization)"
            }
        }
    
    def get_model_path(self, model_name: str) -> Optional[Path]:
        """
        Get the local path of a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Path to the model file, or None if not found
        """
        if model_name not in self.model_configs:
            logger.error(f"Unknown model: {model_name}")
            return None
        
        config = self.model_configs[model_name]
        model_path = self.models_dir / config["filename"]
        
        if model_path.exists():
            return model_path
        else:
            logger.info(f"Model {model_name} not found at {model_path}")
            return None
    
    def download_model(self, model_name: str, force: bool = False) -> Optional[Path]:
        """
        Download a model from Hugging Face Hub.
        
        Args:
            model_name: Name of the model to download
            force: Force re-download even if model exists
            
        Returns:
            Path to the downloaded model, or None if failed
        """
        if model_name not in self.model_configs:
            logger.error(f"Unknown model: {model_name}")
            return None
        
        config = self.model_configs[model_name]
        model_path = self.models_dir / config["filename"]
        
        # Check if model already exists
        if model_path.exists() and not force:
            logger.info(f"Model {model_name} already exists at {model_path}")
            return model_path
        
        # Check available disk space
        required_space = config["size_gb"] * 1024 * 1024 * 1024  # Convert to bytes
        available_space = self._get_available_space()
        
        if available_space < required_space:
            logger.error(f"Insufficient disk space. Required: {config['size_gb']:.1f}GB, Available: {available_space / (1024**3):.1f}GB")
            return None
        
        logger.info(f"Downloading {model_name} ({config['description']})...")
        logger.info(f"Size: {config['size_gb']:.1f}GB")
        logger.info(f"Destination: {model_path}")
        
        try:
            # Download from Hugging Face Hub
            downloaded_path = hf_hub_download(
                repo_id=config["repo_id"],
                filename=config["filename"],
                local_dir=self.models_dir,
                local_dir_use_symlinks=False
            )
            
            # Verify download
            if os.path.exists(downloaded_path):
                file_size = os.path.getsize(downloaded_path) / (1024**3)  # GB
                logger.info(f"Download completed successfully!")
                logger.info(f"File size: {file_size:.1f}GB")
                return Path(downloaded_path)
            else:
                logger.error("Download failed - file not found")
                return None
                
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return None
    
    def setup_model(self, model_name: str, auto_download: bool = True) -> Optional[Path]:
        """
        Set up a model for use, downloading if necessary.
        
        Args:
            model_name: Name of the model to set up
            auto_download: Automatically download if model not found
            
        Returns:
            Path to the model file, or None if setup failed
        """
        # Check if model exists locally
        model_path = self.get_model_path(model_name)
        
        if model_path is None and auto_download:
            logger.info(f"Model {model_name} not found locally, downloading...")
            model_path = self.download_model(model_name)
        
        if model_path is None:
            logger.error(f"Failed to set up model {model_name}")
            return None
        
        logger.info(f"Model {model_name} ready at {model_path}")
        return model_path
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available models and their status.
        
        Returns:
            Dictionary of model information
        """
        models_info = {}
        
        for model_name, config in self.model_configs.items():
            model_path = self.get_model_path(model_name)
            status = "downloaded" if model_path else "not_downloaded"
            
            models_info[model_name] = {
                "status": status,
                "path": str(model_path) if model_path else None,
                "size_gb": config["size_gb"],
                "description": config["description"]
            }
        
        return models_info
    
    def cleanup_models(self, model_names: list = None) -> bool:
        """
        Remove downloaded model files to free up space.
        
        Args:
            model_names: List of model names to remove, or None for all
            
        Returns:
            True if cleanup successful, False otherwise
        """
        if model_names is None:
            model_names = list(self.model_configs.keys())
        
        success = True
        
        for model_name in model_names:
            if model_name not in self.model_configs:
                logger.warning(f"Unknown model: {model_name}")
                continue
            
            config = self.model_configs[model_name]
            model_path = self.models_dir / config["filename"]
            
            if model_path.exists():
                try:
                    model_path.unlink()
                    logger.info(f"Removed model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to remove {model_name}: {str(e)}")
                    success = False
            else:
                logger.info(f"Model {model_name} not found, nothing to remove")
        
        return success
    
    def _get_available_space(self) -> int:
        """
        Get available disk space in bytes.
        
        Returns:
            Available space in bytes
        """
        try:
            stat = os.statvfs(self.models_dir)
            return stat.f_frsize * stat.f_bavail
        except Exception as e:
            logger.error(f"Failed to get disk space: {str(e)}")
            return 0
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary, or None if not found
        """
        if model_name not in self.model_configs:
            return None
        
        config = self.model_configs[model_name]
        model_path = self.get_model_path(model_name)
        
        info = {
            "name": model_name,
            "description": config["description"],
            "size_gb": config["size_gb"],
            "repo_id": config["repo_id"],
            "filename": config["filename"],
            "status": "downloaded" if model_path else "not_downloaded",
            "path": str(model_path) if model_path else None
        }
        
        if model_path and model_path.exists():
            file_size = model_path.stat().st_size / (1024**3)  # GB
            info["actual_size_gb"] = file_size
            info["download_date"] = model_path.stat().st_mtime
        
        return info


# Global model manager instance
model_manager = ModelManager()


def setup_mistral_model(auto_download: bool = True) -> Optional[Path]:
    """
    Convenience function to set up the Mistral model.
    
    Args:
        auto_download: Automatically download if model not found
        
    Returns:
        Path to the Mistral model, or None if setup failed
    """
    return model_manager.setup_model("mistral-small-3.2-24b", auto_download)


def get_model_path(model_name: str) -> Optional[Path]:
    """
    Convenience function to get model path.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Path to the model, or None if not found
    """
    return model_manager.get_model_path(model_name)


if __name__ == "__main__":
    # Test the model manager
    print("Dreams.ai Model Manager")
    print("=" * 50)
    
    # List available models
    models = model_manager.list_available_models()
    for name, info in models.items():
        print(f"\nModel: {name}")
        print(f"Status: {info['status']}")
        print(f"Size: {info['size_gb']:.1f}GB")
        print(f"Description: {info['description']}")
        if info['path']:
            print(f"Path: {info['path']}")
    
    # Test setup
    print("\n" + "=" * 50)
    print("Testing model setup...")
    
    model_path = setup_mistral_model(auto_download=False)
    if model_path:
        print(f"Mistral model ready at: {model_path}")
    else:
        print("Mistral model not found. Run with auto_download=True to download.") 