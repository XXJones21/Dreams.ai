# Integrating Mistral-Small-3.2-24B-Instruct-2506-GGUF for Local LLM Inference

## Executive Summary

**Goal:**
- Remove Ollama dependency and run all LLM inference locally using the quantized GGUF version of Mistral-Small-3.2-24B-Instruct-2506.
- Enable fast, robust, and fully local agent reasoning (including multimodal for Carthir) with no external API calls.
- **Performance Target:** Achieve 10-second image generation prompt completion (currently at 22.43s).
- **Hardware Focus:** Optimize for personal GPU with lean resource utilization.
- Validation: A successful run through the full pipeline (CLI and web test suite) with all agent outputs present and no Ollama required.

---

## Step-by-Step Integration Plan

### 1. Download and Prepare the GGUF Model
- Go to [Unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF on Hugging Face](https://huggingface.co/unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF).
- Download the desired quantized GGUF file (e.g., Q4_K_M for best speed/quality trade-off on limited GPU).
- Place the model file in a known directory (e.g., `models/` in your project root).
- **Hardware Considerations:**
  - Q4_K_M: ~6-8GB VRAM (recommended for lean setup)
  - Q5_K_M: ~8-10GB VRAM (better quality, more VRAM)
  - Q8_K_M: ~12-14GB VRAM (highest quality, requires more VRAM)

### 2. Set Up llama-cpp-python with CUDA Support for Maximum Performance
- **Install llama-cpp-python with CUDA acceleration:**
  ```bash
  # Install with CUDA support for optimal performance
  CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
  
  # Or build from source for maximum optimization
  git clone https://github.com/abetlen/llama-cpp-python.git
  cd llama-cpp-python
  CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install .
  ```
- **Verify CUDA installation and test model loading:**
  ```python
  from llama_cpp import Llama
  
  # Test configuration for your hardware
  llm = Llama(
      model_path="models/mistral-small-3.2-24b-q4_k_m.gguf",
      n_gpu_layers=-1,        # Use all available GPU layers
      n_ctx=4096,             # Optimize context window for speed
      n_batch=512,            # Batch size optimized for your GPU
      n_threads=8,            # CPU threads for non-GPU operations
      use_mmap=True,          # Memory mapping for efficiency
      use_mlock=True,         # Lock memory in RAM
      verbose=False            # Reduce logging overhead
  )
  
  # Test inference
  response = llm("Hello, world!", max_tokens=50)
  print(f"Test response: {response}")
  ```

### 3. Create Optimized LLM Integration Layer
- **Design a performance-optimized LLM wrapper:**
  ```python
  class OptimizedLLM:
      def __init__(self, model_path, gpu_layers=-1, context_size=4096):
          self.llm = Llama(
              model_path=model_path,
              n_gpu_layers=gpu_layers,
              n_ctx=context_size,
              n_batch=512,
              n_threads=8,
              use_mmap=True,
              use_mlock=True,
              verbose=False
          )
          self.model_pool = {}  # For model instance pooling
      
      def invoke(self, messages, max_tokens=1024, temperature=0.7):
          # Convert LangChain format to llama-cpp format
          prompt = self._format_messages(messages)
          response = self.llm(prompt, max_tokens=max_tokens, temperature=temperature)
          return response
  ```
- **Implement model pooling for parallel agent execution:**
  - Keep model instances warm in memory
  - Share model across multiple agent threads
  - Optimize memory usage for concurrent operations

### 4. Prototype Agent Role-Based Prompting with Performance Monitoring
- **Design optimized prompt templates for each agent:**
  ```python
  # Optimized prompt templates for speed
  AGENT_PROMPTS = {
      "carthir": {
          "system": "You are Carthir, a creative film director. Generate concise, structured responses.",
          "max_tokens": 512,  # Limit for speed
          "temperature": 0.7
      },
      "narnion": {
          "system": "You are Narnion, a storyteller. Create engaging scenes efficiently.",
          "max_tokens": 256,
          "temperature": 0.8
      },
      "cenedril": {
          "system": "You are Cenedril, a cinematographer. Generate visual prompts quickly.",
          "max_tokens": 128,  # Short for speed
          "temperature": 0.6
      }
  }
  ```
- **Test role-based prompting with performance metrics:**
  - Measure inference time per agent
  - Monitor GPU utilization and memory usage
  - Validate output quality vs speed trade-offs

### 5. Refactor Pipeline to Use Local Model with CUDA Optimization
- **Replace Ollama API calls with optimized local inference:**
  ```python
  # Update agent functions to use optimized LLM
  def Carthir(state: State):
      # Use optimized LLM with role-specific settings
      llm = get_optimized_llm("carthir")
      response = llm.invoke(messages, max_tokens=512, temperature=0.7)
      # Process response and update state
      return state
  ```
- **Implement parallel agent execution with shared model:**
  - Use your existing `PipelineInstance` parallel architecture
  - Share model instances across agent threads
  - Optimize memory usage for concurrent operations
- **Add performance monitoring and logging:**
  ```python
  import time
  import psutil
  
  def monitor_performance(func):
      def wrapper(*args, **kwargs):
          start_time = time.time()
          start_memory = psutil.Process().memory_info().rss
          
          result = func(*args, **kwargs)
          
          end_time = time.time()
          end_memory = psutil.Process().memory_info().rss
          
          print(f"{func.__name__}: {end_time - start_time:.2f}s, "
                f"Memory: {(end_memory - start_memory) / 1024 / 1024:.1f}MB")
          return result
      return wrapper
  ```

### 6. Hardware-Specific Optimization and Performance Tuning
- **Profile and optimize for your specific GPU:**
  ```python
  # Performance profiling script
  def profile_model_performance():
      configs = [
          {"n_gpu_layers": -1, "n_batch": 512, "n_ctx": 4096},
          {"n_gpu_layers": -1, "n_batch": 1024, "n_ctx": 2048},
          {"n_gpu_layers": -1, "n_batch": 256, "n_ctx": 8192}
      ]
      
      for config in configs:
          start_time = time.time()
          # Test inference with config
          # Measure tokens/second and memory usage
          print(f"Config {config}: {tokens_per_second} tokens/s")
  ```
- **Experiment with different quantization levels:**
  - Test Q4_K_M, Q5_K_M, Q8_K_M for your hardware
  - Measure speed vs quality trade-offs
  - Choose optimal quantization for your 10-second target
- **Optimize context windows and batch sizes:**
  - Smaller contexts for faster inference
  - Optimal batch sizes for your GPU memory
  - Balance between speed and quality

### 7. Test and Validate with Performance Benchmarks
- **Run comprehensive performance tests:**
  ```python
  def benchmark_pipeline_performance():
      test_prompts = [
          "A magical forest adventure",
          "A space exploration mission", 
          "A detective solving a mystery"
      ]
      
      for prompt in test_prompts:
          start_time = time.time()
          result = run_full_pipeline(prompt)
          end_time = time.time()
          
          print(f"Prompt: {prompt}")
          print(f"Total time: {end_time - start_time:.2f}s")
          print(f"Image prompt time: {get_image_prompt_time(result):.2f}s")
  ```
- **Validate against 10-second target:**
  - Measure time to first image prompt
  - Ensure all agent outputs are present and correct
  - Verify no Ollama dependency remains
- **Monitor resource usage:**
  - GPU utilization during inference
  - Memory usage patterns
  - CPU utilization for non-GPU operations

### 8. Implement Advanced Optimizations for 10-Second Target
- **Model caching and warm-up:**
  ```python
  class ModelCache:
      def __init__(self):
          self.models = {}
          self.warm_models()
      
      def warm_models(self):
          # Pre-load models for each agent
          for agent in ["carthir", "narnion", "cenedril"]:
              self.models[agent] = self.load_optimized_model(agent)
  ```
- **Parallel agent execution optimization:**
  - Use your existing `PipelineInstance.run_parallel_agents()`
  - Optimize for concurrent GPU operations
  - Implement agent result streaming
- **Memory management for lean hardware:**
  - Implement model offloading if needed
  - Optimize memory allocation patterns
  - Monitor and prevent memory leaks

### 9. Document and Update Onboarding with Performance Guidelines
- **Update developer documentation:**
  - Hardware requirements and optimization tips
  - Performance tuning guidelines
  - Troubleshooting CUDA and memory issues
- **Create performance monitoring tools:**
  - Real-time performance dashboards
  - Resource usage alerts
  - Performance regression detection

---

## Performance Targets and Success Criteria

### Primary Goals
- **Image Generation Prompt**: ≤10 seconds from user submission
- **Total Pipeline Time**: ≤15 seconds for complete dream generation
- **GPU Utilization**: >80% during inference
- **Memory Efficiency**: <12GB VRAM usage for Q4 quantization

### Success Metrics
- Full pipeline runs locally (no Ollama dependency)
- All agent outputs (narrative, scenes, director vision, image prompt) are present and correct
- Performance is 50-70% better than previous Ollama-based setup
- GPU acceleration provides 2-3x speedup over CPU-only inference
- Documentation and onboarding are up to date with performance guidelines

### Hardware-Specific Considerations
- **Personal GPU Optimization**: Focus on efficient resource utilization
- **Memory Management**: Implement smart caching and offloading
- **Parallel Processing**: Leverage existing pipeline architecture
- **Performance Monitoring**: Real-time resource usage tracking

---

## References
- [Unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF on Hugging Face](https://huggingface.co/unsloth/Mistral-Small-3.2-24B-Instruct-2506-GGUF)
- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [llama-cpp-python PyPI](https://pypi.org/project/llama-cpp-python/)
- [CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/)
- [Mistral Model Documentation](https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506)
- [Performance Optimization Best Practices](https://github.com/ggerganov/llama.cpp/blob/master/README.md#performance-tuning) 