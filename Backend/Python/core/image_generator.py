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
import torch
from diffusers import DiffusionPipeline
import re

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

class SDXLTurboGenerator(ImageGenerator):
    """SDXL Turbo image generator for ultra-fast generation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.service_name = "sdxl_turbo"
        self.pipeline = None
        self.is_loaded = False
        self._setup_pipeline()
    
    def _setup_pipeline(self):
        """Initialize SDXL Turbo pipeline"""
        try:
            print("[SDXL Turbo] 🚀 Initializing SDXL Turbo pipeline...")
            
            # Load SDXL Turbo pipeline
            self.pipeline = DiffusionPipeline.from_pretrained(
                "stabilityai/sdxl-turbo",
                torch_dtype=torch.float16,
                variant="fp16"
            )
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.pipeline = self.pipeline.to("cuda")
                print(f"[SDXL Turbo] ✅ Pipeline loaded on GPU: {torch.cuda.get_device_name()}")
            else:
                print("[SDXL Turbo] ⚠️ CUDA not available, using CPU")
            
            self.is_loaded = True
            print("[SDXL Turbo] ✅ SDXL Turbo pipeline initialized successfully")
            
        except Exception as e:
            print(f"[SDXL Turbo] ❌ Failed to initialize SDXL Turbo pipeline: {e}")
            self.is_loaded = False
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Generate image using SDXL Turbo for ultra-fast generation"""
        if not self.is_loaded:
            print(f"[SDXL Turbo] Pipeline not loaded, falling back to placeholder")
            placeholder = PlaceholderImageGenerator()
            result = placeholder.generate_image(prompt, **kwargs)
            if result:
                result['service'] = 'sdxl_turbo_fallback'
                result['metadata']['original_service'] = 'sdxl_turbo'
            return result
        
        try:
            # Enhanced prompt engineering for Dreams.ai
            director_vision = kwargs.get('director_vision')
            enhanced_prompt = self._create_enhanced_prompt(prompt, director_vision)
            
            print(f"[SDXL Turbo] 🎨 Generating image with prompt: {enhanced_prompt[:100]}...")
            
            # SDXL Turbo optimized settings
            width = kwargs.get('width', 512)  # Default to 512 for speed optimization
            height = kwargs.get('height', 512)
            num_inference_steps = kwargs.get('num_inference_steps', 1)  # 1-4 steps
            guidance_scale = kwargs.get('guidance_scale', 0.0)  # Turbo uses 0.0
            
            start_time = datetime.now()
            
            with torch.no_grad():
                result = self.pipeline(
                    enhanced_prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=torch.Generator("cpu").manual_seed(kwargs.get('seed', 0))
                )
            
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # Extract the generated image
            image = result.images[0]
            
            # Convert PIL image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sdxl_turbo_{timestamp}.png"
            
            # Save image
            filepath = self.save_image(img_byte_arr, filename)
            
            return {
                'image_data': base64.b64encode(img_byte_arr).decode('utf-8'),
                'filepath': filepath,
                'filename': filename,
                'prompt': enhanced_prompt,
                'service': self.service_name,
                'metadata': {
                    'width': width,
                    'height': height,
                    'format': 'PNG',
                    'generated_at': end_time.isoformat(),
                    'generation_time': generation_time,
                    'model': 'SDXL Turbo',
                    'guidance_scale': guidance_scale,
                    'num_inference_steps': num_inference_steps,
                    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
                }
            }
            
        except Exception as e:
            print(f"[SDXL Turbo] ❌ Error during image generation: {e}")
            placeholder = PlaceholderImageGenerator()
            result = placeholder.generate_image(prompt, **kwargs)
            if result:
                result['service'] = 'sdxl_turbo_error'
                result['metadata']['sdxl_turbo_error'] = str(e)
            return result
    
    def _optimize_prompt_for_clip(self, prompt: str, max_tokens: int = 75) -> str:
        """
        Optimize prompt to stay within CLIP's token limit.
        Preserves key content while reducing length.
        """
        # Simple tokenization approximation (CLIP uses roughly 1.3 chars per token)
        # Use a conservative estimate to stay well under the limit
        max_chars = max_tokens * 4  # Conservative estimate: ~4 chars per token
        
        if len(prompt) <= max_chars:
            return prompt
        
        print(f"[SDXL Turbo] 📏 Prompt too long ({len(prompt)} chars), optimizing for CLIP...")
        
        # Strategy: Extract most important elements and reconstruct concisely
        # Priority order: subject, action, setting, style
        
        # Remove structured formatting markers that Cenedril adds
        clean_prompt = prompt
        
        # Remove section headers and formatting
        clean_prompt = re.sub(r'\*\*[^*]+\*\*:?\s*', '', clean_prompt)
        clean_prompt = re.sub(r'Here\'s the structured prompt with all sections filled out:\s*', '', clean_prompt)
        clean_prompt = re.sub(r'\[.*?\]', '', clean_prompt)  # Remove bracketed instructions
        
        # Extract key phrases (look for important descriptive content)
        # Remove redundant technical terms
        redundant_terms = [
            'professional photography', 'photorealistic', 'DSLR camera', 
            'natural lighting', 'realistic textures', 'sharp focus', 
            'high resolution', 'masterpiece', 'best quality', 'ultra detailed',
            'high detail', 'atmospheric lighting', 'cinematic composition'
        ]
        
        for term in redundant_terms:
            clean_prompt = clean_prompt.replace(term, '')
        
        # Clean up extra whitespace and punctuation
        clean_prompt = re.sub(r'\s+', ' ', clean_prompt)
        clean_prompt = re.sub(r'[,\s]*[,\s]+', ', ', clean_prompt)
        clean_prompt = clean_prompt.strip(' ,.')
        
        # If still too long, truncate to essential content
        if len(clean_prompt) > max_chars:
            # Split into sentences and keep the most important ones
            sentences = [s.strip() for s in clean_prompt.split('.') if s.strip()]
            
            # Prioritize sentences with character perspective ("Through my eyes", "I see")
            prioritized = []
            regular = []
            
            for sentence in sentences:
                if any(phrase in sentence.lower() for phrase in ['through my eyes', 'i see', 'through the eyes']):
                    prioritized.append(sentence)
                else:
                    regular.append(sentence)
            
            # Reconstruct with priority content first
            result_sentences = prioritized + regular
            
            # Add sentences until we approach the limit
            optimized_prompt = ""
            for sentence in result_sentences:
                test_prompt = optimized_prompt + sentence + ". " if optimized_prompt else sentence + ". "
                if len(test_prompt) <= max_chars:
                    optimized_prompt = test_prompt
                else:
                    break
            
            clean_prompt = optimized_prompt.strip(' .')
        
        # Add essential style markers back if there's room
        essential_style = "first-person perspective, photorealistic"
        if len(clean_prompt) + len(essential_style) + 2 <= max_chars:
            clean_prompt = f"{clean_prompt}, {essential_style}"
        
        print(f"[SDXL Turbo] ✂️ Optimized prompt: {len(clean_prompt)} chars")
        return clean_prompt
    
    def _create_enhanced_prompt(self, base_prompt: str, director_vision: dict = None) -> str:
        """Create enhanced prompt optimized for Dreams.ai and CLIP token limits"""
        
        # First, optimize the base prompt for CLIP if it's too long
        optimized_base = self._optimize_prompt_for_clip(base_prompt)
        
        # Only add minimal style elements to stay within CLIP limits
        essential_style = ["first-person perspective", "photorealistic"]
        
        if director_vision:
            visual_notes = director_vision.get("visual_notes", "")
            # Only add visual notes if they're short and we have room
            if visual_notes and len(visual_notes) < 50:
                essential_style.append(visual_notes[:30])  # Truncate visual notes
        
        style_text = ", ".join(essential_style)
        
        # Ensure final prompt stays within limits
        test_prompt = f"{optimized_base}, {style_text}"
        final_prompt = self._optimize_prompt_for_clip(test_prompt)
        
        return final_prompt





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
        # Add SDXL Turbo as the only generator
        self.generators['sdxl_turbo'] = SDXLTurboGenerator(self.config.get('sdxl_turbo', {}))
        
        # Set SDXL Turbo as default
        self.default_generator = self.generators['sdxl_turbo']
        
        # Add placeholder generator as fallback
        self.generators['placeholder'] = PlaceholderImageGenerator()
        
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