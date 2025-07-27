# Dreams.ai Development Workflow

## High-Performance Development Process

### Morning Routine (20 minutes)
1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Check Performance System Status**
   ```bash
   # Check CUDA availability
   nvidia-smi
   
   # Verify model loading
   cd Backend/Python
   python -c "from core.agents import llm; print('GGUF model loaded with CUDA acceleration')"
   
   # Run comprehensive test suite
   python test_pipeline.py
   ```

3. **Review Agent Pipeline Performance**
   - Check CUDA utilization in console output
   - Monitor response times and thread allocation
   - Review recent .imn file generations
   - Verify performance optimizations are active

4. **Launch Test Suite Interface**
   ```bash
   # Start GUI test suite for visual monitoring
   start_gui_test.bat  # Windows
   start_gui_test.ps1  # PowerShell
   # Access: http://localhost:5000
   ```

### Development Session

#### 1. Performance-Focused Feature Development
- **Agent Enhancements**: Work on GGUF-optimized agent improvements
- **New Features**: Implement with CUDA acceleration in mind
- **Performance Optimization**: Improve response times and resource usage
- **Bug Fixes**: Address performance and functionality issues
- **Documentation**: Update performance-related documentation

#### 2. Enhanced Testing Strategy
- **GUI Test Suite**: Use visual interface for comprehensive testing
- **Performance Tests**: Monitor CUDA utilization and response times
- **Unit Tests**: Test individual agent functions with performance metrics
- **Integration Tests**: Test full pipeline with concurrent requests
- **Manual Testing**: Test with sample prompts and monitor GPU usage
- **Regression Testing**: Ensure performance optimizations don't break functionality

#### 3. Code Quality with Performance Considerations
- **Performance Review**: Profile CUDA usage and memory consumption
- **Documentation**: Update performance-related comments and docs
- **Error Handling**: Ensure robust fallbacks for CUDA and threading issues
- **Resource Management**: Monitor GPU memory and thread efficiency

### Evening Routine (15 minutes)
1. **Performance Validation**
   ```bash
   # Run performance benchmarks
   cd Backend/Python
   python test_pipeline.py  # Check all tests pass
   
   # Monitor resource usage
   nvidia-smi  # Check GPU status
   ```

2. **Commit Changes with Performance Notes**
   ```bash
   git add .
   git commit -m "feat(performance): descriptive commit message with CUDA/performance notes"
   ```

3. **Update Documentation**
   - Update performance-related documentation
   - Note any CUDA or threading optimizations
   - Document performance improvements or regressions

4. **Plan Next Session**
   - Review performance metrics and bottlenecks
   - Prioritize performance optimization tasks
   - Update project status with performance considerations

## Common Development Tasks (Performance-Optimized)

### Adding a New Agent (GGUF-Optimized)

1. **Create Agent Function in `core/agents.py`**
   ```python
   def NewAgent(state: State):
       """
       New agent description and responsibilities.
       Optimized for GGUF/CUDA performance.
       """
       # Use centralized, robust JSON parsing
       try:
           reply = llm.invoke(agent_prompt)
           parsed_data = parse_new_agent_response(reply.content)
           
           if parsed_data:
               # Successfully parsed - store in .imn with file locking
               dream_id = state.get("id")
               imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
               
               with get_imn_filelock(imn_file_path):
                   imn_data = read_imn(imn_file_path)
                   # Update IMN structure
                   write_imn(imn_data, directory)
               
               return state
           else:
               # Failed to parse - use intelligent fallback
               return handle_parsing_failure(state)
               
       except Exception as e:
           print(f"[NewAgent] Error: {e}")
           return handle_agent_error(state)
   ```

2. **Add to LangGraph Workflow in `main.py`**
   ```python
   graph_builder.add_node("new_agent", NewAgent)
   graph_builder.add_edge("previous_agent", "new_agent")
   graph_builder.add_edge("new_agent", "next_agent")
   ```

