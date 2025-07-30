# Cenedril Ultra-Fast Local Video Generation Integration Plan

**Date:** January 20, 2025  
**Status:** 🔄 **PLANNING PHASE**  
**Target:** 10-second mobile video generation in 15 seconds using RTX 4080 16GB  
**Primary Model:** LTX-Video with RIFE frame interpolation  
**Architecture:** Local GGUF-compatible pipeline with mobile optimization

## Executive Summary

This document outlines the integration of ultra-fast local video generation capabilities into the Cenedril (The Cinematographer) agent. The goal is to extend Cenedril from static shot composition generation to full video creation, leveraging the existing IMN structure and creating mobile-optimized first-person perspective videos. The implementation focuses on aggressive speed optimization to achieve 10-second video generation in 15 seconds on RTX 4080 16GB hardware.

### Key Objectives
- **Speed Target:** 10-second video in 15 seconds (1.5x real-time)
- **Quality Target:** 720p mobile-optimized (9:16 aspect ratio)
- **Hardware:** RTX 4080 16GB VRAM constraint
- **Models:** Local LTX-Video + quantized RIFE for frame interpolation
- **Integration:** Seamless extension of existing Cenedril agent workflow

## Technical Requirements Analysis

### Hardware Constraints & Optimization Strategy
```
RTX 4080 Specifications:
- VRAM: 16GB GDDR6X
- Memory Bandwidth: 716.8 GB/s
- CUDA Cores: 9,728
- RT Cores: 76 (3rd gen)
- Tensor Cores: 304 (4th gen)

Target Performance:
- Input: Cenedril shot composition (text prompt)
- Processing: 15 seconds maximum
- Output: 10-second 720p video (9:16 mobile)
- Frame Rate: 24 FPS (240 frames total)
```

### Model Selection & Quantization Strategy

#### Primary Model: LTX-Video (Optimized)
```python
Model Specifications:
- Architecture: Diffusion Transformer
- Base Size: ~5GB (F16)
- Quantized: ~3GB (Q4_K_M)
- VRAM Usage: 8-10GB peak
- Generation Speed: 0.8-1.2 seconds per frame
- Strengths: Temporal consistency, local inference
```

#### Frame Interpolation: RIFE (Quantized)
```python
RIFE Configuration:
- Model: RIFE 4.6 (latest)
- Quantization: INT8
- VRAM Usage: 2-3GB
- Speed: 40-60 FPS interpolation
- Purpose: 12 base frames → 240 final frames
```

## Implementation Strategy

### Phase 1: Core Infrastructure (Week 1)
**Objective:** Set up local video generation infrastructure

#### 1.1 Model Download & Optimization
```bash
# Model preparation commands
cd Backend/Python/models/
wget https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.safetensors
wget https://github.com/hzwer/ARXIV-RIFE/releases/download/v4.6/flownet.pkl

# Quantization (using ollama or similar)
python quantize_ltx.py --model ltx-video-2b-v0.9.safetensors --output ltx-video-q4.gguf
```

#### 1.2 Dependencies & Environment Setup
```python
# requirements_video.txt additions
torch>=2.0.0
torchvision>=0.15.0
diffusers>=0.21.0
transformers>=4.30.0
accelerate>=0.20.0
xformers>=0.0.20  # Memory optimization
opencv-python>=4.8.0
pillow>=9.5.0
numpy>=1.24.0
```

#### 1.3 GPU Memory Management
```python
# gpu_memory_manager.py
class VideoMemoryManager:
    def __init__(self, total_vram=16):
        self.total_vram = total_vram * 1024  # MB
        self.reserved_system = 2048  # 2GB for system
        self.available_vram = self.total_vram - self.reserved_system
        
    def optimize_for_speed(self):
        return {
            "enable_memory_efficient_attention": True,
            "enable_vae_slicing": False,  # Speed over memory
            "enable_sequential_cpu_offload": False,
            "torch_compile": True,  # PyTorch 2.0 optimization
            "channels_last": True  # Memory layout optimization
        }
```

### Phase 2: Agent Architecture Integration (Week 2)
**Objective:** Integrate video generation into existing agent pipeline

#### 2.1 New Agent: CenedrilVideo
```python
def CenedrilVideo(state: State) -> Command[Literal["carthir_supervisor"]]:
    """
    Ultra-fast local video generation from Cenedril's shot composition.
    Target: 10-second video in 15 seconds on RTX 4080 16GB.
    """
    print(f"[CenedrilVideo] 🎬 Starting ultra-fast video generation...")
    
    # Phase 1: Data Validation & Extraction
    dream_id = state.get("id")
    if not dream_id:
        raise ValueError("[CenedrilVideo] CRITICAL ERROR: No dream ID found")
    
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    
    # Extract Cenedril's shot composition
    cenedril_prompt = imn_data["pre_production"]["cenedril_shot_composition"]
    if not cenedril_prompt:
        raise ValueError("[CenedrilVideo] CRITICAL ERROR: No shot composition from Cenedril")
    
    # Phase 2: Video Generation Pipeline
    video_config = {
        "prompt": cenedril_prompt,
        "duration": 10.0,  # seconds
        "fps": 24,
        "resolution": (720, 1280),  # 9:16 mobile
        "guidance_scale": 7.5,
        "num_inference_steps": 20,  # Reduced for speed
        "enable_memory_efficient_attention": True
    }
    
    # Phase 3: Generate Video
    video_path = generate_ultra_fast_video(video_config, dream_id)
    
    # Phase 4: Store Results in IMN
    imn_data["post_production"] = {
        "video_generation": {
            "status": "completed",
            "video_path": video_path,
            "generation_time": time.time() - start_time,
            "config": video_config
        }
    }
    
    with get_imn_filelock(imn_file_path):
        write_imn(imn_data, directory)
    
    return Command(goto="carthir_supervisor")
```

