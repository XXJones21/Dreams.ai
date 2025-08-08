"""
Dreams.ai Video Generation Module

Handles video generation using LTX models, optimized for mobile content
and RTX 4080 16GB setup targeting real-time generation speeds.
"""

import os
import time
import torch
import gc
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from diffusers import LTXImageToVideoPipeline, LTXConditionPipeline
from diffusers.utils import export_to_video, load_image
from PIL import Image
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LTXVideoGenerator:
    """
    LTX Video Generator optimized for RTX 4080 16GB and mobile content.
    
    Targets 10-second video generation in 15 seconds for mobile screens.
    """
    
    def __init__(self, model_id: str = "Lightricks/LTX-Video", cache_dir: str = "models/ltx_video"):
        """
        Initialize the LTX Video Generator.
        
        Args:
            model_id: HuggingFace model identifier for LTX-Video
            cache_dir: Local cache directory for models on D: drive
        """
        self.model_id = model_id
        self.cache_dir = cache_dir
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.mobile_optimized = True
        
        # Working configuration tested on RTX 4080 16GB
        self.mobile_config = {
            "width": 512,       # Tested working size for memory efficiency
            "height": 512,      # Square format reduces memory usage
            "num_frames": 49,   # ~2 seconds at 24fps (divisible by 8 + 1)
            "num_inference_steps": 50,  # Standard for base model
            "guidance_scale": 7.5,      # Standard guidance for base model
            "fps": 25
        }
        
        # Performance targets
        self.target_realtime_ratio = 1.5  # Generate faster than playback
        
        logger.info(f"Initialized LTX Video Generator for {self.device}")
    
    def load_model(self) -> bool:
        """
        Load the LTX video generation model.
        
        Returns:
            bool: True if model loaded successfully
        """
        try:
            logger.info(f"Loading LTX model: {self.model_id}")
            
            # Clear CUDA cache before loading
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Load with optimizations for RTX 4080 using tested configuration
            self.pipeline = LTXImageToVideoPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.bfloat16,  # Tested working precision
                cache_dir=self.cache_dir,    # Use D: drive cache directory
                use_safetensors=True
            )
            
            # Move to GPU and enable memory optimizations
            self.pipeline.to(self.device)
            
            if hasattr(self.pipeline, 'enable_model_cpu_offload'):
                self.pipeline.enable_model_cpu_offload()
                logger.info("Enabled CPU offloading for memory optimization")
            
            logger.info("LTX model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load LTX model: {e}")
            return False
    
    def unload_model(self):
        """Unload model and free GPU memory"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            torch.cuda.empty_cache()
            gc.collect()
            logger.info("LTX model unloaded and memory freed")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current GPU memory usage"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            return {
                "allocated_gb": allocated,
                "reserved_gb": reserved,
                "free_gb": 16.0 - reserved  # Assuming RTX 4080 16GB
            }
        return {"allocated_gb": 0, "reserved_gb": 0, "free_gb": 0}
    
    def optimize_prompt_for_video(self, image_prompt: str, story_context: str) -> str:
        """
        Optimize Cenedril's image prompt for video generation.
        
        Args:
            image_prompt: Original image generation prompt from Cenedril
            story_context: Story context from Narnion
            
        Returns:
            str: Optimized video prompt
        """
        # Extract key visual elements from the image prompt
        base_prompt = image_prompt
        
        # Add temporal and motion elements for video
        video_enhancements = [
            "The camera maintains a steady first-person perspective.",
            "Subtle ambient motion with gentle lighting changes.",
            "Natural environmental movement and atmosphere.",
            "Smooth, cinematic video quality with consistent framing."
        ]
        
        # Combine with story context for coherent motion
        video_prompt = f"{base_prompt} {' '.join(video_enhancements)}"
        
        # Add story context for narrative coherence
        if story_context:
            video_prompt += f" Scene context: {story_context[:100]}"
        
        # Ensure first-person perspective
        if "pov" not in video_prompt.lower() and "first-person" not in video_prompt.lower():
            video_prompt = f"First-person POV: {video_prompt}"
        
        return video_prompt
    
    def generate_video_from_image(
        self, 
        image_path: str, 
        video_prompt: str,
        output_path: str,
        config_override: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, float, str]:
        """
        Generate video from image using optimized settings.
        
        Args:
            image_path: Path to input image
            video_prompt: Text prompt for video generation
            output_path: Path to save output video
            config_override: Optional config overrides
            
        Returns:
            Tuple of (success, generation_time, output_path)
        """
        if self.pipeline is None:
            logger.error("Model not loaded. Call load_model() first.")
            return False, 0.0, ""
        
        try:
            # Use mobile config with any overrides
            config = self.mobile_config.copy()
            if config_override:
                config.update(config_override)
            
            # Load and prepare image
            image = load_image(image_path)
            
            logger.info(f"Generating video: {config['width']}x{config['height']}, {config['num_frames']} frames")
            logger.info(f"Video prompt: {video_prompt[:100]}...")
            
            # Start timing
            start_time = time.time()
            
            # Generate video with optimized settings
            negative_prompt = "worst quality, inconsistent motion, blurry, jittery, distorted, third person"
            
            video_output = self.pipeline(
                image=image,
                prompt=video_prompt,
                negative_prompt=negative_prompt,
                generator=torch.Generator(device=self.device).manual_seed(42),
                width=config["width"],
                height=config["height"],
                num_frames=config["num_frames"],
                num_inference_steps=config["num_inference_steps"],
                guidance_scale=config["guidance_scale"],
                decode_timestep=config["decode_timestep"],
                decode_noise_scale=config["decode_noise_scale"]
            )
            
            generation_time = time.time() - start_time
            
            # Save video
            export_to_video(video_output.frames[0], output_path, fps=config["fps"])
            
            # Calculate performance metrics
            video_duration = config["num_frames"] / config["fps"]
            speed_ratio = generation_time / video_duration
            
            logger.info(f"Video generation complete: {output_path}")
            logger.info(f"Generation time: {generation_time:.2f}s for {video_duration:.2f}s video")
            logger.info(f"Speed ratio: {speed_ratio:.2f}x (target: <{self.target_realtime_ratio}x)")
            
            # Performance assessment
            if speed_ratio <= self.target_realtime_ratio:
                logger.info("🎉 EXCELLENT: Achieved real-time generation target!")
            elif speed_ratio <= 3.0:
                logger.info("✅ GOOD: Near real-time performance")
            else:
                logger.warning("⚠️ SLOW: Consider optimizing settings")
            
            return True, generation_time, output_path
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return False, 0.0, ""
    
    def generate_video_for_cenedril(
        self, 
        image_path: str, 
        cenedril_prompt: str,
        story_context: str,
        dream_id: str,
        output_dir: str = "generated_videos"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Generate video specifically for Cenedril pipeline integration.
        
        Args:
            image_path: Path to Cenedril's generated image
            cenedril_prompt: Original prompt from Cenedril
            story_context: Scene context from Narnion
            dream_id: Unique dream identifier
            output_dir: Directory to save output
            
        Returns:
            Tuple of (success, video_path, metadata)
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate output filename
        video_filename = f"{dream_id}_cenedril_video.mp4"
        video_path = str(output_path / video_filename)
        
        # Optimize prompt for video generation
        video_prompt = self.optimize_prompt_for_video(cenedril_prompt, story_context)
        
        # Generate video
        success, gen_time, output_file = self.generate_video_from_image(
            image_path=image_path,
            video_prompt=video_prompt,
            output_path=video_path
        )
        
        # Prepare metadata
        metadata = {
            "dream_id": dream_id,
            "generation_time": gen_time,
            "video_duration": self.mobile_config["num_frames"] / self.mobile_config["fps"],
            "resolution": f"{self.mobile_config['width']}x{self.mobile_config['height']}",
            "fps": self.mobile_config["fps"],
            "frames": self.mobile_config["num_frames"],
            "model_used": self.model_id,
            "prompt_optimized": video_prompt,
            "memory_usage": self.get_memory_usage()
        }
        
        if success:
            logger.info(f"Cenedril video generated successfully: {video_path}")
        else:
            logger.error(f"Cenedril video generation failed for dream {dream_id}")
        
        return success, video_path if success else "", metadata

# Global instance for pipeline integration
_video_generator = None

def get_video_generator() -> LTXVideoGenerator:
    """Get or create global video generator instance"""
    global _video_generator
    if _video_generator is None:
        _video_generator = LTXVideoGenerator()
    return _video_generator

def initialize_video_generator() -> bool:
    """Initialize the global video generator"""
    generator = get_video_generator()
    return generator.load_model()

def cleanup_video_generator():
    """Cleanup the global video generator"""
    global _video_generator
    if _video_generator is not None:
        _video_generator.unload_model()
        _video_generator = None 