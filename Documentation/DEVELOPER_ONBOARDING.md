# Dreams.ai Developer Onboarding

Welcome to Dreams.ai! This guide will help you get up and running quickly with our high-performance AI storytelling platform.

## Quick Start (10 minutes)

### Prerequisites
- **Python 3.13+** (required for the backend)
- **Node.js 18+** (required for the frontend)
- **Git** (for version control)
- **CUDA-compatible GPU** (recommended for optimal performance)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Dreams.ai
```

### 2. Frontend Setup
```bash
npm install
```

### 3. Backend Setup
```bash
cd Backend/Python
pip install -r requirements.txt
```

### 4. GGUF Model Setup
Download and place the GGUF model in the models directory:
```bash
# Create models directory if it doesn't exist
mkdir -p Backend/Python/models

# Place your GGUF model file
# Expected location: Backend/Python/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

### 5. Start the Services
```bash
# Terminal 1: Start the backend (with CUDA acceleration)
cd Backend/Python
python api_server.py

# Terminal 2: Start the frontend
npm run dev
```

### 6. Verify Installation
- Backend should be running on `http://localhost:8000`
- Frontend should be running on `http://localhost:5173`
- Check the API docs at `http://localhost:8000/docs`
- Monitor CUDA status in console output

### 7. Run Test Suite
```bash
# Quick test with GUI interface (Recommended)
start_gui_test.bat  # Windows
start_gui_test.ps1  # PowerShell

# Or run comprehensive tests
cd Backend/Python
python test_pipeline.py
```

---

## 🚀 Performance Architecture Overview

### High-Performance Features
- **GGUF Model Integration**: Meta-Llama-3.1-8B with Q4_K_M quantization
- **CUDA Acceleration**: 35 GPU layers offloaded for maximum performance
- **Dynamic Threading**: Environment-aware thread allocation (8-16 threads)
- **Memory Optimization**: Half-precision caching and memory mapping
- **Thread-Safe Operations**: File locking for concurrent .imn access

### Technology Stack

#### Backend Performance Stack
- **FastAPI**: High-performance async web framework
- **LangGraph**: Agent orchestration with state management
- **LangChain Community**: Optimized LLM implementations
- **llama-cpp-python**: GGUF model loading with CUDA support
- **filelock**: Thread-safe file operations
- **psutil**: System resource monitoring

#### Frontend
- **React 18**: UI framework with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Lightning-fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Supabase Client**: Real-time database integration

#### AI/ML Performance Stack
- **GGUF Models**: Quantized model format for optimal performance
- **CUDA Acceleration**: GPU processing with layer offloading
- **Dynamic Threading**: Environment-aware performance tuning
- **Memory Mapping**: Faster model loading with reduced memory usage

---

## 🧪 Comprehensive Testing Infrastructure

Dreams.ai includes multiple testing layers for quality assurance:

### GUI Test Suite (Primary)
**Quick Access:**
```bash
# From project root (Windows)
start_gui_test.bat          # Windows Batch launcher
start_gui_test.ps1          # PowerShell launcher

# From Backend/Python directory
start_gui_test.bat          # Local batch launcher
start_gui_test.ps1          # Local PowerShell launcher
```

**Features:**
- **Visual Interface**: `http://localhost:5000`
- **Dream Cards**: Frontend-like interface showing generated dreams
- **Real-time Testing**: Live pipeline execution with status updates
- **Image Generation**: Automatic visual content creation
- **Performance Monitoring**: Response time and resource tracking
- **Test History**: Complete test result tracking

### Automated Test Pipeline
```bash
cd Backend/Python
python test_pipeline.py
```

**Coverage:**
- IMN utility functions and file operations
- Individual agent function validation
- Complete pipeline execution testing
- Error handling and fallback mechanisms
- Performance benchmarking with CUDA

### Simple API Testing
```bash
cd Backend/Python
python test_gui_simple.py
```

### Interactive Pipeline Testing
```bash
cd Backend/Python
python main.py
# Enter custom prompts for live testing
```

---

## 🏗️ Enhanced Architecture Overview