#### 2.2 Ultra-Fast Generation Function
```python
def generate_ultra_fast_video(config: dict, dream_id: str) -> str:
    """
    Core video generation with aggressive optimization for 15-second target.
    """
    import torch
    import time
    from diffusers import LTXPipeline
    
    start_time = time.time()
    
    # Initialize pipeline with maximum optimization
    pipe = LTXPipeline.from_pretrained(
        "models/ltx-video-q4.gguf",
        torch_dtype=torch.float16,
        variant="fp16"
    )
    
    # Aggressive optimization
    pipe.enable_memory_efficient_attention()
    pipe.enable_model_cpu_offload()
    pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead")
    
    # Mobile-optimized generation
    prompt = config["prompt"]
    
    # Generate base frames (reduced count for speed)
    base_frames = pipe(
        prompt=prompt,
        num_frames=12,  # Generate fewer base frames
        height=720,
        width=1280,
        num_inference_steps=20,  # Reduced steps
        guidance_scale=7.5,
        generator=torch.Generator("cuda").manual_seed(42)
    ).frames[0]
    
    # RIFE interpolation to reach target frame count
    interpolated_frames = rife_interpolate(base_frames, target_fps=24)
    
    # Save video
    output_path = f"generated_videos/{dream_id}_mobile.mp4"
    save_video_mobile_optimized(interpolated_frames, output_path)
    
    generation_time = time.time() - start_time
    print(f"[CenedrilVideo] ✅ Video generated in {generation_time:.2f}s")
    
    return output_path
```

#### 2.3 CarthirSupervisor Updates
```python
# Addition to CarthirSupervisor routing logic
elif pipeline_step == "cenedril_complete":
    print("[CarthirSupervisor] 🎨 Cenedril completed, routing to CenedrilVideo for video generation")
    return Command(
        goto="cenedril_video",
        update={"pipeline_step": "video_complete"}
    )

elif pipeline_step == "video_complete":
    print("[CarthirSupervisor] 🎬 Video generation completed, finishing pipeline")
    return Command(goto="__end__")
```

### Phase 3: Mobile Optimization & Performance Tuning (Week 3)
**Objective:** Achieve 15-second generation target through optimization

#### 3.1 Frame Interpolation Strategy
```python
def rife_interpolate(base_frames, target_fps=24):
    """
    RIFE-based frame interpolation for smooth video.
    12 base frames → 240 final frames (10 seconds @ 24fps)
    """
    from RIFE_HDv3 import Model
    
    # Load quantized RIFE model
    model = Model()
    model.load_model('models/rife_q8.pth', -1)
    
    # Interpolate between each pair of base frames
    interpolated = []
    for i in range(len(base_frames) - 1):
        frame_a = base_frames[i]
        frame_b = base_frames[i + 1]
        
        # Generate 19 intermediate frames between each pair
        intermediate_frames = model.inference(frame_a, frame_b, num_frames=19)
        interpolated.extend([frame_a] + intermediate_frames)
    
    interpolated.append(base_frames[-1])  # Add final frame
    return interpolated[:240]  # Ensure exactly 240 frames
```

#### 3.2 Mobile Video Encoding
```python
def save_video_mobile_optimized(frames, output_path):
    """
    Mobile-optimized H.264 encoding with small file size.
    """
    import cv2
    
    # Mobile-optimized codec settings
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(
        output_path, fourcc, 24.0, (1280, 720),
        # Optimized for mobile playback
        params=[
            cv2.VIDEOWRITER_PROP_QUALITY, 80,  # Good quality/size balance
            cv2.VIDEOWRITER_PROP_BITRATE, 2000000  # 2Mbps for mobile
        ]
    )
    
    for frame in frames:
        # Convert to mobile-friendly format
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)
    
    out.release()
```

### Phase 4: IMN Structure Extension (Week 4)
**Objective:** Extend IMN format to support video generation data

