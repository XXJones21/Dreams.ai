# Integrating Meta Llama 3.1 Models for Local LLM Inference

## Executive Summary

**Goal:**
- Remove Ollama dependency and run all LLM inference locally using Meta's open source Llama 3.1 models.
- Enable fast, robust, and fully local agent reasoning with specialized models for each agent role.
- **Performance Target:** Achieve 10-second image generation prompt completion (currently at 22.43s).
- **Hardware Focus:** Optimize for personal GPU with lean resource utilization and model specialization.
- **Agent Specialization:** Use different Llama 3.1 models optimized for specific agent roles.
- Validation: A successful run through the full pipeline (CLI and web test suite) with all agent outputs present and no Ollama required.

---

## Step-by-Step Integration Plan

### 1. Download and Prepare the GGUF Models
- **Primary Models:**
  - **Llama 3.1 8B Instruct**: For Narnion (storyteller) and Cenedril (cinematographer) - speed-focused agents
  - **Llama 3.1 70B Instruct**: For Carthir (creative director) - reasoning-focused agent
  - **Llama 3.1 8B Vision**: For Narnion's image understanding capabilities
- **Download Sources:**
  - [TheBloke/Llama-3.1-8B-Instruct-GGUF](https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF)
  - [TheBloke/Llama-3.1-70B-Instruct-GGUF](https://huggingface.co/TheBloke/Llama-3.1-70B-Instruct-GGUF)
  - [TheBloke/Llama-3.1-8B-Vision-GGUF](https://huggingface.co/TheBloke/Llama-3.1-8B-Vision-GGUF)
- **Hardware Considerations:**
  - **Llama 3.1 8B Q4_K_M**: ~4-6GB VRAM (recommended for speed-focused agents)
  - **Llama 3.1 70B Q4_K_M**: ~16-20GB VRAM (for creative director role)
  - **Llama 3.1 8B Vision Q4_K_M**: ~4-6GB VRAM (for multimodal capabilities)

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
  
  # Test configuration for Llama 3.1 8B (speed-focused agents)
  llm_8b = Llama(
      model_path="models/llama-3.1-8b-instruct.Q4_K_M.gguf",
      n_gpu_layers=-1,        # Use all available GPU layers
      n_ctx=4096,             # Optimize context window for speed
      n_batch=512,            # Batch size optimized for your GPU
      n_threads=8,            # CPU threads for non-GPU operations
      use_mmap=True,          # Memory mapping for efficiency
      use_mlock=True,         # Lock memory in RAM
      verbose=False            # Reduce logging overhead
  )
  
  # Test configuration for Llama 3.1 70B (creative director)
  llm_70b = Llama(
      model_path="models/llama-3.1-70b-instruct.Q4_K_M.gguf",
      n_gpu_layers=-1,
      n_ctx=8192,             # Larger context for complex reasoning
      n_batch=256,            # Smaller batch for memory efficiency
      n_threads=8,
      use_mmap=True,
      use_mlock=True,
      verbose=False
  )
  
  # Test inference
  response_8b = llm_8b("Hello, world!", max_tokens=50)
  response_70b = llm_70b("Create a creative story concept", max_tokens=100)
  print(f"8B response: {response_8b}")
  print(f"70B response: {response_70b}")
  ```

### 3. Create Optimized LLM Integration Layer with Model Specialization
- **Design a performance-optimized LLM wrapper with agent-specific models:**
  ```python
  class OptimizedLLM:
      def __init__(self):
          self.model_instances = {}
          self.agent_configs = {
              "carthir": {
                  "model_path": "models/llama-3.1-70b-instruct.Q4_K_M.gguf",
                  "n_ctx": 8192,
                  "n_batch": 256,
                  "max_tokens": 512,
                  "temperature": 0.7
              },
              "narnion": {
                  "model_path": "models/llama-3.1-8b-instruct.Q4_K_M.gguf",
                  "n_ctx": 4096,
                  "n_batch": 512,
                  "max_tokens": 256,
                  "temperature": 0.8
              },
              "cenedril": {
                  "model_path": "models/llama-3.1-8b-instruct.Q4_K_M.gguf",
                  "n_ctx": 2048,
                  "n_batch": 512,
                  "max_tokens": 128,
                  "temperature": 0.6
              },
              "narnion_vision": {
                  "model_path": "models/llama-3.1-8b-vision.Q4_K_M.gguf",
                  "n_ctx": 4096,
                  "n_batch": 512,
                  "max_tokens": 128,
                  "temperature": 0.5
              }
          }
      
      def get_model_for_agent(self, agent_name: str):
          """Get or create model instance for specific agent"""
          if agent_name not in self.model_instances:
              config = self.agent_configs[agent_name]
              self.model_instances[agent_name] = Llama(
                  model_path=config["model_path"],
                  n_gpu_layers=-1,
                  n_ctx=config["n_ctx"],
                  n_batch=config["n_batch"],
                  n_threads=8,
                  use_mmap=True,
                  use_mlock=True,
                  verbose=False
              )
          return self.model_instances[agent_name]
      
      def invoke(self, agent_name: str, messages, **kwargs):
          """Invoke model with agent-specific settings"""
          llm = self.get_model_for_agent(agent_name)
          config = self.agent_configs[agent_name]
          
          # Merge agent config with kwargs
          params = {
              "max_tokens": config["max_tokens"],
              "temperature": config["temperature"],
              **kwargs
          }
          
          # Convert LangChain format to llama-cpp format
          prompt = self._format_messages(messages)
          response = llm(prompt, **params)
          return response
  ```
- **Implement model pooling for parallel agent execution:**
  - Keep model instances warm in memory
  - Share models across multiple agent threads
  - Optimize memory usage for concurrent operations

### 4. Prototype Agent Role-Based Prompting with Performance Monitoring
- **Design optimized prompt templates for each agent with Llama 3.1:**
  ```python
  # Optimized prompt templates for Llama 3.1 models
  AGENT_PROMPTS = {
      "carthir": {
          "system": "You are Carthir, a creative film director with exceptional storytelling vision. Generate concise, structured responses that establish compelling narrative foundations.",
          "max_tokens": 512,  # Limit for speed
          "temperature": 0.7
      },
      "narnion": {
          "system": "You are Narnion, a master storyteller who creates engaging, interactive scenes. Generate dynamic narrative content efficiently.",
          "max_tokens": 256,
          "temperature": 0.8
      },
      "cenedril": {
          "system": "You are Cenedril, a cinematographer who translates narrative vision into precise visual prompts. Generate concise, evocative visual descriptions.",
          "max_tokens": 128,  # Short for speed
          "temperature": 0.6
      },
      "narnion_vision": {
          "system": "You are Narnion analyzing visual content. Identify objects, actions, and narrative opportunities in images with precision.",
          "max_tokens": 128,
          "temperature": 0.5
      }
  }
  ```
- **Test role-based prompting with performance metrics:**
  - Measure inference time per agent
  - Monitor GPU utilization and memory usage
  - Validate output quality vs speed trade-offs
  - Compare Llama 3.1 performance vs previous models

### 5. Refactor Pipeline to Use Specialized Llama 3.1 Models
- **Replace Ollama API calls with optimized local inference:**
  ```python
  # Update agent functions to use specialized Llama 3.1 models
  def Carthir(state: State):
      # Use Llama 3.1 70B for creative director role
      llm = get_optimized_llm("carthir")
      response = llm.invoke("carthir", messages, max_tokens=512, temperature=0.7)
      # Process response and update state
      return state
  
  def Narnion(state: State):
      # Use Llama 3.1 8B for storyteller role
      llm = get_optimized_llm("narnion")
      response = llm.invoke("narnion", messages, max_tokens=256, temperature=0.8)
      # Process response and update state
      return state
  
  def Cenedril(state: State):
      # Use Llama 3.1 8B for cinematographer role
      llm = get_optimized_llm("cenedril")
      response = llm.invoke("cenedril", messages, max_tokens=128, temperature=0.6)
      # Process response and update state
      return state
  
  def NarnionVision(image_data, state: State):
      # Use Llama 3.1 8B Vision for image understanding
      llm = get_optimized_llm("narnion_vision")
      response = llm.invoke("narnion_vision", messages, max_tokens=128, temperature=0.5)
      # Process visual analysis and update state
      return state
  ```
- **Implement parallel agent execution with shared models:**
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
- **Profile and optimize for your specific GPU with Llama 3.1:**
  ```python
  # Performance profiling script for Llama 3.1 models
  def profile_llama_models_performance():
      configs = {
          "llama-3.1-8b": [
              {"n_gpu_layers": -1, "n_batch": 512, "n_ctx": 4096},
              {"n_gpu_layers": -1, "n_batch": 1024, "n_ctx": 2048},
              {"n_gpu_layers": -1, "n_batch": 256, "n_ctx": 8192}
          ],
          "llama-3.1-70b": [
              {"n_gpu_layers": -1, "n_batch": 256, "n_ctx": 8192},
              {"n_gpu_layers": -1, "n_batch": 128, "n_ctx": 4096},
              {"n_gpu_layers": -1, "n_batch": 512, "n_ctx": 2048}
          ]
      }
      
      for model_name, model_configs in configs.items():
          for config in model_configs:
              start_time = time.time()
              # Test inference with config
              # Measure tokens/second and memory usage
              print(f"{model_name} Config {config}: {tokens_per_second} tokens/s")
  ```
- **Experiment with different quantization levels for Llama 3.1:**
  - Test Q4_K_M, Q5_K_M, Q8_K_M for your hardware
  - Measure speed vs quality trade-offs
  - Choose optimal quantization for your 10-second target
- **Optimize context windows and batch sizes for each model:**
  - Smaller contexts for faster inference (8B models)
  - Larger contexts for complex reasoning (70B model)
  - Optimal batch sizes for your GPU memory

### 7. Test and Validate with Performance Benchmarks
- **Run comprehensive performance tests with Llama 3.1:**
  ```python
  def benchmark_llama_pipeline_performance():
      test_prompts = [
          "A magical forest adventure",
          "A space exploration mission", 
          "A detective solving a mystery"
      ]
      
      for prompt in test_prompts:
          start_time = time.time()
          result = run_full_pipeline_with_llama(prompt)
          end_time = time.time()
          
          print(f"Prompt: {prompt}")
          print(f"Total time: {end_time - start_time:.2f}s")
          print(f"Image prompt time: {get_image_prompt_time(result):.2f}s")
          print(f"Model usage: {get_model_usage_stats(result)}")
  ```
- **Validate against 10-second target:**
  - Measure time to first image prompt
  - Ensure all agent outputs are present and correct
  - Verify no Ollama dependency remains
  - Compare performance vs previous Mistral setup
- **Monitor resource usage:**
  - GPU utilization during inference
  - Memory usage patterns for different models
  - CPU utilization for non-GPU operations

### 8. Implement Advanced Optimizations for 10-Second Target
- **Model caching and warm-up for Llama 3.1:**
  ```python
  class LlamaModelCache:
      def __init__(self):
          self.models = {}
          self.warm_models()
      
      def warm_models(self):
          # Pre-load Llama 3.1 models for each agent
          agent_models = {
              "carthir": "llama-3.1-70b-instruct",
              "narnion": "llama-3.1-8b-instruct", 
              "cenedril": "llama-3.1-8b-instruct",
              "narnion_vision": "llama-3.1-8b-vision"
          }
          
          for agent, model_name in agent_models.items():
              self.models[agent] = self.load_optimized_llama_model(agent, model_name)
  ```
- **Parallel agent execution optimization:**
  - Use your existing `PipelineInstance.run_parallel_agents()`
  - Optimize for concurrent GPU operations with different models
  - Implement agent result streaming
- **Memory management for lean hardware:**
  - Implement model offloading if needed
  - Optimize memory allocation patterns for Llama 3.1
  - Monitor and prevent memory leaks

### 9. Document and Update Onboarding with Performance Guidelines
- **Update developer documentation:**
  - Hardware requirements and optimization tips for Llama 3.1
  - Performance tuning guidelines for different model sizes
  - Troubleshooting CUDA and memory issues
- **Create performance monitoring tools:**
  - Real-time performance dashboards
  - Resource usage alerts
  - Performance regression detection
- **Model comparison documentation:**
  - Llama 3.1 vs previous models performance metrics
  - Agent-specific model recommendations
  - Hardware requirements for different model combinations

---

## Performance Targets and Success Criteria

### Primary Goals
- **Image Generation Prompt**: ≤10 seconds from user submission
- **Total Pipeline Time**: ≤15 seconds for complete dream generation
- **GPU Utilization**: >80% during inference
- **Memory Efficiency**: <20GB VRAM usage for Llama 3.1 70B + 8B combination

### Success Metrics
- Full pipeline runs locally (no Ollama dependency)
- All agent outputs (narrative, scenes, director vision, image prompt) are present and correct
- Performance is 50-70% better than previous Ollama-based setup
- Llama 3.1 models provide superior quality vs previous models
- GPU acceleration provides 2-3x speedup over CPU-only inference
- Documentation and onboarding are up to date with Llama 3.1 guidelines

### Hardware-Specific Considerations
- **Personal GPU Optimization**: Focus on efficient resource utilization with model specialization
- **Memory Management**: Implement smart caching and offloading for different model sizes
- **Parallel Processing**: Leverage existing pipeline architecture with specialized models
- **Performance Monitoring**: Real-time resource usage tracking for multiple models

---

## References
- [TheBloke/Llama-3.1-8B-Instruct-GGUF on Hugging Face](https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF)
- [TheBloke/Llama-3.1-70B-Instruct-GGUF on Hugging Face](https://huggingface.co/TheBloke/Llama-3.1-70B-Instruct-GGUF)
- [TheBloke/Llama-3.1-8B-Vision-GGUF on Hugging Face](https://huggingface.co/TheBloke/Llama-3.1-8B-Vision-GGUF)
- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [llama-cpp-python PyPI](https://pypi.org/project/llama-cpp-python/)
- [CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/)
- [Meta Llama 3.1 Documentation](https://ai.meta.com/llama/)
- [Performance Optimization Best Practices](https://github.com/ggerganov/llama.cpp/blob/master/README.md#performance-tuning) 