### AI Agent Network (GGUF-Optimized)

#### **Carthir (Creative Director)**
- **Role**: Creative vision and initial story architecture
- **Input**: User's initial prompt
- **Output**: Creative pitch, story structure, and initial .imn file
- **Key Functions**: `Carthir()`, `convert_prompt_to_imn()`
- **Performance**: GGUF-optimized with CUDA acceleration
- **Features**: Robust JSON parsing with intelligent fallbacks

#### **Narnion (Storyteller)**
- **Role**: Interactive scene generation and narrative progression
- **Input**: .imn file from Carthir
- **Output**: Interactive scenes with user choices
- **Key Functions**: `Narnion()`
- **Features**: Real-time scene generation with error recovery
- **Performance**: Centralized JSON parsing with fallbacks

#### **CarthirReview (Director's Vision)**
- **Role**: Creative consistency and visual direction
- **Input**: Scene context from Narnion
- **Output**: Visual direction and image prompts
- **Key Functions**: `CarthirReview()`
- **Features**: Persistent memory and intelligent fallbacks
- **Performance**: Optimized vision parsing with error handling

#### **Cenedril (Cinematographer)**
- **Role**: Visual prompt generation for media creation
- **Input**: Director's vision from CarthirReview
- **Output**: Final visual prompts for image/video generation
- **Key Functions**: `Cenedril()`
- **Features**: File locking and atomic operations for consistency
- **Performance**: Thread-safe operations with atomic file updates

### Data Flow (Performance-Optimized)
```
User Prompt
    ↓
Carthir [GGUF/CUDA Optimized]
    ↓
convert_prompt_to_imn [Thread-Safe File Operations]
    ↓
Narnion [Parallel Processing Ready]
    ↓
CarthirReview [Persistent Memory]
    ↓
Cenedril [Atomic Operations]
    ↓
Final Output [Performance Metrics Logged]
```

### Enhanced File Structure
```
Dreams.ai/
├── Backend/
│   ├── Python/
│   │   ├── agents/              # AI agent implementations
│   │   ├── core/                # Optimized core utilities
│   │   │   ├── agents.py        # GGUF/CUDA agent definitions
│   │   │   ├── imn_utils.py     # Thread-safe .imn operations
│   │   │   ├── image_generator.py # Image generation utilities
│   │   │   └── pipeline_instance.py # Pipeline management
│   │   ├── api/                 # High-performance FastAPI routes
│   │   │   └── dream_routes.py  # Optimized dream endpoints
│   │   ├── Dreams/              # Generated .imn files
│   │   ├── models/              # GGUF model storage
│   │   │   └── Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
│   │   ├── main.py              # LangGraph pipeline with monitoring
│   │   ├── api_server.py        # FastAPI server with optimization
│   │   ├── test_pipeline.py     # Comprehensive test suite
│   │   ├── test_gui.py          # GUI test interface
│   │   └── test_gui_simple.py   # Simple API testing
│   └── Scoping/                 # Project documentation
├── Documentation/               # Technical documentation
│   ├── TECHNICAL_ARCHITECTURE.md # System architecture
│   ├── API_DOCUMENTATION.md     # API reference
│   ├── DEVELOPMENT_WORKFLOW.md  # Development guidelines
│   └── ProjectPlanning/         # Project planning
│       └── PERFORMANCE_OPTIMIZATION_PLAN.md # Performance strategies
├── src/                         # React frontend with TypeScript
├── supabase/                    # Database migrations
├── start_gui_test.bat           # Test suite launcher (Windows)
├── start_gui_test.ps1           # Test suite launcher (PowerShell)
└── README.md
```

---

## 🔧 Key Files to Know

### Backend Core
- `Backend/Python/core/agents.py` - **GGUF/CUDA optimized agent definitions**
- `Backend/Python/main.py` - LangGraph agent pipeline (the heart of the system)
- `Backend/Python/api_server.py` - FastAPI server entry point
- `Backend/Python/core/imn_utils.py` - Thread-safe .imn file operations
- `Backend/Python/api/dream_routes.py` - High-performance API endpoints

