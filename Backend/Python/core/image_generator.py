"""
Image Generation Module for Dreams.ai
Supports multiple image generation services and provides a unified interface.
"""

import os
import requests
import base64
from PIL import Image
import io
from typing import Optional, Dict, Any
import json
from datetime import datetime

class ImageGenerator:
    """Base class for image generation services"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.service_name = "base"
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Generate an image from a prompt.
        
        Args:
            prompt: The image generation prompt
            **kwargs: Additional parameters
            
        Returns:
            Dict containing image data and metadata, or None if failed
        """
        raise NotImplementedError("Subclasses must implement generate_image")
    
    def save_image(self, image_data: bytes, filename: str, directory: str = "generated_images") -> str:
        """
        Save generated image to disk.
        
        Args:
            image_data: Raw image bytes
            filename: Name for the saved file
            directory: Directory to save in
            
        Returns:
            Path to saved image
        """
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filepath

class PlaceholderImageGenerator(ImageGenerator):
    """Placeholder image generator for testing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.service_name = "placeholder"
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Generate a placeholder image for testing.
        
        Args:
            prompt: The image generation prompt (used for metadata)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing placeholder image data and metadata
        """
        try:
            # Create a simple placeholder image
            width = kwargs.get('width', 512)
            height = kwargs.get('height', 512)
            
            # Create a gradient image as placeholder
            image = Image.new('RGB', (width, height), color='#4F46E5')
            
            # Add some text to indicate it's a placeholder
            from PIL import ImageDraw, ImageFont
            
            draw = ImageDraw.Draw(image)
            
            # Try to use a default font, fallback to basic if not available
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Add placeholder text
            text = f"Placeholder for:\n{prompt[:50]}..."
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw text with outline for visibility
            draw.text((x, y), text, fill='white', font=font)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"placeholder_{timestamp}.png"
            
            # Save image
            filepath = self.save_image(img_byte_arr, filename)
            
            return {
                'image_data': base64.b64encode(img_byte_arr).decode('utf-8'),
                'filepath': filepath,
                'filename': filename,
                'prompt': prompt,
                'service': self.service_name,
                'metadata': {
                    'width': width,
                    'height': height,
                    'format': 'PNG',
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"Error generating placeholder image: {e}")
            return None

class StableDiffusionGenerator(ImageGenerator):
    """Stable Diffusion image generator (placeholder for future implementation)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.service_name = "stable_diffusion"
        self.api_url = config.get('api_url', 'http://localhost:7860')
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Generate image using Stable Diffusion API.
        
        Args:
            prompt: The image generation prompt
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generated image data and metadata
        """
        # Placeholder implementation - can be expanded with actual SD API calls
        print(f"Stable Diffusion generation requested for: {prompt}")
        print("This is a placeholder implementation")
        
        # For now, use placeholder generator
        placeholder = PlaceholderImageGenerator()
        result = placeholder.generate_image(prompt, **kwargs)
        
        if result:
            result['service'] = self.service_name
            result['metadata']['original_service'] = 'stable_diffusion'
        
        return result

class DALLEGenerator(ImageGenerator):
    """DALL-E image generator (placeholder for future implementation)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.service_name = "dalle"
        self.api_key = config.get('api_key')
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Generate image using DALL-E API.
        
        Args:
            prompt: The image generation prompt
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generated image data and metadata
        """
        # Placeholder implementation - can be expanded with actual DALL-E API calls
        print(f"DALL-E generation requested for: {prompt}")
        print("This is a placeholder implementation")
        
        # For now, use placeholder generator
        placeholder = PlaceholderImageGenerator()
        result = placeholder.generate_image(prompt, **kwargs)
        
        if result:
            result['service'] = self.service_name
            result['metadata']['original_service'] = 'dalle'
        
        return result

class ImageGenerationManager:
    """Manages multiple image generation services"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.generators = {}
        self.default_generator = None
        
        # Initialize generators
        self._setup_generators()
    
    def _setup_generators(self):
        """Setup available image generators"""
        # Always include placeholder generator
        self.generators['placeholder'] = PlaceholderImageGenerator()
        self.default_generator = self.generators['placeholder']
        
        # Add other generators if configured
        if self.config.get('stable_diffusion'):
            self.generators['stable_diffusion'] = StableDiffusionGenerator(
                self.config['stable_diffusion']
            )
        
        if self.config.get('dalle'):
            self.generators['dalle'] = DALLEGenerator(
                self.config['dalle']
            )
    
    def generate_image(self, prompt: str, service: str = None, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Generate an image using the specified service.
        
        Args:
            prompt: The image generation prompt
            service: Service to use (if None, uses default)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing image data and metadata, or None if failed
        """
        if service and service in self.generators:
            generator = self.generators[service]
        else:
            generator = self.default_generator
        
        return generator.generate_image(prompt, **kwargs)
    
    def get_available_services(self) -> list:
        """Get list of available image generation services"""
        return list(self.generators.keys())
    
    def get_service_info(self, service: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific service"""
        if service in self.generators:
            return {
                'name': service,
                'generator': self.generators[service].service_name,
                'config': self.config.get(service, {})
            }
        return None

# Global image generation manager instance
image_manager = ImageGenerationManager()

def generate_dream_image(prompt: str, service: str = None, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Convenience function to generate an image for a dream.
    
    Args:
        prompt: The image generation prompt
        service: Service to use (if None, uses default)
        **kwargs: Additional parameters
        
    Returns:
        Dict containing image data and metadata, or None if failed
    """
    return image_manager.generate_image(prompt, service, **kwargs) 