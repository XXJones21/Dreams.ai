#!/usr/bin/env python3
"""
LTX Model Benchmark Script

Compares performance between LTX-Video base model and LTX-Video-0.9.7-distilled
using identical Cenedril-style prompts and captures detailed metrics.
"""

import os
import sys
import time
import json
import torch
import psutil
import gc
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from diffusers import LTXImageToVideoPipeline, LTXConditionPipeline
from diffusers.utils import export_to_video, load_image
from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
from PIL import Image, ImageDraw

class LTXBenchmark:
    """Comprehensive benchmark tool for LTX video models"""
    
    def __init__(self, cache_dir: str = "models/ltx_video"):
        self.cache_dir = cache_dir
        self.results = {}
        self.log_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Test configuration for 10-second videos
        self.test_configs = {
            "base_model": {
                "model_id": "Lightricks/LTX-Video",
                "pipeline_class": LTXImageToVideoPipeline,
                "config": {
                    "width": 512,
                    "height": 512, 
                    "num_frames": 241,  # 10 seconds at 24fps (8*30+1 = 241)
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            },
            "distilled_model": {
                "model_id": "Lightricks/LTX-Video-0.9.7-distilled", 
                "pipeline_class": LTXConditionPipeline,
                "config": {
                    "width": 512,
                    "height": 512,
                    "num_frames": 241,  # 10 seconds at 24fps (8*30+1 = 241) 
                    "num_inference_steps": 7,
                    "guidance_scale": 1.0,
                    "decode_timestep": 0.05,
                    "decode_noise_scale": 0.025
                }
            }
        }
        
    def log(self, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def get_system_info(self) -> Dict[str, Any]:
        """Capture system information"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No CUDA",
            "total_vram_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3 if torch.cuda.is_available() else 0,
            "cpu_count": psutil.cpu_count(),
            "total_ram_gb": psutil.virtual_memory().total / 1024**3,
            "python_version": sys.version,
            "torch_version": torch.__version__
        }
        return info
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        memory = {
            "ram_used_gb": psutil.virtual_memory().used / 1024**3,
            "ram_percent": psutil.virtual_memory().percent
        }
        
        if torch.cuda.is_available():
            memory.update({
                "vram_allocated_gb": torch.cuda.memory_allocated(0) / 1024**3,
                "vram_reserved_gb": torch.cuda.memory_reserved(0) / 1024**3,
                "vram_percent": (torch.cuda.memory_allocated(0) / torch.cuda.get_device_properties(0).total_memory) * 100
            })
        
        return memory
        
    def create_test_image(self) -> str:
        """Create a test input image"""
        os.makedirs("benchmark_outputs", exist_ok=True)
        
        # Create a simple geometric test image
        img = Image.new('RGB', (512, 512), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Add some geometric shapes for motion testing
        draw.rectangle([100, 100, 200, 200], fill='red', outline='darkred', width=3)
        draw.ellipse([300, 150, 400, 250], fill='green', outline='darkgreen', width=3)
        draw.polygon([(250, 300), (300, 400), (200, 400)], fill='blue', outline='darkblue', width=3)
        
        try:
            draw.text((50, 450), "LTX Benchmark Test", fill='black')
        except:
            pass  # Handle missing font gracefully
            
        image_path = "benchmark_outputs/test_input.png"
        img.save(image_path)
        self.log(f"Created test image: {image_path}")
        return image_path
        
    def load_model(self, model_name: str, config: Dict[str, Any]) -> Tuple[Optional[Any], Dict[str, Any]]:
        """Load and initialize a model with timing"""
        self.log(f"Loading {model_name}...")
        
        # Set PyTorch memory management environment variable for better memory handling
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
        
        # Aggressive memory clearing before loading
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        for _ in range(3):
            gc.collect()
        
        load_start = time.time()
        memory_before = self.get_memory_usage()
        self.log(f"📊 VRAM before loading: {memory_before.get('vram_allocated_gb', 0):.2f}GB")
        
        try:
            pipeline = config["pipeline_class"].from_pretrained(
                config["model_id"],
                torch_dtype=torch.bfloat16,
                cache_dir=self.cache_dir
            )
            
                         # Move to GPU and check memory before CPU offloading
            pipeline = pipeline.to("cuda")
            memory_gpu_only = self.get_memory_usage()
            self.log(f"📊 VRAM after GPU load: {memory_gpu_only.get('vram_allocated_gb', 0):.2f}GB")
            
            # Enable CPU offloading for memory optimization
            if hasattr(pipeline, 'enable_model_cpu_offload'):
                pipeline.enable_model_cpu_offload()
                self.log("🔄 CPU offloading enabled")
            
            load_time = time.time() - load_start
            memory_after = self.get_memory_usage()
            
            # Get more detailed memory info
            if torch.cuda.is_available():
                reserved_memory = torch.cuda.memory_reserved(0) / 1024**3
                allocated_memory = torch.cuda.memory_allocated(0) / 1024**3
                self.log(f"📊 Detailed VRAM - Allocated: {allocated_memory:.2f}GB, Reserved: {reserved_memory:.2f}GB")
            
            metrics = {
                "load_time_seconds": load_time,
                "memory_before": memory_before,
                "memory_gpu_only": memory_gpu_only,
                "memory_after": memory_after,
                "memory_increase_gb": memory_after.get("vram_allocated_gb", 0) - memory_before.get("vram_allocated_gb", 0),
                "model_components": list(pipeline.components.keys()) if hasattr(pipeline, 'components') else []
            }
            
            self.log(f"✅ {model_name} loaded in {load_time:.2f}s")
            self.log(f"📊 VRAM final: {memory_after.get('vram_allocated_gb', 0):.2f}GB allocated")
            
            return pipeline, metrics
            
        except Exception as e:
            self.log(f"❌ Failed to load {model_name}: {e}")
            return None, {"error": str(e), "load_time_seconds": time.time() - load_start}
            
    def generate_video(self, pipeline: Any, model_name: str, config: Dict[str, Any], 
                      prompt: str, image_path: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Generate video with detailed metrics"""
        self.log(f"Generating 10-second video with {model_name}...")
        
        generation_start = time.time()
        memory_before = self.get_memory_usage()
        
        try:
            # Load input image
            image = load_image(image_path)
            
            # Configure generation parameters
            gen_config = config["config"].copy()
            gen_config["prompt"] = prompt
            gen_config["negative_prompt"] = "worst quality, inconsistent motion, blurry, jittery, distorted"
            gen_config["generator"] = torch.Generator().manual_seed(42)  # Consistent seed
            
            # Generate based on model type
            if "distilled" in config["model_id"]:
                # Distilled model uses condition pipeline
                video_condition = export_to_video([image])
                from diffusers.utils import load_video
                video_cond = load_video(video_condition)
                condition1 = LTXVideoCondition(video=video_cond, frame_index=0)
                
                video = pipeline(
                    conditions=[condition1],
                    **gen_config
                ).frames[0]
            else:
                # Base model uses standard image-to-video
                video = pipeline(
                    image=image,
                    **gen_config
                ).frames[0]
                
            generation_time = time.time() - generation_start
            memory_after = self.get_memory_usage()
            
            # Save video
            output_path = f"benchmark_outputs/{model_name.replace('/', '_').replace('-', '_')}_10sec_video.mp4"
            export_to_video(video, output_path, fps=24)
            
            # Calculate metrics
            video_duration = gen_config["num_frames"] / 24  # 24fps
            speed_ratio = generation_time / video_duration
            
            metrics = {
                "generation_time_seconds": generation_time,
                "video_duration_seconds": video_duration,
                "speed_ratio": speed_ratio,
                "fps": 24,
                "resolution": f"{gen_config['width']}x{gen_config['height']}",
                "num_frames": gen_config["num_frames"],
                "inference_steps": gen_config["num_inference_steps"],
                "guidance_scale": gen_config["guidance_scale"],
                "memory_before": memory_before,
                "memory_after": memory_after,
                "memory_peak_gb": memory_after.get("vram_allocated_gb", 0),
                "output_path": output_path,
                "file_size_mb": os.path.getsize(output_path) / 1024**2 if os.path.exists(output_path) else 0
            }
            
            self.log(f"✅ Video generated in {generation_time:.2f}s")
            self.log(f"🎬 Speed ratio: {speed_ratio:.2f}x (lower is better)")
            self.log(f"📹 Output: {output_path}")
            
            return output_path, metrics
            
        except Exception as e:
            generation_time = time.time() - generation_start
            self.log(f"❌ Generation failed: {e}")
            return None, {
                "error": str(e),
                "generation_time_seconds": generation_time,
                "memory_before": memory_before,
                "memory_after": self.get_memory_usage()
            }
            
    def cleanup_model(self, pipeline: Any, model_name: str):
        """Clean up model and free GPU memory aggressively"""
        if pipeline is not None:
            # First move pipeline to CPU to free GPU memory
            try:
                pipeline.to("cpu")
            except:
                pass
            
            # Delete the pipeline
            del pipeline
            
            # Aggressive GPU memory cleanup
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()  # Additional cleanup
                
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
            
            # Check memory after cleanup
            memory_after = self.get_memory_usage()
            self.log(f"🧹 Cleaned up {model_name}")
            self.log(f"📊 VRAM after cleanup: {memory_after.get('vram_allocated_gb', 0):.2f}GB allocated")
            
            # Wait a moment for cleanup to complete
            import time
            time.sleep(2)
            
    def run_benchmark(self, prompt: str):
        """Run complete benchmark comparing both models"""
        self.log("🚀 Starting LTX Model Benchmark")
        self.log("=" * 60)
        
        # System info
        system_info = self.get_system_info()
        self.log(f"GPU: {system_info['gpu_name']}")
        self.log(f"VRAM: {system_info['total_vram_gb']:.1f}GB")
        self.log(f"Prompt: {prompt}")
        
        # Create test image
        image_path = self.create_test_image()
        
        # Initialize results
        self.results = {
            "system_info": system_info,
            "test_prompt": prompt,
            "test_image": image_path,
            "models": {}
        }
        
        # Test each model
        for model_key, model_config in self.test_configs.items():
            self.log(f"\n{'='*20} Testing {model_key} {'='*20}")
            
            # Load model
            pipeline, load_metrics = self.load_model(model_key, model_config)
            
            if pipeline is None:
                self.results["models"][model_key] = {"load_metrics": load_metrics, "status": "failed_to_load"}
                continue
                
            # Generate video
            video_path, gen_metrics = self.generate_video(pipeline, model_key, model_config, prompt, image_path)
            
            # Store results
            self.results["models"][model_key] = {
                "model_id": model_config["model_id"],
                "load_metrics": load_metrics,
                "generation_metrics": gen_metrics,
                "status": "success" if video_path else "failed_to_generate"
            }
            
            # Cleanup
            self.cleanup_model(pipeline, model_key)
            
        # Save results
        self.save_results()
        self.print_summary()
        
    def save_results(self):
        """Save benchmark results to JSON file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        self.log(f"📄 Results saved to: {self.log_file}")
        
    def print_summary(self):
        """Print benchmark summary"""
        self.log("\n" + "="*60)
        self.log("🏁 BENCHMARK SUMMARY")
        self.log("="*60)
        
        for model_key, results in self.results["models"].items():
            if results["status"] == "success":
                gen_metrics = results["generation_metrics"]
                load_metrics = results["load_metrics"]
                
                self.log(f"\n📊 {model_key.upper()}")
                self.log(f"   Model: {results['model_id']}")
                self.log(f"   Load Time: {load_metrics['load_time_seconds']:.2f}s")
                self.log(f"   Generation Time: {gen_metrics['generation_time_seconds']:.2f}s")
                self.log(f"   Speed Ratio: {gen_metrics['speed_ratio']:.2f}x")
                self.log(f"   Peak VRAM: {gen_metrics['memory_peak_gb']:.2f}GB")
                self.log(f"   File Size: {gen_metrics['file_size_mb']:.1f}MB")
                self.log(f"   Status: ✅ Success")
            else:
                self.log(f"\n📊 {model_key.upper()}")
                self.log(f"   Status: ❌ {results['status']}")
                
        self.log(f"\n📄 Detailed results: {self.log_file}")

def main():
    """Main benchmark execution"""
    # Cenedril-style first-person perspective prompt for testing
    test_prompt = """
    First-person POV of walking through a magical forest at golden hour. 
    The camera moves forward along a winding dirt path lined with ancient oak trees. 
    Glowing mushrooms pulse with soft blue light on either side of the path. 
    Particles of golden light drift through the air like fireflies. 
    The late afternoon sun filters through the canopy above, creating dramatic 
    rays of light that illuminate the misty forest floor. The perspective 
    maintains a steady walking pace, with slight natural camera movement 
    that captures the immersive first-person experience.
    """
    
    benchmark = LTXBenchmark()
    benchmark.run_benchmark(test_prompt)

if __name__ == "__main__":
    main() 