3. **Implement Parsing Function in `core/imn_utils.py`**
   ```python
   def parse_new_agent_response(content):
       """Robust JSON parsing with intelligent fallbacks."""
       try:
           # Clean content and extract JSON
           cleaned_content = clean_json_content(content)
           parsed_data = json.loads(cleaned_content)
           return validate_agent_response(parsed_data)
       except Exception as e:
           print(f"[parse_new_agent_response] Parsing failed: {e}")
           return None
   ```

4. **Test with Performance Monitoring**
   ```bash
   # Monitor GPU usage during testing
   nvidia-smi -l 1 &
   
   # Run comprehensive tests
   python test_pipeline.py
   
   # Stop monitoring
   killall nvidia-smi
   ```

### Modifying .imn Schema (Thread-Safe)

1. **Update Schema Documentation**
   - Edit relevant documentation files
   - Document new fields and their purposes
   - Include thread-safety considerations

2. **Update Utility Functions with File Locking**
   ```python
   # In core/imn_utils.py
   def create_imn_structure(...):
       """Enhanced IMN structure creation with new fields."""
       # Add new fields to structure with proper defaults
       return enhanced_structure
   
   def update_imn_with_locking(imn_file_path, update_func):
       """Thread-safe IMN file updates."""
       with get_imn_filelock(imn_file_path):
           imn_data = read_imn(imn_file_path)
           updated_data = update_func(imn_data)
           write_imn(updated_data, os.path.dirname(imn_file_path))
   ```

3. **Update Agent Functions with Thread Safety**
   - Modify agents to handle new fields
   - Add validation for new data
   - Implement file locking for all .imn operations

4. **Test Schema Changes with Concurrency**
   ```bash
   # Test with multiple concurrent requests
   python test_gui.py  # GUI test suite handles concurrency
   
   # Verify thread safety
   python -c "
   import threading
   from test_pipeline import test_concurrent_dreams
   test_concurrent_dreams(num_threads=5)
   "
   ```

### Debugging Agent Issues (Performance-Aware)

1. **Check Console Output for Performance Metrics**
   - Look for CUDA status messages
   - Check thread allocation reports
   - Monitor GPU utilization logs
   - Verify model loading times

2. **Validate .imn Files with Performance Monitoring**
   ```python
   from core.imn_utils import validate_imn_structure, read_imn
   import time
   
   start_time = time.time()
   imn_data = read_imn("path/to/file.imn")
   load_time = time.time() - start_time
   
   if validate_imn_structure(imn_data):
       print(f"File structure is valid (loaded in {load_time:.3f}s)")
   ```

3. **Test Individual Agents with Performance Profiling**
   ```python
   import time
   import psutil
   import GPUtil
   
   # Monitor resources before agent execution
   gpu_before = GPUtil.getGPUs()[0].memoryUsed if GPUtil.getGPUs() else 0
   cpu_before = psutil.cpu_percent()
   
   # Test specific agent
   start_time = time.time()
   result = AgentFunction(test_state)
   execution_time = time.time() - start_time
   
   # Monitor resources after
   gpu_after = GPUtil.getGPUs()[0].memoryUsed if GPUtil.getGPUs() else 0
   cpu_after = psutil.cpu_percent()
   
   print(f"Execution time: {execution_time:.2f}s")
   print(f"GPU memory used: {gpu_after - gpu_before}MB")
   print(f"CPU usage: {cpu_after}%")
   ```

4. **Check LangGraph State with Performance Context**
   - Verify state transitions don't cause memory leaks
   - Check message flow efficiency
   - Validate data persistence performance

### Performance Optimization Workflow

1. **Profile Current Performance**
   ```bash
   # Monitor GPU utilization
   nvidia-smi dmon -s u -d 1
   
   # Profile Python execution
   python -m cProfile -o profile_output.prof test_pipeline.py
   
   # Analyze profile
   python -c "
   import pstats
   p = pstats.Stats('profile_output.prof')
   p.sort_stats('cumulative').print_stats(20)
   "
   ```

2. **Optimize GGUF Model Parameters**
   ```python
   # In core/agents.py - experiment with parameters
   llm = ChatLlamaCpp(
       model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
       n_gpu_layers=35,      # Adjust based on GPU memory
       n_threads=optimal_threads,  # Tune for your CPU
       n_batch=512,          # Optimize for GPU throughput
       n_ctx=2048,          # Balance context vs speed
       # Add other optimizations
   )
   ```