#### 4.1 IMN Schema Updates
```python
# core/imn_utils.py additions
def create_video_structure():
    """Create video generation structure for IMN files."""
    return {
        "video_generation": {
            "status": "pending",
            "model_config": {
                "primary_model": "LTX-Video",
                "interpolation_model": "RIFE",
                "quantization": "Q4_K_M",
                "optimization_level": "ultra_fast"
            },
            "generation_metadata": {
                "start_time": None,
                "end_time": None,
                "generation_duration": None,
                "frame_count": 240,
                "fps": 24,
                "resolution": "720x1280"
            },
            "output": {
                "video_path": None,
                "file_size": None,
                "duration": 10.0
            }
        }
    }

def update_imn_for_video():
    """Update IMN structure to include post_production section."""
    # Add to create_imn_structure function
    imn_data["post_production"] = create_video_structure()
```

## Performance Optimization Strategies

### GPU Memory Optimization
```python
# Memory management strategies
optimization_config = {
    "model_loading": {
        "use_safetensors": True,
        "load_in_4bit": True,
        "torch_dtype": "float16",
        "device_map": "auto"
    },
    "inference": {
        "enable_memory_efficient_attention": True,
        "enable_sequential_cpu_offload": False,  # Keep on GPU for speed
        "enable_vae_slicing": False,  # Speed over memory
        "enable_vae_tiling": False,
        "torch_compile": True
    },
    "pipeline": {
        "num_inference_steps": 20,  # Reduced from default 50
        "guidance_scale": 7.5,
        "scheduler": "DPMSolverMultistepScheduler"  # Faster convergence
    }
}
```

### Batch Processing Strategy
```python
def batch_frame_generation(prompt, num_frames=12):
    """
    Generate frames in optimized batches for maximum GPU utilization.
    """
    # Generate all frames in single batch for temporal consistency
    batch_size = 4  # Balanced for 16GB VRAM
    frame_batches = []
    
    for i in range(0, num_frames, batch_size):
        batch_frames = pipe(
            prompt=[prompt] * min(batch_size, num_frames - i),
            num_frames=1,  # Single frame per prompt
            height=720,
            width=1280,
            num_inference_steps=20,
            guidance_scale=7.5
        ).frames
        frame_batches.extend(batch_frames)
    
    return frame_batches
```

## Success Metrics & Testing

### Performance Benchmarks
- **Generation Speed:** ≤ 15 seconds for 10-second video
- **Memory Usage:** ≤ 14GB VRAM peak (2GB buffer)
- **Output Quality:** Temporal consistency score > 0.85
- **File Size:** < 20MB for mobile compatibility

### Test Cases
1. **Simple Static Scene:** Basic POV shot (target: 10 seconds generation)
2. **Moving Camera:** Walking/movement simulation (target: 12 seconds)
3. **Complex Environment:** Multiple objects/lighting (target: 15 seconds)
4. **Stress Test:** Maximum complexity (monitor for failures)

### Quality Assurance
```python
def validate_video_output(video_path):
    """Validate generated video meets quality standards."""
    import cv2
    
    cap = cv2.VideoCapture(video_path)
    
    # Basic validation
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps
    
    assert frame_count == 240, f"Expected 240 frames, got {frame_count}"
    assert abs(fps - 24) < 0.1, f"Expected 24 FPS, got {fps}"
    assert abs(duration - 10.0) < 0.1, f"Expected 10s duration, got {duration}"
    
    cap.release()
    return True
```

## Risk Assessment & Mitigation

### Technical Risks
1. **VRAM Overflow:** Implement dynamic model offloading
2. **Generation Timeout:** Fallback to lower quality settings
3. **Model Compatibility:** Test all quantized models before deployment
4. **Temporal Inconsistency:** Validate RIFE interpolation quality

### Mitigation Strategies
```python
class VideoGenerationFallback:
    """Fallback strategies for failed video generation."""
    
    def handle_vram_overflow(self):
        # Reduce batch size and enable CPU offloading
        return {"batch_size": 1, "enable_cpu_offload": True}
    
    def handle_timeout(self):
        # Reduce quality for speed
        return {"num_inference_steps": 10, "num_frames": 8}
    
    def handle_model_error(self):
        # Fallback to image sequence
        return "generate_image_sequence"
```

## Implementation Timeline

### Week 1: Infrastructure Setup
- [ ] Download and quantize LTX-Video model
- [ ] Set up RIFE interpolation
- [ ] Configure GPU memory management
- [ ] Basic pipeline testing

### Week 2: Agent Integration
- [ ] Implement CenedrilVideo agent
- [ ] Update CarthirSupervisor routing
- [ ] Integrate with IMN structure
- [ ] Basic end-to-end testing

### Week 3: Optimization
- [ ] Implement frame interpolation
- [ ] Mobile video encoding
- [ ] Performance tuning
- [ ] Memory optimization

### Week 4: Testing & Validation
- [ ] Comprehensive testing suite
- [ ] Performance benchmarking
- [ ] Quality validation
- [ ] Documentation completion

## Next Steps

1. **Immediate:** Set up development environment with LTX-Video
2. **Week 1:** Begin model quantization and basic inference testing
3. **Week 2:** Start agent integration with existing pipeline
4. **Week 3:** Focus on optimization and speed improvements
5. **Week 4:** Testing, validation, and deployment preparation

---

**Status:** Ready for implementation  
**Next Review:** January 27, 2025  
**Responsible:** Cenedril Video Generation Team