### Testing Infrastructure
- `Backend/Python/test_pipeline.py` - Comprehensive test suite
- `Backend/Python/test_gui.py` - GUI test interface with image generation
- `Backend/Python/test_gui_simple.py` - Simple API validation
- `start_gui_test.bat` / `start_gui_test.ps1` - Test suite launchers

### Frontend
- `src/App.tsx` - Main React application
- `src/components/` - UI components organized by feature
- `src/utils/supabase.ts` - Supabase client configuration

### Documentation & Configuration
- `Documentation/TECHNICAL_ARCHITECTURE.md` - Complete system architecture
- `Documentation/API_DOCUMENTATION.md` - API reference with performance details
- `Backend/Scoping/` - Comprehensive project documentation
- `Backend/Python/requirements.txt` - Python dependencies with performance packages

---

## ⚡ Performance Configuration

### GGUF Model Configuration
The system uses optimized GGUF models for maximum performance:

```python
# Located in Backend/Python/core/agents.py
llm = ChatLlamaCpp(
    model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=1024,      # Optimized for speed
    top_p=0.9,
    verbose=True,         # Enable CUDA status monitoring
    n_ctx=2048,          # Reduced context for faster processing
    n_threads=optimal_threads,  # Dynamic 8-16 threads
    n_batch=512,         # GPU-optimized batch size
    use_mmap=True,       # Memory mapping for faster loading
    use_mlock=False,     # OS memory management
    f16_kv=True,         # Half precision key-value cache
    n_gpu_layers=35,     # Maximum GPU layer offloading
)
```

### Environment Detection
The system automatically optimizes based on runtime:

```python
# Detects Flask server vs CLI environment
is_flask_server = threading.active_count() > 1 or os.environ.get('FLASK_RUN_PORT') is not None

if is_flask_server:
    # Conservative threading for Flask server
    optimal_threads = min(8, os.cpu_count() // 2)
else:
    # Aggressive threading for CLI/standalone
    optimal_threads = min(16, os.cpu_count())
```

### Performance Monitoring
Monitor system performance during development:
- **CUDA Status**: Check console output for GPU utilization
- **Thread Allocation**: Monitor optimal thread selection
- **Memory Usage**: Track RAM and VRAM consumption
- **Response Times**: Monitor dream generation speed

---

## Understanding the Agent Workflow

### Agent Responsibilities (Enhanced)

#### Carthir (Creative Director)
- **Input**: User's initial prompt
- **Output**: Creative vision, story structure, and initial .imn file
- **Key Functions**: `Carthir()`, `convert_prompt_to_imn()`
- **Performance Features**: CUDA acceleration, robust JSON parsing
- **Error Handling**: Intelligent fallbacks when LLM parsing fails

#### Narnion (Storyteller)
- **Input**: .imn file from Carthir
- **Output**: Interactive scenes with user choices
- **Key Functions**: `Narnion()`
- **Performance Features**: Centralized JSON parsing, error recovery
- **Thread Safety**: File locking for concurrent .imn access

#### CarthirReview (Director's Vision)
- **Input**: Scene context from Narnion
- **Output**: Visual direction and image prompts
- **Key Functions**: `CarthirReview()`
- **Performance Features**: Persistent memory, intelligent fallbacks
- **Visual Processing**: Enhanced director vision parsing

#### Cenedril (Cinematographer)
- **Input**: Director's vision from CarthirReview
- **Output**: Final visual prompts for generation
- **Key Functions**: `Cenedril()`
- **Performance Features**: Thread-safe operations, atomic file updates
- **Image Generation**: Optimized visual prompt creation

### LangGraph Workflow (Optimized)
```python
# Enhanced workflow in main.py with performance monitoring
graph_builder.add_edge(START, "carthir")
graph_builder.add_edge("carthir", "convert_prompt")
graph_builder.add_edge("convert_prompt", "narnion")
graph_builder.add_edge("narnion", "carthir_review")
graph_builder.add_edge("carthir_review", "cenedril")
graph_builder.add_edge("cenedril", END)
```