3. **Implement Caching Strategies**
   ```python
   # Cache frequently used prompts and responses
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def cached_llm_call(prompt_hash):
       """Cache LLM responses for identical prompts."""
       return llm.invoke(prompt)
   ```

4. **Benchmark Changes**
   ```bash
   # Before and after performance comparison
   python test_pipeline.py --benchmark
   
   # Continuous performance monitoring
   start_gui_test.bat  # Visual performance tracking
   ```

## Enhanced Testing Guidelines

### Performance Testing
- **GPU Utilization**: Monitor CUDA usage during tests
- **Memory Management**: Track VRAM and RAM consumption
- **Response Times**: Benchmark agent execution speeds
- **Concurrent Testing**: Verify thread safety and performance under load

### GUI Test Suite Integration
```bash
# Primary testing interface
start_gui_test.bat  # Windows
start_gui_test.ps1  # PowerShell

# Features:
# - Visual dream cards with performance metrics
# - Real-time pipeline execution monitoring
# - Automatic image generation testing
# - Performance benchmarking tools
# - Test history and analytics
```

### Comprehensive Test Coverage
```bash
# Run all test types
cd Backend/Python

# 1. GUI Test Suite (Recommended)
start_gui_test.bat  # Visual interface at http://localhost:5000

# 2. CLI Test Suite
python test_pipeline.py  # Comprehensive automated tests

# 3. Simple API Testing
python test_gui_simple.py  # Quick API validation

# 4. Interactive Testing
python main.py  # Manual prompt testing

# 5. Performance Benchmarking
python -c "
from test_pipeline import benchmark_performance
benchmark_performance(num_iterations=10)
"
```

### Test Data Management (Performance-Aware)
```python
# Sample test prompts optimized for performance testing
PERFORMANCE_TEST_PROMPTS = [
    "A corgi taking a nap on a sunny beach",  # Simple, fast generation
    "A magical forest adventure with talking animals",  # Medium complexity
    "A space exploration mission to discover new worlds",  # Complex scenario
    "A detective solving a mystery in a cyberpunk city"  # High complexity
]

CONCURRENT_TEST_PROMPTS = [
    "Quick dream test 1",
    "Quick dream test 2", 
    "Quick dream test 3",
    "Quick dream test 4",
    "Quick dream test 5"
]
```

## Code Quality Standards (Performance-Enhanced)

### Python Code Style with Performance
- Follow PEP 8 guidelines with performance annotations
- Use type hints for all functions, especially performance-critical ones
- Write comprehensive docstrings including performance notes
- Keep functions focused, small, and optimized

### Performance-Aware Error Handling
```python
try:
    # Main logic with performance monitoring
    start_time = time.time()
    result = process_data_with_cuda(data)
    execution_time = time.time() - start_time
    
    if execution_time > PERFORMANCE_THRESHOLD:
        logger.warning(f"Slow execution detected: {execution_time:.2f}s")
    
except CudaException as e:
    # Handle CUDA-specific errors
    logger.error(f"CUDA error: {e}")
    return fallback_cpu_processing(data)
except ThreadingException as e:
    # Handle threading errors
    logger.error(f"Threading error: {e}")
    return single_threaded_fallback(data)
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
    return None
```

### Documentation with Performance Context
- Update docstrings with performance characteristics
- Document CUDA requirements and optimizations
- Maintain performance-focused README sections
- Comment on performance-critical code sections

```python
def optimized_agent_function(state: State):
    """
    High-performance agent function optimized for GGUF/CUDA.
    
    Performance characteristics:
    - Typical execution: 2-5 seconds with CUDA
    - Memory usage: ~500MB VRAM
    - Thread safety: Uses file locking
    - Fallback: CPU processing if CUDA unavailable
    
    Args:
        state: LangGraph state with agent communication
        
    Returns:
        Updated state with agent results
        
    Raises:
        CudaException: If GPU processing fails
        FileSystemException: If IMN file operations fail
    """
    pass
```

