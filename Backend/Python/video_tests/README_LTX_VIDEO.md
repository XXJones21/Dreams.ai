# LTX Video Generation Integration for Dreams.ai

## Overview

This integration extends the Dreams.ai pipeline with ultra-fast local video generation using LTX-Video models. The system is optimized for RTX 4080 16GB setups and targets **10-second video generation in 15 seconds** for mobile screens.

## Architecture

### Pipeline Flow
```
Carthir (Story) → IMN Creation → Narnion (Scene) → CarthirReview (Director) → Cenedril (Image) → CenedrilVideo (Video) → Complete
```

### New Components

1. **`core/video_generator.py`** - LTX video generation engine
2. **`CenedrilVideo` agent** - Pipeline integration agent
3. **Mobile optimization** - 9:16 aspect ratio, 576x1024 resolution
4. **Performance monitoring** - Real-time generation tracking

## Key Features

### 🚀 Ultra-Fast Generation
- **Target**: 10-second videos in 15 seconds (1.5x real-time)
- **Model**: LTX-Video 2B distilled for RTX 4080 optimization
- **Mobile-first**: 9:16 aspect ratio optimized for social media

### 🎬 Seamless Integration
- Extends existing Cenedril image generation to video
- Uses Cenedril's shot composition prompts as video base
- Incorporates Narnion's scene context for narrative coherence
- Stores results in IMN structure for pipeline consistency

### 📱 Mobile Optimization
- **Resolution**: 576x1024 (mobile-optimized 9:16)
- **Duration**: ~3 seconds default (customizable)
- **Frame rate**: 25 FPS
- **Quality**: Optimized for social media platforms

## Installation

### 1. Install Dependencies
```bash
cd Backend/Python
python install_ltx_video.py
```

### 2. Verify Installation
```bash
python test_ltx_video.py
```

### 3. Test Pipeline Integration
```bash
python main.py  # Run your Dreams.ai pipeline
```

## Configuration

### Mobile Video Settings (RTX 4080 Optimized)
```python
mobile_config = {
    "width": 576,       # 9:16 mobile aspect ratio
    "height": 1024,     # Mobile screen optimized
    "num_frames": 81,   # ~3 seconds at 25fps
    "num_inference_steps": 8,  # Fast generation
    "guidance_scale": 1.0,     # Distilled model optimal
    "fps": 25
}
```

### Performance Targets
- **Real-time ratio**: <1.5x (generate faster than playback)
- **Memory usage**: <14GB VRAM (RTX 4080 compatible)
- **Quality**: Mobile-optimized with first-person perspective

## Usage

### Basic Pipeline Run
The video generation is automatically integrated into your existing Dreams.ai pipeline. After Cenedril generates an image, CenedrilVideo will:

1. Take Cenedril's generated image as input
2. Optimize the image prompt for video generation
3. Generate a mobile-optimized video
4. Store results in the IMN structure

### Manual Video Generation
```python
from core.video_generator import get_video_generator

# Initialize generator
generator = get_video_generator()
generator.load_model()

# Generate video
success, video_path, metadata = generator.generate_video_for_cenedril(
    image_path="path/to/cenedril_image.png",
    cenedril_prompt="First-person POV shot composition...",
    story_context="Scene context from Narnion...",
    dream_id="unique_dream_id"
)
```

## Performance Monitoring

### Real-time Metrics
- **Generation time**: Actual time to generate video
- **Video duration**: Length of generated video
- **Speed ratio**: Generation time / video duration
- **Memory usage**: VRAM utilization tracking

### Performance Assessment
- **🎉 EXCELLENT**: <1.5x ratio (real-time target achieved)
- **✅ GOOD**: 1.5-3.0x ratio (near real-time)
- **⚠️ SLOW**: >3.0x ratio (needs optimization)

## File Structure

```
Backend/Python/
├── core/
│   ├── video_generator.py      # LTX video generation engine
│   └── agents.py               # Updated with CenedrilVideo agent
├── requirements_ltx_video.txt  # Video generation dependencies
├── install_ltx_video.py        # Installation script
├── test_ltx_video.py          # Test and verification script
└── README_LTX_VIDEO.md        # This documentation
```

## Troubleshooting

### Common Issues

1. **Out of memory errors**
   - Reduce `num_frames` (e.g., 49 instead of 81)
   - Use FP8 quantized models
   - Enable CPU offloading

2. **Slow generation**
   - Verify RTX 4080 CUDA setup
   - Check VRAM availability
   - Consider reducing resolution

3. **Import errors**
   - Run `python install_ltx_video.py`
   - Verify diffusers version >=0.34.0
   - Check torch CUDA compatibility

### Performance Optimization

1. **Memory Management**
   ```python
   # Enable optimizations in video_generator.py
   pipeline.enable_model_cpu_offload()
   torch.cuda.empty_cache()
   ```

2. **Speed Tuning**
   ```python
   # Adjust config for faster generation
   config = {
       "num_frames": 49,  # Shorter videos
       "num_inference_steps": 4,  # Fewer steps
       "guidance_scale": 1.0  # Optimal for distilled
   }
   ```

## Technical Specifications

### Hardware Requirements
- **GPU**: RTX 4080 16GB (recommended)
- **VRAM**: 12GB minimum, 16GB optimal
- **Python**: 3.10+
- **CUDA**: 12.1+

### Model Specifications
- **Base Model**: LTX-Video (Lightricks)
- **Variant**: 2B parameter distilled model
- **Quantization**: FP16/BF16 with optional FP8
- **Context**: Image-to-video generation

### Output Specifications
- **Resolution**: 576x1024 (9:16 mobile)
- **Frame Rate**: 25 FPS
- **Duration**: 3-10 seconds (configurable)
- **Format**: MP4 H.264
- **Quality**: Mobile-optimized compression

## Integration with Dreams.ai

### IMN Structure Updates
The video generation adds a new section to the IMN file:
```json
{
  "video_generation": [
    {
      "video_path": "path/to/generated_video.mp4",
      "generation_metadata": { ... },
      "source_image": "path/to/cenedril_image.png",
      "optimized_prompt": "First-person POV: ...",
      "generation_time": 12.5,
      "performance_ratio": 1.38,
      "created_at": "2025-01-20T..."
    }
  ]
}
```

### Pipeline State Management
- Video generation is optional and non-blocking
- Failures gracefully continue the pipeline
- Performance metrics stored for analysis
- Memory management prevents VRAM overflow

## Future Enhancements

### Planned Features
1. **Variable duration** - User-controlled video length
2. **Style consistency** - LoRA integration for visual style
3. **Batch generation** - Multiple videos per dream
4. **Quality upscaling** - Temporal and spatial upscalers
5. **Interactive controls** - Real-time parameter adjustment

### Model Upgrades
- **13B model support** - Higher quality option
- **Quantization improvements** - Better memory efficiency
- **Custom fine-tuning** - Dreams.ai specific optimization

## Contributing

### Development Guidelines
1. Maintain RTX 4080 compatibility
2. Preserve mobile-first optimization
3. Keep real-time performance targets
4. Add comprehensive error handling
5. Update performance metrics

### Testing
```bash
# Run full test suite
python test_ltx_video.py

# Test pipeline integration
python main.py --test-video-generation

# Performance benchmarking
python benchmark_video_performance.py
```

---

**Created for Dreams.ai** | **Optimized for RTX 4080 16GB** | **Target: Real-time Mobile Video Generation** 