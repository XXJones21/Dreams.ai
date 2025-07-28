# Dreams.ai Backend

This directory contains the Python backend for the Dreams.ai application, including the AI agent pipeline, image generation, and test suite.

## Image Generation Fix

### Issue
Previously, all dreams were sharing the same generated image despite having different prompts. This was caused by the SDXL Turbo image generator using a fixed seed (0) for all image generations.

### Solution
The image generation now uses a **random seed for initial generation** and **stores it in the IMN file** for perfect reproducibility. This ensures:

1. **True Randomness**: Each dream gets a truly random, unique image on first generation
2. **Perfect Reproducibility**: The same dream will always generate the exact same image when regenerated
3. **Shareable Dreams**: Anyone can recreate the exact same image using the stored seed
4. **Visual Markers**: Each dream's image acts as a visual marker for that specific dream

### Implementation
- **Initial Generation**: Uses `random.randint(1, 1000000)` for true randomness
- **Seed Storage**: Stores the seed in `post_production.image_generation.seed` in the IMN file
- **Regeneration**: Uses stored seed for perfect consistency
- **Metadata Storage**: Stores complete image generation parameters for full reproducibility

### Testing
Run the image uniqueness test:
```bash
python test_image_uniqueness.py
```

This will generate test images and verify they are unique.

### Utility Scripts

#### Image Regeneration
Regenerate images from existing IMN files using their stored seeds:
```bash
# Regenerate all images
python regenerate_images.py --regenerate-all

# Verify reproducibility for a specific dream
python regenerate_images.py --verify f1c48beb-efbe-48e9-8a83-d0a863ccd9c3
```

#### IMN File Structure
The image generation metadata is stored in the IMN file under `post_production.image_generation`:
```json
{
  "post_production": {
    "image_generation": {
      "seed": 123456,
      "prompt": "A majestic corgi...",
      "service": "sdxl_turbo",
      "width": 512,
      "height": 512,
      "num_inference_steps": 1,
      "guidance_scale": 0.0,
      "generation_time": 2.34,
      "filename": "sdxl_turbo_20250728_123456.png",
      "generated_at": "2025-07-28T12:34:56.789Z",
      "model": "SDXL Turbo"
    }
  }
}
```

## Components

### Core Modules
- `core/agents.py` - AI agent implementations (Carthir, Narnion, Cenedril)
- `core/image_generator.py` - Image generation services (SDXL Turbo, etc.)
- `core/imn_utils.py` - IMN file utilities
- `core/pipeline_instance.py` - Pipeline execution engine

### Test Suite
- `test_gui.py` - Web-based test interface
- `test_image_uniqueness.py` - Image generation uniqueness test

### API Server
- `api_server.py` - FastAPI server for production use
- `api/dream_routes.py` - Dream-related API endpoints

## Usage

### Development Testing
```bash
python test_gui.py
```
Access the test interface at http://localhost:5000

### Production API
```bash
python api_server.py
```

### Image Uniqueness Test
```bash
python test_image_uniqueness.py
```

## Configuration

The system supports multiple image generation services:
- SDXL Turbo (default, ultra-fast)
- Stable Diffusion
- DALL-E
- Placeholder (fallback)

Configuration is handled through the `ImageGenerationManager` class.