## Git Workflow (Performance-Focused)

### Branch Strategy with Performance Tracking
- `main`: Production-ready code with performance validation
- `develop`: Integration branch with performance testing
- `feature/*`: New features with performance benchmarks
- `performance/*`: Performance optimization branches
- `bugfix/*`: Bug fixes including performance issues
- `hotfix/*`: Critical fixes including performance regressions

### Enhanced Commit Messages
```
type(scope): description [performance impact]

feat(agent): add CUDA-optimized Carthir memory persistence [+40% speed]
fix(pipeline): resolve JSON parsing error causing GPU memory leak [-memory leak]
perf(gguf): optimize thread allocation for Flask environment [+25% throughput]
docs(readme): update CUDA installation instructions [no performance impact]
test(pipeline): add concurrent testing suite [improved test coverage]
```

### Pull Request Process with Performance Validation
1. Create feature branch with performance baseline
2. Implement changes with performance monitoring
3. Write/update tests including performance tests
4. Benchmark performance changes
5. Update documentation with performance notes
6. Create pull request with performance metrics
7. Code review including performance assessment
8. Merge to develop after performance validation

## Environment Management (Performance-Optimized)

### Local Development Setup with CUDA
```bash
# Backend with CUDA support
cd Backend/Python
pip install -r requirements.txt  # Includes llama-cpp-python with CUDA

# Verify CUDA installation
python -c "
from llama_cpp import Llama
import llama_cpp
print(f'llama-cpp-python version: {llama_cpp.__version__}')
print('CUDA support: Available' if llama_cpp.llama_supports_gpu_offload() else 'Not available')
"

# Start with performance monitoring
python api_server.py  # Check console for CUDA status

# Frontend
npm install
npm run dev

# Test Suite
start_gui_test.bat  # Performance monitoring interface
```

### Environment Variables (Performance-Enhanced)
```bash
# .env file with performance settings
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-anon-key

# CUDA settings (optional)
CUDA_VISIBLE_DEVICES=0  # Use specific GPU
CUDA_LAUNCH_BLOCKING=1  # For debugging

# Performance tuning
GGUF_MAX_THREADS=16     # Override thread detection
GGUF_GPU_LAYERS=35      # Override GPU layer count
```

### Dependencies Management (Performance-Focused)
```bash
# Update Python dependencies with CUDA support
pip install --upgrade llama-cpp-python[cuda]
pip install --upgrade torch  # If using PyTorch
pip freeze > requirements.txt

# Verify CUDA support after updates
python -c "from core.agents import llm; print('CUDA test passed')"

# Update Node.js dependencies
npm update package-name
npm audit fix
```

## Monitoring and Logging (Performance-Enhanced)

### Performance Logging Strategy
```python
import logging
import time
import psutil
import GPUtil

# Configure performance logger
perf_logger = logging.getLogger('performance')
perf_logger.setLevel(logging.INFO)

def log_performance_metrics(func_name, start_time, end_time):
    """Log comprehensive performance metrics."""
    execution_time = end_time - start_time
    cpu_percent = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    
    gpu_info = "N/A"
    if GPUtil.getGPUs():
        gpu = GPUtil.getGPUs()[0]
        gpu_info = f"{gpu.memoryUsed}MB/{gpu.memoryTotal}MB ({gpu.load*100:.1f}%)"
    
    perf_logger.info(f"[{func_name}] Time: {execution_time:.2f}s, CPU: {cpu_percent}%, Memory: {memory_info.percent}%, GPU: {gpu_info}")

# Usage in agent functions
def monitored_agent_function(state: State):
    start_time = time.time()
    
    try:
        result = agent_logic(state)
        end_time = time.time()
        log_performance_metrics("agent_function", start_time, end_time)
        return result
    except Exception as e:
        end_time = time.time()
        log_performance_metrics("agent_function_ERROR", start_time, end_time)
        raise
```