### State Management (Enhanced)
```python
class State(TypedDict):
    messages: Annotated[list, add_messages]          # Agent communication
    imn_filename: Annotated[str | None, last_value]  # Current .imn file
    id: Annotated[str | None, last_value]            # Dream ID
    user_id: str | None                              # User identifier
    carthir_memory: dict | None                      # Persistent creative memory
```

---

## 📁 Enhanced .imn File Format

The .imn (Imagination) file format has been enhanced for performance and thread safety:

```json
{
  "pre_production": {
    "id": "unique-dream-id",
    "user_id": "user-id",
    "dream_name": "Dream Title",
    "story_prompt": "Initial story description",
    "initial_goal": "User's goal",
    "pitch": "Creative pitch",
    "created_at": "2024-07-20T18:05:43Z",
    "director_vision": {
      "director_vision": "Creative vision description",
      "image_prompt": "Detailed image generation prompt",
      "visual_notes": "Style and composition notes",
      "approval_criteria": "Success criteria"
    },
    "first_frame_prompt": "Optimized image generation prompt",
    "visual_notes": "Enhanced visual guidance"
  },
  "in_production": [
    {
      "scene_id": 1,
      "frame_image": null,
      "timestamp": null,
      "scene_context": "Scene description",
      "user_action": null,
      "tap_location": null,
      "object_tapped": null,
      "actions": ["Choice 1", "Choice 2", "Choice 3"]
    }
  ],
  "post_production": {
    "final_outcome": "Story conclusion",
    "user_feedback": "User feedback",
    "exported_at": "2024-07-20T18:05:43Z"
  }
}
```

### File Operations (Thread-Safe)
```python
# Thread-safe .imn file operations
with get_imn_filelock(imn_file_path):
    imn_data = read_imn(imn_file_path)
    # Perform operations...
    write_imn(imn_data, directory)
```

---

## Development Workflow (Enhanced)

### Performance-Focused Development Process
1. **Morning**: Pull latest changes, check CUDA status, verify model loading
2. **Development**: Work on assigned agent or feature with performance monitoring
3. **Testing**: Run comprehensive test suite, monitor GPU utilization
4. **Performance Check**: Verify response times and resource usage
5. **Evening**: Commit changes, update documentation

### Testing the Agent Pipeline (Comprehensive)
```bash
# Option 1: GUI Test Suite (Recommended)
start_gui_test.bat
# Access: http://localhost:5000

# Option 2: Comprehensive CLI Tests
cd Backend/Python
python test_pipeline.py

# Option 3: Interactive Testing
cd Backend/Python
python main.py
# Enter test prompt: "A magical forest adventure with talking animals"

# Option 4: Simple API Testing
cd Backend/Python
python test_gui_simple.py
```

### Performance Monitoring During Development
```bash
# Monitor CUDA status
nvidia-smi

# Check GPU memory usage
nvidia-smi -l 1

# Monitor system resources
htop  # Linux/macOS
# Task Manager # Windows
```

### Common Development Tasks (Enhanced)

#### Adding a New Agent
1. Create agent function in `Backend/Python/core/agents.py`
2. Add to LangGraph workflow in `main.py`
3. Update state management with proper typing
4. Implement thread-safe .imn operations
5. Add error handling and fallback mechanisms
6. Test with comprehensive test suite

#### Modifying .imn Schema
1. Update schema documentation
2. Modify agent functions to handle new fields
3. Update utility functions in `core/imn_utils.py`
4. Implement backward compatibility
5. Test with existing .imn files
6. Run full test suite validation

#### Optimizing Performance
1. Profile CUDA utilization with `nvidia-smi`
2. Monitor thread allocation in console output
3. Track memory usage patterns
4. Optimize model parameters for speed vs quality
5. Test with concurrent requests
6. Benchmark against previous performance

#### Debugging Agent Issues
1. Check console output for CUDA status and errors
2. Verify .imn file structure with `validate_imn_structure()`
3. Test individual agents with mock data
4. Check LangGraph state transitions
5. Monitor file locking behavior
6. Use performance profiling tools

---

## 🐛 Common Issues & Solutions (Enhanced)

