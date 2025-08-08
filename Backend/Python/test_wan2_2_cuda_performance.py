#!/usr/bin/env python3
"""
Wan2.2 CUDA Performance Test
Based on official GitHub repository specifications and computational efficiency guidelines

Repository: https://github.com/Wan-Video/Wan2.2
Target: RTX 4080 16GB - 5-second video generation
Expected: <9 minutes total time (GitHub benchmark)

Key Features from GitHub:
- TI2V-5B: 5B dense model for single GPU
- High compression VAE (4×16×16)
- Native 720P@24fps support
- Consumer GPU optimized
- Smart offloading for memory efficiency

Computational Efficiency (from GitHub):
Single-GPU 5B: --offload_model True --convert_model_dtype --t5_cpu
"""

import os
import sys
import subprocess
import time
import torch
import psutil
from pathlib import Path
import json
import tempfile

class Wan2CudaPerformanceTest:
    def __init__(self):
        self.start_time = None
        self.model_dir = "models/wan2_2"
        self.wan2_dir = "Wan2.2"
        self.results = {}
        
        # GitHub specifications for RTX 4080 class GPUs
        self.test_configs = {
            "5_second_720p": {
                "task": "ti2v-5B",
                "size": "1280*704",  # 720P
                "frame_num": 120,    # 5 seconds at 24fps
                "sample_steps": 50,  # Default quality
                "expected_time": 540,  # 9 minutes (GitHub benchmark)
                "expected_vram": 12   # Estimated for RTX 4080
            },
            "2_second_test": {
                "task": "ti2v-5B", 
                "size": "1280*704",
                "frame_num": 48,     # 2 seconds at 24fps
                "sample_steps": 25,  # Reduced for testing
                "expected_time": 216, # Proportional to 5s
                "expected_vram": 10   # Estimated
            }
        }

    def check_environment(self):
        """Comprehensive environment check based on GitHub requirements"""
        print("🔍 ENVIRONMENT VERIFICATION")
        print("=" * 50)
        
        # Check CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"✅ CUDA Available: {cuda_available}")
        
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            device_count = torch.cuda.device_count()
            compute_capability = torch.cuda.get_device_capability(0)
            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            print(f"✅ GPU: {device_name}")
            print(f"✅ Compute Capability: {compute_capability[0]}.{compute_capability[1]}")
            print(f"✅ Total VRAM: {total_memory:.1f}GB")
            print(f"✅ Device Count: {device_count}")
            
            # Check if RTX 4080 class
            if "4080" in device_name or total_memory >= 15.0:
                print("✅ RTX 4080 class GPU detected - suitable for testing")
            else:
                print(f"⚠️  GPU may not meet RTX 4080 requirements")
        else:
            print("❌ CUDA not available - cannot proceed")
            return False
            
        # Check PyTorch version
        torch_version = torch.__version__
        print(f"✅ PyTorch Version: {torch_version}")
        
        # Check Python version
        python_version = sys.version
        print(f"✅ Python Version: {python_version}")
        
        # Check model files
        model_path = Path(self.model_dir)
        if model_path.exists():
            total_size = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
            total_size_gb = total_size / (1024**3)
            print(f"✅ Model Directory: {model_path} ({total_size_gb:.1f}GB)")
            
            # Check key model files
            required_files = [
                "diffusion_pytorch_model-00001-of-00003.safetensors",
                "diffusion_pytorch_model-00002-of-00003.safetensors", 
                "diffusion_pytorch_model-00003-of-00003.safetensors",
                "models_t5_umt5-xxl-enc-bf16.pth",
                "Wan2.2_VAE.pth"
            ]
            
            for file in required_files:
                file_path = model_path / file
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024**2)
                    print(f"   ✅ {file}: {size_mb:.0f}MB")
                else:
                    print(f"   ❌ {file}: Missing")
                    return False
        else:
            print(f"❌ Model directory not found: {model_path}")
            return False
            
        # Check Wan2.2 repository
        wan2_path = Path(self.wan2_dir)
        if wan2_path.exists():
            generate_py = wan2_path / "generate.py"
            if generate_py.exists():
                print(f"✅ Wan2.2 Repository: {wan2_path}")
            else:
                print(f"❌ generate.py not found in {wan2_path}")
                return False
        else:
            print(f"❌ Wan2.2 repository not found: {wan2_path}")
            return False
            
        return True

    def check_vram_usage(self):
        """Enhanced VRAM monitoring"""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / (1024**3)
            reserved = torch.cuda.memory_reserved() / (1024**3)
            total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            free = total - reserved
            utilization = (reserved / total) * 100
            
            return {
                "allocated": allocated,
                "reserved": reserved,
                "free": free,
                "total": total,
                "utilization": utilization,
                "summary": f"VRAM: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved ({utilization:.1f}% utilization)"
            }
        else:
            return {"summary": "CUDA not available"}

    def set_cuda_optimizations(self):
        """Set CUDA environment optimizations based on GitHub best practices"""
        print("\n🚀 CUDA OPTIMIZATIONS")
        print("=" * 30)
        
        # Environment variables for RTX 4080 optimization
        cuda_env = {
            'PYTORCH_CUDA_ALLOC_CONF': 'expandable_segments:True',
            'CUDA_LAUNCH_BLOCKING': '0',  # Async execution
            'TORCH_CUDNN_V8_API_ENABLED': '1',
            'CUDA_DEVICE_ORDER': 'PCI_BUS_ID',
            'CUDA_VISIBLE_DEVICES': '0'
        }
        
        for key, value in cuda_env.items():
            os.environ[key] = value
            print(f"   Set {key}={value}")
            
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            print("   Cleared CUDA cache and synchronized")

    def build_command(self, config_name):
        """Build command exactly as specified in GitHub repository"""
        config = self.test_configs[config_name]
        
        # GitHub single-GPU specifications for ti2v-5B
        cmd = [
            "python", "generate.py",
            "--task", config["task"],
            "--size", config["size"],
            "--frame_num", str(config["frame_num"]),
            "--ckpt_dir", f"../{self.model_dir}",
            "--offload_model", "True",       # GitHub specification
            "--convert_model_dtype",         # GitHub specification
            "--t5_cpu",                      # GitHub specification for 5B
            "--prompt", "A simple blue sky with white clouds, cinematic quality, smooth motion",
            "--sample_steps", str(config["sample_steps"]),
            "--sample_solver", "unipc",
            "--sample_guide_scale", "5.0",
            "--sample_shift", "5.0"
        ]
        
        return cmd, config

    def run_generation_test(self, config_name):
        """Run video generation with comprehensive monitoring"""
        print(f"\n🎬 GENERATION TEST: {config_name.upper()}")
        print("=" * 50)
        
        cmd, config = self.build_command(config_name)
        
        print(f"Command: {' '.join(cmd)}")
        print(f"Expected time: {config['expected_time']}s ({config['expected_time']/60:.1f} minutes)")
        print(f"Expected VRAM: ~{config['expected_vram']}GB")
        print(f"Target: {config['frame_num']} frames at {config['size']}")
        
        # Change to Wan2.2 directory
        original_dir = os.getcwd()
        os.chdir(self.wan2_dir)
        
        try:
            start_time = time.time()
            
            # Set up process with UTF-8 encoding to handle Chinese characters
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            print(f"\n⏱️  Starting at {time.strftime('%H:%M:%S')}")
            print(f"Initial VRAM: {self.check_vram_usage()['summary']}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',  # Handle encoding errors gracefully
                env=env
            )
            
            # Monitor progress
            last_vram_check = time.time()
            generation_started = False
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                    
                if output:
                    elapsed = time.time() - start_time
                    print(f"[{elapsed:6.1f}s] {output.strip()}")
                    
                    # Track key milestones
                    if "loading" in output.lower() and "model" in output.lower():
                        vram = self.check_vram_usage()
                        print(f"         📦 Model Loading - {vram['summary']}")
                        
                    elif "generating video" in output.lower():
                        generation_started = True
                        vram = self.check_vram_usage()
                        print(f"         🎬 Generation Started - {vram['summary']}")
                        
                    elif generation_started and ("step" in output.lower() or "%" in output):
                        vram = self.check_vram_usage()
                        print(f"         ⚡ Progress - {vram['summary']}")
                        
                    # Check VRAM every 30 seconds during generation
                    if time.time() - last_vram_check > 30:
                        vram = self.check_vram_usage()
                        print(f"         📊 Periodic Check - {vram['summary']}")
                        last_vram_check = time.time()
                
                # Timeout check
                if elapsed > config['expected_time'] * 2:  # 2x expected time
                    print(f"\n⏰ TIMEOUT: Exceeded {config['expected_time']*2}s")
                    process.terminate()
                    break
            
            # Get final results
            return_code = process.poll()
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            result = self.analyze_results(config_name, total_time, return_code, config)
            
            return result
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            return {"success": False, "error": str(e)}
            
        finally:
            os.chdir(original_dir)

    def analyze_results(self, config_name, total_time, return_code, config):
        """Comprehensive result analysis"""
        print(f"\n📊 RESULTS ANALYSIS: {config_name}")
        print("=" * 40)
        
        success = return_code == 0
        
        result = {
            "config": config_name,
            "success": success,
            "total_time": total_time,
            "expected_time": config["expected_time"],
            "frame_count": config["frame_num"],
            "return_code": return_code
        }
        
        if success:
            print(f"✅ Generation successful!")
            
            # Performance metrics
            fps_generation = config["frame_num"] / total_time
            speed_ratio = config["expected_time"] / total_time
            efficiency = (speed_ratio - 1) * 100 if speed_ratio >= 1 else -(1 - speed_ratio) * 100
            
            result.update({
                "fps_generation": fps_generation,
                "speed_ratio": speed_ratio,
                "efficiency_percent": efficiency
            })
            
            print(f"   Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
            print(f"   Expected: {config['expected_time']}s ({config['expected_time']/60:.1f} minutes)")
            print(f"   Speed ratio: {speed_ratio:.2f}x {'faster' if speed_ratio > 1 else 'slower'}")
            print(f"   Generation FPS: {fps_generation:.2f} frames/second")
            print(f"   Efficiency: {efficiency:+.1f}% vs GitHub benchmark")
            
            # Check for output files
            output_files = list(Path(".").glob("*.mp4"))
            if output_files:
                for file in output_files:
                    size_mb = file.stat().st_size / (1024**2)
                    print(f"   Generated: {file.name} ({size_mb:.1f}MB)")
                    result["output_file"] = str(file.name)
                    result["output_size_mb"] = size_mb
            else:
                print("   ⚠️  No output files found")
                
        else:
            print(f"❌ Generation failed (code: {return_code})")
            print(f"   Time before failure: {total_time:.1f}s")
            
        # Final VRAM check
        final_vram = self.check_vram_usage()
        print(f"   Final VRAM: {final_vram['summary']}")
        result["final_vram"] = final_vram
        
        return result

    def run_comprehensive_test(self):
        """Run comprehensive CUDA performance test"""
        print("🚀 WAN2.2 CUDA PERFORMANCE TEST")
        print("=" * 50)
        print("Repository: https://github.com/Wan-Video/Wan2.2")
        print("Target: RTX 4080 16GB optimal performance")
        print("=" * 50)
        
        # Step 1: Environment check
        if not self.check_environment():
            print("\n❌ Environment check failed")
            return False
            
        # Step 2: CUDA optimizations
        self.set_cuda_optimizations()
        
        # Step 3: Run tests
        test_results = {}
        
        # Quick test first (2 seconds)
        print(f"\n🧪 PHASE 1: Quick Test (2 seconds)")
        result_2s = self.run_generation_test("2_second_test")
        test_results["2_second"] = result_2s
        
        if result_2s["success"]:
            print("\n✅ Quick test successful! Proceeding to full test...")
            
            # Full test (5 seconds)
            print(f"\n🧪 PHASE 2: Full Performance Test (5 seconds)")
            result_5s = self.run_generation_test("5_second_720p")
            test_results["5_second"] = result_5s
        else:
            print("\n❌ Quick test failed - skipping full test")
            
        # Generate summary report
        self.generate_report(test_results)
        
        return test_results

    def generate_report(self, results):
        """Generate comprehensive performance report"""
        print(f"\n📋 PERFORMANCE REPORT")
        print("=" * 50)
        
        for test_name, result in results.items():
            print(f"\n{test_name.upper()} TEST:")
            if result["success"]:
                print(f"   ✅ Status: Successful")
                print(f"   ⏱️  Time: {result['total_time']:.1f}s")
                print(f"   🎯 vs Target: {result['speed_ratio']:.2f}x")
                print(f"   📈 Efficiency: {result['efficiency_percent']:+.1f}%")
                if "output_file" in result:
                    print(f"   📁 Output: {result['output_file']} ({result['output_size_mb']:.1f}MB)")
            else:
                print(f"   ❌ Status: Failed")
                print(f"   ⏱️  Time: {result['total_time']:.1f}s (before failure)")
                
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if "5_second" in results and results["5_second"]["success"]:
            efficiency = results["5_second"]["efficiency_percent"]
            if efficiency >= 0:
                print(f"   🚀 EXCELLENT: Meets/exceeds GitHub benchmarks ({efficiency:+.1f}%)")
            else:
                print(f"   ⚠️  BELOW TARGET: {efficiency:+.1f}% vs GitHub benchmark")
        elif "2_second" in results and results["2_second"]["success"]:
            print(f"   ⚠️  PARTIAL: 2s test successful, 5s test needed")
        else:
            print(f"   ❌ FAILED: Environment/setup issues detected")
            
        # Save results to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"wan2_cuda_test_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        print(f"\n📊 Detailed results saved to: {report_file}")

def main():
    """Main test execution"""
    tester = Wan2CudaPerformanceTest()
    
    print("Starting Wan2.2 CUDA Performance Test...")
    print("Press Enter to continue or Ctrl+C to abort...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest aborted by user")
        return
        
    results = tester.run_comprehensive_test()
    
    if any(r.get("success", False) for r in results.values()):
        print("\n🎉 Test completed successfully!")
        return True
    else:
        print("\n❌ Test failed - check environment and setup")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)