### Real-Time Performance Monitoring
```bash
# Monitor GPU usage continuously
nvidia-smi dmon -s puct -d 1

# Monitor system resources
htop  # Linux/macOS
# Task Manager > Performance tab  # Windows

# Monitor API performance
curl -w "Time: %{time_total}s, Size: %{size_download}bytes\n" \
     http://localhost:8000/api/dream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "test prompt"}'
```

### Health Checks with Performance Metrics
```python
def comprehensive_health_check():
    """Check system health including performance metrics."""
    checks = {
        "cuda_available": check_cuda_availability(),
        "model_loaded": check_model_loading_time(),
        "gpu_memory": check_gpu_memory_usage(),
        "thread_allocation": check_thread_optimization(),
        "file_system": check_file_performance(),
        "database": check_database_performance(),
        "agent_pipeline": benchmark_pipeline_performance()
    }
    
    # Log performance summary
    perf_summary = {
        "overall_health": all(checks.values()),
        "performance_score": calculate_performance_score(checks),
        "recommendations": generate_performance_recommendations(checks)
    }
    
    return checks, perf_summary
```

## Troubleshooting Guide (Performance-Enhanced)

### Common Performance Issues

#### CUDA Not Available or Underutilized
```bash
# Check CUDA installation
nvidia-smi
nvcc --version

# Verify llama-cpp-python CUDA support
python -c "
import llama_cpp
print('CUDA support:', llama_cpp.llama_supports_gpu_offload())
print('Available backends:', llama_cpp.llama_print_system_info())
"

# Reinstall with CUDA if needed
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --no-cache-dir
```

#### Slow Response Times
```bash
# Monitor GPU utilization
nvidia-smi -l 1

# Check thread allocation
python -c "
from core.agents import optimal_threads
print(f'Optimal threads: {optimal_threads}')
print(f'CPU count: {os.cpu_count()}')
"

# Profile memory usage
python -m memory_profiler test_pipeline.py
```

#### Memory Issues (GPU/RAM)
```bash
# Check GPU memory
nvidia-smi --query-gpu=memory.used,memory.total --format=csv

# Monitor Python memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f}MB')
"

# Optimize model parameters if needed
# Reduce n_ctx, n_gpu_layers, or n_batch in agents.py
```

#### Thread Contention
```bash
# Monitor thread usage
htop  # Look for high CPU usage across threads

# Check file locking behavior
lsof Backend/Python/Dreams/  # Linux/macOS
# Check for locked .imn files

# Verify thread-safe operations
python test_concurrent_access.py
```

### Performance Debug Mode
```python
# Enable comprehensive performance logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add performance profiling
import cProfile
import pstats

def profile_agent_execution():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run agent pipeline
    result = run_pipeline()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(20)
    return result
```

## Best Practices (Performance-Optimized)

### Code Organization with Performance
- Keep performance-critical functions in `core/agents.py`
- Separate CUDA-dependent code from fallback implementations
- Use clear, descriptive names with performance indicators
- Group related performance optimizations together
- Maintain consistent file structure for optimal loading

### Error Recovery with Performance Considerations
- Implement graceful degradation from CUDA to CPU
- Provide meaningful error messages with performance context
- Use intelligent fallback mechanisms that maintain acceptable performance
- Log performance regressions for debugging

### Resource Management
- Monitor GPU memory usage continuously
- Optimize thread allocation based on environment
- Use efficient data structures for IMN operations
- Cache frequently accessed model outputs
- Implement proper cleanup for GPU resources

### Security with Performance
- Validate all inputs without sacrificing speed
- Sanitize user data efficiently
- Use secure authentication with performance caching
- Implement proper authorization with minimal overhead

### Development Environment Optimization
```bash
# IDE/Editor settings for performance development
# - Enable CUDA syntax highlighting
# - Configure performance profiling tools
# - Set up resource monitoring dashboards
# - Use GPU memory usage plugins

# Recommended development tools
pip install nvidia-ml-py3  # GPU monitoring in Python
pip install memory-profiler  # Memory usage profiling
pip install line-profiler   # Line-by-line profiling
```

---

*This workflow guide emphasizes performance optimization and should be updated as CUDA/GGUF optimizations evolve.* 