### Performance Issues
- **CUDA Not Available**: Check `nvidia-smi`, verify llama-cpp-python CUDA support
- **Slow Response Times**: Monitor GPU utilization, adjust thread allocation
- **Memory Issues**: Check VRAM usage, adjust model parameters
- **Thread Contention**: Verify file locking, monitor thread allocation

### Backend Issues
- **JSON Parsing Errors**: Check agent functions for robust error handling
- **Model Loading**: Verify GGUF model path and file existence
- **Import Errors**: Ensure all performance dependencies are installed
- **File Path Issues**: Verify Dreams directory and model directory exist

### Testing Issues
- **GUI Test Suite**: Check Flask dependencies, verify port availability
- **Test Failures**: Run individual test components, check error logs
- **Performance Tests**: Monitor system resources during testing
- **File Locking**: Verify no concurrent access to .imn files

### Frontend Issues
- **Build Errors**: Check Node.js version and dependencies
- **API Connection**: Verify backend is running with CUDA acceleration
- **Performance**: Monitor API response times in browser dev tools

### Agent Pipeline Issues
- **GGUF Model Issues**: Check model path, CUDA compatibility
- **State Management**: Check LangGraph state transitions and typing
- **File I/O**: Verify write permissions and file locking
- **Performance Degradation**: Monitor CUDA utilization and memory usage

---

## 🔧 Setup Verification

### Performance System Check
```bash
# Check CUDA availability
nvidia-smi

# Verify Python dependencies
cd Backend/Python
python -c "from llama_cpp import Llama; print('CUDA support available')"

# Check model file
ls Backend/Python/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf

# Run system health check
python -c "from core.agents import llm; print('GGUF model loaded successfully')"
```

### Test Suite Verification
```bash
# Quick GUI test
start_gui_test.bat  # Should open http://localhost:5000

# Comprehensive test
cd Backend/Python
python test_pipeline.py  # Should show all tests passing

# API test
python test_gui_simple.py  # Should show API endpoints working
```

---

## 📚 Learning Resources

### Performance & Optimization
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)
- [CUDA Programming Guide](https://docs.nvidia.com/cuda/)
- [Performance Optimization Plan](../ProjectPlanning/PERFORMANCE_OPTIMIZATION_PLAN.md)

### Core Technologies
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)

### Code Examples
- Check GGUF-optimized agents in `core/agents.py`
- Review performance test suite in `test_pipeline.py`
- Study API patterns in `api/dream_routes.py`
- Explore .imn file examples in `Backend/Dreams/`

---

## 🎯 Next Steps

1. **Setup Verification**: Complete the performance system check above
2. **Run Test Suite**: Execute the GUI test suite to verify everything works
3. **Read Architecture Docs**: Study `Documentation/TECHNICAL_ARCHITECTURE.md`
4. **Performance Monitoring**: Learn to monitor CUDA utilization and response times
5. **Explore Agents**: Familiarize yourself with the GGUF-optimized agent implementations
6. **Join Development**: Start contributing with performance-focused development!

---

## 🚀 Performance Development Tips

### Optimization Best Practices
- Always monitor CUDA utilization during development
- Use thread-safe operations for all .imn file access
- Implement intelligent fallbacks for all AI operations
- Profile performance changes before committing
- Test with concurrent requests to verify thread safety

### Monitoring Commands
```bash
# Monitor GPU usage
nvidia-smi -l 1

# Check system resources
htop  # Linux/macOS

# Monitor API performance
curl -w "Total: %{time_total}s\n" http://localhost:8000/health
```

### Development Environment
- Use verbose mode to monitor CUDA status
- Keep test suite running for quick validation
- Monitor memory usage patterns
- Profile response times regularly

---

## Getting Help

- **Performance Issues**: Check CUDA status and system resources
- **Technical Issues**: Run comprehensive test suite for diagnostics
- **Architecture Questions**: Review the enhanced documentation
- **Code Reviews**: Submit pull requests with performance considerations
- **General Questions**: Reach out to the team with specific error details

Welcome to the high-performance Dreams.ai team! 🚀✨ 