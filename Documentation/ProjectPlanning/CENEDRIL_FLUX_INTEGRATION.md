# Cenedril FLUX.1-dev GGUF Integration Plan

**Date:** January 20, 2025  
**Status:** 🔄 **PLANNING PHASE**  
**Target:** Single image generation from IMN file using FLUX.1-dev GGUF  
**Model Source:** [city96/FLUX.1-dev-gguf](https://huggingface.co/city96/FLUX.1-dev-gguf)

## Executive Summary

This document outlines the integration of FLUX.1-dev GGUF model into Cenedril (The Cinematographer) agent for actual image generation capability. The goal is to transform Cenedril from a text prompt generator into a full image generation agent while maintaining the high-performance GGUF/CUDA architecture already established in Dreams.ai.

## Model Selection Rationale

### FLUX.1-dev GGUF Advantages
- **High Quality**: FLUX.1-dev is a state-of-the-art text-to-image model
- **GGUF Format**: Perfect compatibility with existing llama-cpp-python infrastructure
- **Multiple Quantization Options**: Flexible memory usage (4.03GB - 23.8GB)
- **Active Community**: 124,320 downloads last month, proven stability
- **Non-Commercial License**: Suitable for development and testing phase

### Quantization Options Analysis
Based on [city96/FLUX.1-dev-gguf](https://huggingface.co/city96/FLUX.1-dev-gguf):

| Quantization | Size | Recommended Use Case |
|--------------|------|---------------------|
| **Q4_K_S** | 6.81 GB | 🎯 **PRIMARY CHOICE** - Best balance of quality/performance |
| Q3_K_S | 5.23 GB | Backup if VRAM limited |
| Q5_K_S | 8.29 GB | Higher quality if VRAM permits |
| Q2_K | 4.03 GB | Emergency fallback for very limited systems |

**Recommended**: **Q4_K_S (6.81 GB)** for optimal quality/performance balance

## Technical Architecture Integration

### Current Infrastructure Compatibility
✅ **Existing Infrastructure Supports:**
- GGUF/CUDA acceleration with 35 GPU layers
- Dynamic threading (8-16 threads)
- Memory mapping and optimization
- Thread-safe file operations
- **Existing ImageGenerationManager**: Plugin-style architecture ready for FLUX integration

### Integration with Existing Image Generator

#### 1. FLUX Generator Class (Add to existing image_generator.py)
```python
# Add to Backend/Python/core/image_generator.py

from langchain_community.chat_models import ChatLlamaCpp
import threading

class FluxImageGenerator(ImageGenerator):
    """FLUX.1-dev GGUF image generator integrated with existing Dreams.ai architecture"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.service_name = "flux"
        self.model = None
        self.is_loaded = False
        self._setup_model()
    
    def _setup_model(self):
        """Initialize FLUX GGUF model with optimized settings"""
        # Environment-aware threading (matching existing agents.py pattern)
        is_flask_server = threading.active_count() > 1 or os.environ.get('FLASK_RUN_PORT') is not None
        
        if is_flask_server:
            optimal_threads = min(4, os.cpu_count() // 4)
            gpu_layers = 20  # Conservative for Flask environment
        else:
            optimal_threads = min(8, os.cpu_count() // 2)
            gpu_layers = 30  # More aggressive for CLI
        
        try:
            self.model = ChatLlamaCpp(
                model_path="models/flux-1-dev-Q4_K_S.gguf",
                temperature=0.8,      # Slightly higher for creativity
                max_tokens=77,        # Standard for image prompts
                top_p=0.95,
                verbose=True,
                n_ctx=512,           # Reduced for image tasks
                n_threads=optimal_threads,
                n_batch=128,         # Smaller batch for image generation
                use_mmap=True,
                use_mlock=False,
                f16_kv=True,
                n_gpu_layers=gpu_layers,
            )
            self.is_loaded = True
            print(f"[FLUX] ✅ FLUX.1-dev GGUF model loaded successfully")
            print(f"[FLUX] Threads: {optimal_threads}, GPU Layers: {gpu_layers}")
            
        except Exception as e:
            print(f"[FLUX] ❌ Failed to load FLUX model: {e}")
            self.is_loaded = False
    
    def generate_image(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Generate image using FLUX model with Dreams.ai optimization
        
        Args:
            prompt: The image generation prompt
            **kwargs: Additional parameters including director_vision
            
        Returns:
            Dict containing image data and metadata, or None if failed
        """
        if not self.is_loaded:
            print(f"[FLUX] Model not loaded, falling back to placeholder")
            # Fallback to placeholder generator
            placeholder = PlaceholderImageGenerator()
            result = placeholder.generate_image(prompt, **kwargs)
            if result:
                result['service'] = 'flux_fallback'
                result['metadata']['original_service'] = 'flux'
            return result
        
        try:
            # Enhanced prompt engineering for Dreams.ai first-person perspective
            director_vision = kwargs.get('director_vision')
            enhanced_prompt = self._create_enhanced_prompt(prompt, director_vision)
            
            print(f"[FLUX] Generating image with prompt: {enhanced_prompt[:100]}...")
            
            # Generate image using FLUX
            start_time = datetime.now()
            response = self.model.invoke(enhanced_prompt)
            end_time = datetime.now()
            
            generation_time = (end_time - start_time).total_seconds()
            
            # Process FLUX response (this will need specific implementation based on FLUX output format)
            image_result = self._process_flux_response(response, enhanced_prompt)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flux_dream_{timestamp}.png"
            
            return {
                'image_data': image_result.get("image_data"),
                'filepath': image_result.get("filepath"),
                'filename': filename,
                'prompt': enhanced_prompt,
                'service': self.service_name,
                'metadata': {
                    'width': kwargs.get('width', 512),
                    'height': kwargs.get('height', 512), 
                    'format': 'PNG',
                    'generated_at': end_time.isoformat(),
                    'generation_time': generation_time,
                    'model': 'FLUX.1-dev-Q4_K_S',
                    'threads_used': getattr(self.model, 'n_threads', 'unknown'),
                    'gpu_layers': getattr(self.model, 'n_gpu_layers', 'unknown')
                }
            }
            
        except Exception as e:
            print(f"[FLUX] Error during image generation: {e}")
            # Fallback to placeholder
            placeholder = PlaceholderImageGenerator()
            result = placeholder.generate_image(prompt, **kwargs)
            if result:
                result['service'] = 'flux_error'
                result['metadata']['flux_error'] = str(e)
            return result
    
    def _create_enhanced_prompt(self, base_prompt: str, director_vision: dict = None) -> str:
        """Create enhanced prompt optimized for Dreams.ai first-person perspective"""
        
        style_elements = []
        if director_vision:
            visual_notes = director_vision.get("visual_notes", "")
            if visual_notes:
                style_elements.append(visual_notes)
        
        # Standard Dreams.ai style elements
        style_elements.extend([
            "first-person perspective",
            "immersive viewpoint", 
            "cinematic composition",
            "high detail",
            "atmospheric lighting"
        ])
        
        style_text = ", ".join(style_elements)
        enhanced_prompt = f"{base_prompt}, {style_text}, masterpiece, best quality"
        
        return enhanced_prompt
    
    def _process_flux_response(self, response, prompt: str) -> dict:
        """Process FLUX model response and extract image data"""
        # NOTE: This will need to be implemented based on actual FLUX GGUF output format
        # For now, creating a placeholder structure that matches existing interface
        
        # The actual implementation will depend on how FLUX GGUF outputs images
        # It might be base64 encoded, binary data, or require additional processing
        
        try:
            # Placeholder implementation - replace with actual FLUX processing
            image_data = response.content  # This will need to be adapted
            
            # Save to file (using existing save_image method)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flux_dream_{timestamp}.png"
            
            # For now, create a placeholder file until we understand FLUX output format
            if isinstance(image_data, str):
                # If it's text, create a placeholder
                placeholder = PlaceholderImageGenerator()
                placeholder_result = placeholder.generate_image(f"FLUX: {prompt}")
                return {
                    "image_data": placeholder_result.get("image_data"),
                    "filepath": placeholder_result.get("filepath"),
                    "format": "PNG"
                }
            
            return {
                "image_data": image_data,
                "filepath": self.save_image(image_data, filename) if isinstance(image_data, bytes) else None,
                "format": "unknown"
            }
            
        except Exception as e:
            print(f"[FLUX] Error processing response: {e}")
            return {"image_data": None, "filepath": None, "format": "error"}

# Update the ImageGenerationManager._setup_generators method
# Add this to the existing method:
def _setup_generators_with_flux(self):
    """Enhanced setup that includes FLUX generator"""
    # Existing generators
    self.generators['placeholder'] = PlaceholderImageGenerator()
    self.default_generator = self.generators['placeholder']
    
    # Add FLUX generator
    self.generators['flux'] = FluxImageGenerator(self.config.get('flux', {}))
    
    # Add other generators if configured
    if self.config.get('stable_diffusion'):
        self.generators['stable_diffusion'] = StableDiffusionGenerator(
            self.config['stable_diffusion']
        )
    
    if self.config.get('dalle'):
        self.generators['dalle'] = DALLEGenerator(
            self.config['dalle']
        )
```

#### 2. Enhanced Cenedril Agent
```python
# Update to Backend/Python/core/agents.py - Cenedril function

def Cenedril(state: State):
    """
    Enhanced Cenedril: The Cinematographer with FLUX Image Generation
    Now generates actual images using FLUX.1-dev GGUF model via existing ImageGenerationManager
    """
    dream_id = state.get("id")
    if not dream_id:
        print("No dream ID found in state.")
        return state
        
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
        
    if imn_data is None:
        print("Error reading .imn file")
        return state
    
    director_vision = imn_data["pre_production"].get("director_vision")
    
    if director_vision:
        image_prompt = director_vision.get("image_prompt", "")
        visual_notes = director_vision.get("visual_notes", "")
        
        print(f"[Cenedril] 🎬 Using director's vision for FLUX image generation")
        print(f"[Cenedril] 📝 Image Prompt: {image_prompt}")
        print(f"[Cenedril] 🎨 Visual Notes: {visual_notes}")
        
        # Attempt FLUX image generation using existing ImageGenerationManager
        try:
            from core.image_generator import image_manager
            
            print(f"[Cenedril] 🚀 Generating image with FLUX.1-dev...")
            
            # Use the existing image generation manager with FLUX service
            image_result = image_manager.generate_image(
                prompt=image_prompt,
                service="flux",  # Specify FLUX generator
                director_vision=director_vision,
                width=512,
                height=512
            )
            
            if image_result and image_result.get('service') in ['flux']:
                # Store complete image generation results
                imn_data["pre_production"]["first_frame_prompt"] = image_prompt
                imn_data["pre_production"]["visual_notes"] = visual_notes
                imn_data["pre_production"]["generated_image"] = {
                    "method": "FLUX.1-dev-GGUF",
                    "image_data": image_result.get("image_data"),
                    "filepath": image_result.get("filepath"),
                    "filename": image_result.get("filename"),
                    "prompt_used": image_result.get("prompt"),
                    "service": image_result.get("service"),
                    "metadata": image_result.get("metadata"),
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
                generation_time = image_result.get('metadata', {}).get('generation_time', 'unknown')
                print(f"[Cenedril] ✅ Image generated successfully!")
                print(f"[Cenedril] ⏱️ Generation time: {generation_time}s")
                
            elif image_result and image_result.get('service') in ['flux_fallback', 'flux_error']:
                print(f"[Cenedril] ⚠️ FLUX generation used fallback/error mode")
                # Store the fallback result
                imn_data["pre_production"]["first_frame_prompt"] = image_prompt
                imn_data["pre_production"]["visual_notes"] = visual_notes
                imn_data["pre_production"]["generated_image"] = {
                    "method": "FLUX-fallback",
                    "image_data": image_result.get("image_data"),
                    "filepath": image_result.get("filepath"),
                    "filename": image_result.get("filename"),
                    "prompt_used": image_result.get("prompt"),
                    "service": image_result.get("service"),
                    "metadata": image_result.get("metadata"),
                    "flux_error": image_result.get('metadata', {}).get('flux_error'),
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
            else:
                print(f"[Cenedril] ❌ Image generation failed completely")
                # Fallback to prompt storage only
                imn_data["pre_production"]["first_frame_prompt"] = image_prompt
                imn_data["pre_production"]["visual_notes"] = visual_notes
                imn_data["pre_production"]["generation_failed"] = True
                
        except Exception as e:
            print(f"[Cenedril] 💥 Error in image generation: {e}")
            # Graceful fallback
            imn_data["pre_production"]["first_frame_prompt"] = image_prompt
            imn_data["pre_production"]["visual_notes"] = visual_notes
            imn_data["pre_production"]["generation_error"] = str(e)
        
        # Save updated IMN file
        directory = os.path.join("..", "Dreams")
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        
        print(f"[Cenedril] 💾 Results saved to IMN file")
        
    else:
        # Existing fallback logic remains unchanged
        print(f"[Cenedril] No director vision found, using fallback prompt generation.")
        # ... existing fallback code ...
    
    return state
```

## Implementation Timeline

### **Phase 1: Model Setup & Testing (Week 1)**

#### **Day 1-2: Model Download & Setup**
- [ ] Download FLUX.1-dev Q4_K_S model (6.81 GB)
- [ ] Create models directory structure
- [ ] Verify CUDA compatibility
- [ ] Test basic model loading

#### **Day 3-4: Core Integration**
- [ ] Implement `FluxImageGenerator` class
- [ ] Create enhanced Cenedril agent
- [ ] Update IMN schema for image data
- [ ] Implement file locking for concurrent access

#### **Day 5-7: Testing & Validation**
- [ ] Create comprehensive test suite
- [ ] Test resource allocation with dual models
- [ ] Validate image generation quality
- [ ] Performance optimization

### **Phase 2: API & Frontend Integration (Week 2)**

#### **Day 8-10: API Enhancement**
- [ ] Create image retrieval endpoints
- [ ] Implement base64 image serving
- [ ] Add metadata API endpoints
- [ ] Error handling and fallbacks

#### **Day 11-14: Testing & Optimization**
- [ ] Load testing with concurrent users
- [ ] Memory usage optimization
- [ ] Performance benchmarking
- [ ] Documentation updates

## Technical Implementation Details

### Model Storage Structure
```
Backend/Python/models/
├── Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf  # Existing text model
├── flux-1-dev-Q4_K_S.gguf                   # NEW: FLUX image model
└── model_configs.json                        # NEW: Model configuration
```

### Resource Allocation Strategy
```python
# Estimated VRAM usage:
# - Text model (Llama 3.1 8B): ~4-5 GB
# - FLUX model (Q4_K_S): ~6.8 GB
# - Total estimated: ~11-12 GB VRAM required

# Mitigation strategies:
# 1. Reduce text model GPU layers if needed
# 2. Use Q3_K_S FLUX variant for lower VRAM systems
# 3. Implement model swapping for very limited systems
```

### Enhanced IMN Schema
```json
{
  "pre_production": {
    "id": "dream-uuid",
    "generated_image": {
      "method": "FLUX.1-dev-GGUF",
      "image_data": "base64_encoded_image_or_file_path",
      "prompt_used": "enhanced_prompt_with_style",
      "generation_time": 3.45,
      "model": "FLUX.1-dev-Q4_K_S", 
      "metadata": {
        "generated_at": "2025-01-20T...",
        "threads_used": 8,
        "gpu_layers": 30
      }
    }
  }
}
```

## Testing Framework

### Unit Tests
```python
# Backend/Python/test_flux_integration.py (NEW FILE)

def test_flux_model_loading():
    """Test FLUX model loads correctly"""
    pass

def test_flux_image_generation():
    """Test single image generation"""
    pass

def test_cenedril_flux_integration():
    """Test end-to-end Cenedril with FLUX"""
    pass

def test_resource_allocation():
    """Test dual model VRAM usage"""
    pass

def test_concurrent_generation():
    """Test text + image generation concurrency"""
    pass
```

### Performance Benchmarks
```python
# Target Performance Metrics:
# - FLUX image generation: 3-7 seconds
# - Total pipeline (including image): <15 seconds  
# - VRAM usage: <12 GB total
# - No degradation to text generation speed
```

## Risk Assessment & Mitigation

### **High Priority Risks**

#### **1. VRAM Limitations**
- **Risk**: Combined models exceed available VRAM
- **Mitigation**: Dynamic model loading, quantization options, graceful fallbacks

#### **2. Generation Speed**
- **Risk**: Image generation too slow for user experience
- **Mitigation**: Async generation, progressive loading, placeholder images

#### **3. Model Compatibility**
- **Risk**: FLUX GGUF format incompatible with llama-cpp-python
- **Mitigation**: Alternative libraries, format conversion, external API fallback

### **Medium Priority Risks**

#### **4. Image Quality**
- **Risk**: Generated images don't match director's vision
- **Mitigation**: Prompt engineering, style tuning, quality validation

#### **5. Licensing Compliance**
- **Risk**: FLUX.1-dev non-commercial license restrictions
- **Mitigation**: Clear documentation, commercial model evaluation for production

## Success Criteria

### **Minimum Viable Product (MVP)**
- [ ] FLUX model loads and generates images
- [ ] Cenedril creates actual images from director's vision
- [ ] Images stored in IMN file format
- [ ] Basic API endpoint to retrieve images
- [ ] No crashes or memory leaks

### **Production Ready**
- [ ] Sub-15 second total pipeline time
- [ ] High-quality first-person perspective images
- [ ] Robust error handling and fallbacks
- [ ] Comprehensive test coverage
- [ ] Performance monitoring and metrics

## Next Steps

### **Immediate Actions (This Week)**
1. **Download FLUX.1-dev Q4_K_S** from [Hugging Face](https://huggingface.co/city96/FLUX.1-dev-gguf)
2. **Create basic FluxImageGenerator** class
3. **Test model loading** and CUDA compatibility
4. **Implement simple image generation** test

### **Short Term (Next 2 Weeks)**
1. **Full Cenedril integration** with FLUX
2. **Enhanced API endpoints** for image retrieval
3. **Comprehensive testing** framework
4. **Performance optimization** and monitoring

### **Medium Term (1-2 Months)**
1. **Production model evaluation** (commercial licensing)
2. **Advanced prompt engineering** for dream-specific imagery
3. **Real-time generation** optimization
4. **Video generation integration** for animated dream sequences

## Conclusion

This integration represents a significant milestone in Dreams.ai's evolution from text-based dream generation to truly visual, immersive experiences. By leveraging the FLUX.1-dev GGUF model within the existing high-performance architecture and ImageGenerationManager, Cenedril will transform from a prompt generator into a true "Cinematographer" capable of bringing dreams to visual life.

The implementation maintains the core principles of Dreams.ai:
- **High Performance**: GGUF/CUDA optimization
- **Thread Safety**: Robust file operations and state management  
- **Graceful Degradation**: Fallbacks for all failure modes
- **Modular Architecture**: Seamless integration with existing image generation infrastructure

**Success Metric**: Generate the first AI-created dream image that captures the magic of Dreams.ai's narrative vision, transforming Cenedril into a true visual storytelling agent.

---

*This document serves as the roadmap for Cenedril's evolution into true visual storytelling, bridging the gap between narrative imagination and visual reality.* 