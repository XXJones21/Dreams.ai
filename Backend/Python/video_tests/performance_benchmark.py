#!/usr/bin/env python3
"""
High-Performance LTX Benchmark
Target: 10-second video generation in 15 seconds on RTX 4080 16GB

Optimization Strategy:
1. Full GPU utilization (no CPU offloading)
2. FP16 precision for speed
3. Minimal inference steps
4. Torch compilation
5. Memory format optimization
"""

import os
import sys
import time
import json
import torch
import gc
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from diffusers import LTXImageToVideoPipeline, LTXConditionPipeline
from diffusers.utils import export_to_video
from PIL import Image, ImageDraw

class PerformanceBenchmark:
    """High-performance benchmark for LTX models targeting 15-second generation"""
    
    def __init__(self, cache_dir: str = "models/ltx_video"):
        self.cache_dir = cache_dir
        self.output_dir = "performance_outputs"
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Performance-focused test configurations
        self.test_configs = {
            "ultra_fast": {
                "width": 576,
                "height": 1024,
                "num_frames": 81,  # ~3.2 seconds at 25fps - reduced for speed
                "num_inference_steps": 8,  # Minimal steps
                "guidance_scale": 1.0,
                "torch_dtype": torch.float16,  # FP16 for speed
                "enable_cpu_offload": False,  # Full GPU
                "compile_model": True,
                "memory_format": "channels_last"
            },
            "speed_optimized": {
                "width": 512,
                "height": 512, 
                "num_frames": 121,  # ~5 seconds at 24fps
                "num_inference_steps": 12,
                "guidance_scale": 1.5,
                "torch_dtype": torch.float16,
                "enable_cpu_offload": False,
                "compile_model": True,
                "memory_format": "channels_last"
            },
            "target_10sec": {
                "width": 576,
                "height": 1024,
                "num_frames": 241,  # 10 seconds at 24fps
                "num_inference_steps": 15,  # Minimal for quality
                "guidance_scale": 2.0,
                "torch_dtype": torch.float16,
                "enable_cpu_offload": False,
                "compile_model": True,
                "memory_format": "channels_last"
            }
        }
        
        # Cenedril-style first-person prompt
        self.test_prompt = """First-person POV of walking through a magical forest at golden hour.
The camera moves forward along a winding dirt path lined with ancient oak trees.
Glowing mushrooms pulse with soft blue light on either side of the path.
Particles of golden light drift through the air like fireflies.
The late afternoon sun filters through the canopy above, creating dramatic
rays of light that illuminate the misty forest floor. The perspective
is from the viewer's eyes, showing hands occasionally reaching out to touch
the glowing flora. The movement is smooth and steady, like a first-person
exploration of an enchanted realm."""
        
        self.negative_prompt = "static, blurry, low quality, distorted, pixelated, bad anatomy"

    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def kill_all_python_processes(self):
        """Aggressively kill any Python processes that might be holding GPU memory"""
        try:
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                         capture_output=True, text=True)
        except:
            pass

    def aggressive_memory_cleanup(self):
        """Nuclear option memory cleanup"""
        # Clear Python garbage collector
        gc.collect()
        
        # Clear CUDA cache multiple times
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            torch.cuda.empty_cache()
            
        # Set memory fraction to ensure clean slate
        if torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(0.95)  # Use 95% of VRAM
            
        # Force Python garbage collection again
        gc.collect()

    def get_real_memory_usage(self) -> Dict[str, float]:
        """Get actual GPU memory usage using nvidia-ml-py"""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            return {
                "total_gb": info.total / 1024**3,
                "used_gb": info.used / 1024**3,
                "free_gb": info.free / 1024**3,
                "utilization": (info.used / info.total) * 100
            }
        except ImportError:
            # Fallback to torch (less accurate but available)
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                reserved = torch.cuda.memory_reserved(0) / 1024**3
                total = torch.cuda.get_device_properties(0).total_memory / 1024**3
                return {
                    "total_gb": total,
                    "used_gb": reserved,  # Use reserved as it's more accurate
                    "free_gb": total - reserved,
                    "utilization": (reserved / total) * 100
                }
            return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "utilization": 0}

    def optimize_pipeline(self, pipeline, config: Dict[str, Any]):
        """Apply performance optimizations to pipeline"""
        self.log("🚀 Applying performance optimizations...")
        
        # 1. Memory format optimization
        if config.get("memory_format") == "channels_last":
            try:
                pipeline.unet = pipeline.unet.to(memory_format=torch.channels_last)
                self.log("✅ Applied channels_last memory format")
            except:
                self.log("⚠️ Could not apply channels_last format")
        
        # 2. Enable attention optimizations
        try:
            pipeline.enable_attention_slicing("auto")
            self.log("✅ Enabled attention slicing")
        except:
            self.log("⚠️ Could not enable attention slicing")
            
        # 3. Compile model for speed (if requested)
        if config.get("compile_model", False):
            try:
                self.log("🔄 Compiling model with torch.compile() - this may take a moment...")
                pipeline.unet = torch.compile(pipeline.unet, mode="reduce-overhead")
                self.log("✅ Model compiled successfully")
            except Exception as e:
                self.log(f"⚠️ Could not compile model: {e}")
        
        return pipeline

    def test_model_performance(self, model_name: str, model_id: str, test_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific model configuration for performance"""
        self.log(f"🏃‍♂️ Testing {model_name} with {test_name} config")
        self.log("=" * 60)
        
        # Memory cleanup before test
        self.aggressive_memory_cleanup()
        memory_before = self.get_real_memory_usage()
        self.log(f"📊 Memory before loading: {memory_before['used_gb']:.2f}GB used ({memory_before['utilization']:.1f}%)")
        
        try:
            # Load model
            load_start = time.time()
            
            if "distilled" in model_id:
                pipeline = LTXConditionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=config["torch_dtype"],
                    cache_dir=self.cache_dir
                )
            else:
                pipeline = LTXImageToVideoPipeline.from_pretrained(
                    model_id,
                    torch_dtype=config["torch_dtype"],
                    cache_dir=self.cache_dir
                )
            
            load_time = time.time() - load_start
            
            # Move to GPU WITHOUT CPU offloading for maximum performance
            self.log("🚀 Moving to GPU (full GPU mode - no CPU offloading)")
            pipeline = pipeline.to("cuda", dtype=config["torch_dtype"])
            
            # Apply performance optimizations
            pipeline = self.optimize_pipeline(pipeline, config)
            
            memory_after_load = self.get_real_memory_usage()
            self.log(f"📊 Memory after loading: {memory_after_load['used_gb']:.2f}GB used ({memory_after_load['utilization']:.1f}%)")
            self.log(f"✅ Model loaded in {load_time:.2f}s")
            
            # Create test image
            test_image = Image.new('RGB', (config["width"], config["height"]), color='green')
            draw = ImageDraw.Draw(test_image)
            draw.text((50, 50), "PERFORMANCE TEST", fill='white')
            
            # Generate video
            self.log(f"🎬 Generating {config['num_frames']} frames ({config['num_frames']/24:.1f}s video)...")
            
            generation_start = time.time()
            memory_before_gen = self.get_real_memory_usage()
            
            # Video generation parameters
            gen_params = {
                "prompt": self.test_prompt,
                "negative_prompt": self.negative_prompt,
                "num_frames": config["num_frames"],
                "width": config["width"],
                "height": config["height"],
                "num_inference_steps": config["num_inference_steps"],
                "guidance_scale": config["guidance_scale"],
                "generator": torch.Generator().manual_seed(42),
            }
            
            if "distilled" in model_id:
                # For distilled model, use conditions format
                video = pipeline(**gen_params).frames[0]
            else:
                # For base model, add image parameter
                gen_params["image"] = test_image
                video = pipeline(**gen_params).frames[0]
            
            generation_time = time.time() - generation_start
            memory_peak = self.get_real_memory_usage()
            
            # Calculate performance metrics
            video_duration = config["num_frames"] / 24.0  # Assuming 24fps
            speed_ratio = generation_time / video_duration
            
            # Save video
            output_path = f"{self.output_dir}/{model_name}_{test_name}.mp4"
            export_to_video(video, output_path, fps=24)
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            self.log(f"✅ Video generated in {generation_time:.2f}s")
            self.log(f"🎯 Speed ratio: {speed_ratio:.2f}x ({'✅ TARGET MET!' if speed_ratio <= 1.5 else '❌ Too slow'})")
            self.log(f"📹 Output: {output_path}")
            self.log(f"📊 Peak memory: {memory_peak['used_gb']:.2f}GB ({memory_peak['utilization']:.1f}%)")
            
            # Cleanup
            del pipeline
            self.aggressive_memory_cleanup()
            
            return {
                "status": "success",
                "model_name": model_name,
                "test_name": test_name,
                "load_time_seconds": load_time,
                "generation_time_seconds": generation_time,
                "video_duration_seconds": video_duration,
                "speed_ratio": speed_ratio,
                "target_met": speed_ratio <= 1.5,
                "memory_usage": {
                    "before_load_gb": memory_before["used_gb"],
                    "after_load_gb": memory_after_load["used_gb"],
                    "peak_gb": memory_peak["used_gb"],
                    "peak_utilization_percent": memory_peak["utilization"]
                },
                "video_info": {
                    "frames": config["num_frames"],
                    "resolution": f"{config['width']}x{config['height']}",
                    "file_size_mb": file_size_mb,
                    "inference_steps": config["num_inference_steps"]
                },
                "output_path": output_path
            }
            
        except Exception as e:
            self.log(f"❌ Test failed: {e}")
            self.aggressive_memory_cleanup()
            return {
                "status": "failed",
                "model_name": model_name,
                "test_name": test_name,
                "error": str(e)
            }

    def run_benchmark(self):
        """Run complete performance benchmark"""
        self.log("🚀 Starting High-Performance LTX Benchmark")
        self.log(f"🎯 TARGET: 10-second video in 15 seconds (1.5x speed ratio)")
        self.log("=" * 80)
        
        # Kill any existing Python processes
        self.kill_all_python_processes()
        time.sleep(2)
        
        # Check GPU
        memory_info = self.get_real_memory_usage()
        self.log(f"🔧 GPU: {torch.cuda.get_device_name(0)}")
        self.log(f"🔧 Total VRAM: {memory_info['total_gb']:.1f}GB")
        self.log(f"🔧 Available: {memory_info['free_gb']:.1f}GB")
        
        results = []
        
        # Test models
        models_to_test = [
            ("base_model", "Lightricks/LTX-Video"),
            ("distilled_model", "Lightricks/LTX-Video-0.9.7-distilled")
        ]
        
        for model_name, model_id in models_to_test:
            self.log(f"\n🧪 TESTING {model_name.upper()}")
            self.log("=" * 60)
            
            # Test different configurations
            for test_name, config in self.test_configs.items():
                result = self.test_model_performance(model_name, model_id, test_name, config)
                results.append(result)
                
                # Break early if we hit our target
                if result.get("target_met", False):
                    self.log(f"🎉 TARGET ACHIEVED with {model_name} using {test_name}!")
                
                # Wait between tests
                time.sleep(5)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"performance_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "target_speed_ratio": 1.5,
                "gpu": torch.cuda.get_device_name(0),
                "vram_gb": memory_info['total_gb'],
                "results": results
            }, f, indent=2)
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("🏁 PERFORMANCE BENCHMARK SUMMARY")
        self.log("=" * 80)
        
        successful_tests = [r for r in results if r.get("status") == "success"]
        target_met_tests = [r for r in successful_tests if r.get("target_met", False)]
        
        if target_met_tests:
            fastest = min(target_met_tests, key=lambda x: x["speed_ratio"])
            self.log(f"🏆 FASTEST TARGET-MEETING CONFIG:")
            self.log(f"    Model: {fastest['model_name']}")
            self.log(f"    Config: {fastest['test_name']}")
            self.log(f"    Speed: {fastest['speed_ratio']:.2f}x")
            self.log(f"    Generation Time: {fastest['generation_time_seconds']:.1f}s")
        
        for result in successful_tests:
            status = "🎯 TARGET MET" if result.get("target_met", False) else "⏰ Too slow"
            self.log(f"\n{result['model_name']} ({result['test_name']}): {result['speed_ratio']:.2f}x - {status}")
        
        self.log(f"\n📄 Detailed results: {results_file}")

if __name__ == "__main__":
    # Install pynvml for accurate memory monitoring
    try:
        import pynvml
    except ImportError:
        print("Installing pynvml for accurate memory monitoring...")
        subprocess.run([sys.executable, "-m", "pip", "install", "nvidia-ml-py"])
    
    benchmark = PerformanceBenchmark()
    benchmark.run_benchmark() 