# Dreams.ai Technical Architecture

## System Overview

Dreams.ai is a multi-agent AI system that generates interactive narrative experiences. The platform uses a sophisticated pipeline of specialized AI agents to transform user prompts into rich, interactive dream stories stored in `.imn` (Imagination) files. The system is optimized for high performance using **GGUF models with CUDA acceleration** and intelligent threading strategies.

## Architecture Components

### 1. AI Agent Network

The system employs four specialized AI agents, each optimized for high-performance execution:

#### **Carthir (Creative Director)**
- **Role**: Creative vision and initial story architecture
- **Input**: User's initial prompt
- **Output**: Creative pitch, story structure, and initial .imn file
- **Key Functions**: `Carthir()`, `convert_prompt_to_imn()`
- **Performance**: GGUF-optimized with CUDA acceleration
- **Features**: Robust JSON parsing with fallback mechanisms

#### **Narnion (Storyteller)**
- **Role**: Interactive scene generation and narrative progression
- **Input**: .imn file from Carthir
- **Output**: Interactive scenes with user choices and actions
- **Key Functions**: `Narnion()`
- **Features**: Scene context generation, user action suggestions, centralized JSON parsing
- **Performance**: Real-time scene generation with error recovery

#### **CarthirReview (Director's Vision)**
- **Role**: Creative consistency and visual direction
- **Input**: Scene context from Narnion
- **Output**: Visual direction and image prompts
- **Key Functions**: `CarthirReview()`
- **Features**: Director's vision generation, visual style guidance, persistent memory
- **Performance**: Optimized vision parsing with intelligent fallbacks

#### **Cenedril (Cinematographer)**
- **Role**: Visual prompt generation for media creation
- **Input**: Director's vision from CarthirReview
- **Output**: Final visual prompts for image/video generation
- **Key Functions**: `Cenedril()`
- **Features**: Image prompt generation, visual style specification, file locking for consistency
- **Performance**: Thread-safe operations with atomic file updates

### 2. Performance Optimization Architecture

#### **GGUF Model Integration**
```python
llm = ChatLlamaCpp(
    model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=1024,      # Optimized for speed
    top_p=0.9,
    verbose=True,         # Enable CUDA status monitoring
    n_ctx=2048,          # Reduced context window for speed
    n_threads=optimal_threads,  # Dynamic 8-16 threads
    n_batch=512,         # Larger batch for GPU processing
    use_mmap=True,       # Memory mapping for faster loading
    use_mlock=False,     # OS memory management
    f16_kv=True,         # Half precision key-value cache
    n_gpu_layers=35,     # Maximum GPU layer offloading
)
```

#### **Environment-Aware Threading**
The system detects its runtime environment and optimizes accordingly:

```python
# Check for multi-threaded environment (Flask)
is_flask_server = threading.active_count() > 1 or os.environ.get('FLASK_RUN_PORT') is not None

if is_flask_server:
    # Conservative threading for Flask server
    optimal_threads = min(8, os.cpu_count() // 2)
else:
    # Aggressive threading for CLI/standalone
    optimal_threads = min(16, os.cpu_count())
```

#### **Memory Optimization**
- **Memory Mapping**: `use_mmap=True` for faster model loading
- **Half Precision**: `f16_kv=True` reduces memory usage by ~50%
- **Batch Processing**: Optimized batch size (512) for GPU throughput
- **Context Management**: Reduced context window (2048) for faster processing

### 3. Data Flow Architecture

```
User Prompt
    ↓
Carthir (Creative Director) [GGUF/CUDA Optimized]
    ↓
convert_prompt_to_imn (.imn file creation with file locking)
    ↓
Narnion (Storyteller) [Parallel Processing Ready]
    ↓
CarthirReview (Director's Vision) [Persistent Memory]
    ↓
Cenedril (Cinematographer) [Thread-Safe Operations]
    ↓
Final Output (.imn file with complete story)
```

### 4. State Management

The system uses LangGraph for state management with enhanced type safety:

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]          # Agent communication
    imn_filename: Annotated[str | None, last_value]  # Current .imn file
    id: Annotated[str | None, last_value]            # Dream ID
    user_id: str | None                              # User identifier
    carthir_memory: dict | None                      # Persistent creative memory
```

### 5. File System Architecture

#### **Thread-Safe .imn File Operations**
```python
# Centralized file locking for thread safety
with get_imn_filelock(imn_file_path):
    imn_data = read_imn(imn_file_path)
    # Perform operations...
    write_imn(imn_data, directory)
```

#### **Robust JSON Parsing**
Centralized parsing functions with intelligent fallbacks:
- `parse_carthir_response()`: Creative pitch parsing with fallbacks
- `parse_director_vision_response()`: Visual direction parsing
- `parse_narnion_response()`: Scene generation parsing
- `create_scene_for_imn()`: Structured scene creation

### 6. File Structure

```
Dreams.ai/
├── Backend/
│   ├── Python/
│   │   ├── agents/              # AI agent implementations
│   │   ├── core/                # Optimized core utilities
│   │   │   ├── agents.py        # GGUF/CUDA optimized agent definitions
│   │   │   ├── imn_utils.py     # Thread-safe .imn file operations
│   │   │   ├── image_generator.py # Image generation utilities
│   │   │   └── pipeline_instance.py # Pipeline management
│   │   ├── api/                 # FastAPI routes
│   │   │   └── dream_routes.py  # High-performance dream endpoints
│   │   ├── Dreams/              # Generated .imn files
│   │   ├── models/              # GGUF model storage
│   │   │   └── Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
│   │   ├── main.py              # LangGraph pipeline with performance monitoring
│   │   ├── api_server.py        # FastAPI server with CORS optimization
│   │   ├── test_pipeline.py     # Comprehensive test suite
│   │   ├── test_gui.py          # GUI test interface with image generation
│   │   └── test_gui_simple.py   # Simple API testing
│   └── Scoping/                 # Project documentation
├── Documentation/               # Technical documentation
├── src/                         # React frontend with TypeScript
├── supabase/                    # Database migrations and schema
└── public/                      # Static assets and logos
```

## Technology Stack

### Backend Performance Stack
- **Python 3.13+**: Core language with latest performance optimizations
- **FastAPI**: High-performance async web framework
- **LangGraph**: Agent orchestration with state management
- **LangChain Community**: Optimized LLM implementations
- **llama-cpp-python**: GGUF model loading with CUDA support
- **filelock**: Thread-safe file operations
- **psutil**: System resource monitoring
- **Pydantic**: High-performance data validation

### Frontend
- **React 18**: UI framework with concurrent features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Lightning-fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Supabase Client**: Real-time database integration

### AI/ML Performance Stack
- **GGUF Models**: Quantized model format for optimal performance
- **CUDA Acceleration**: GPU processing with 35-layer offloading
- **Meta-Llama-3.1-8B**: Instruction-tuned model with Q4_K_M quantization
- **Dynamic Threading**: Environment-aware thread allocation
- **Memory Mapping**: Faster model loading with `use_mmap`
- **Half Precision Cache**: 50% memory reduction with `f16_kv`
- **Batch Optimization**: 512-token batches for GPU efficiency

### Database & Storage
- **Supabase**: PostgreSQL database with real-time features
- **Supabase Auth**: Secure JWT-based authentication
- **Supabase Storage**: Scalable file storage with CDN

## API Architecture

### High-Performance Endpoints

#### `POST /api/dream`
Creates a new dream with optimized processing pipeline.

**Performance Features:**
- CUDA-accelerated AI generation
- Parallel agent processing (planned)
- Real-time progress updates (planned)
- Intelligent error recovery

**Request:**
```json
{
  "prompt": "A corgi taking a nap on a sunny beach"
}
```

**Response:**
```json
{
  "dream_name": "Sunshine & Snuggles",
  "story_prompt": "A delightful corgi...",
  "initial_goal": "To experience pure joy...",
  "pitch": "Imagine a world painted in warm, golden light...",
  "imn_filename": "dream-id.imn"
}
```

#### `GET /api/dreams/{dream_id}`
Retrieves specific dreams with optimized caching.

#### `GET /api/dreams`
Lists dreams with efficient pagination and filtering.

### Error Handling & Performance

The API implements comprehensive error handling with performance monitoring:
- **400 Bad Request**: Invalid input with detailed validation
- **404 Not Found**: Dream not found with caching optimization
- **500 Internal Server Error**: Server errors with fallback mechanisms
- **Performance Metrics**: Response time tracking and resource monitoring

## .imn File Format (Enhanced)

The `.imn` (Imagination) file format has been enhanced for performance and thread safety:

```json
{
  "pre_production": {
    "id": "unique-dream-id",
    "user_id": "user-id",
    "dream_name": "Dream Title",
    "story_prompt": "Initial story description",
    "initial_goal": "User's goal",
    "pitch": "Creative pitch",
    "created_at": "2024-01-01T12:00:00Z",
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
    "exported_at": "2024-01-01T12:30:00Z"
  }
}
```

### File Operations Performance
- **Thread-Safe Operations**: File locking prevents corruption
- **Atomic Writes**: Consistent file updates
- **Validation**: Structure validation before writing
- **Error Recovery**: Graceful handling of corrupted files

## Agent Communication Protocol

### High-Performance Message Format
Agents communicate through optimized structured messages:

```python
{
  "role": "user|assistant",
  "content": "message content",
  "additional_kwargs": {},
  "response_metadata": {},
  "id": "message-id"
}
```

### State Transitions (Optimized)
1. **User Input** → `Carthir` (CUDA-accelerated)
2. **Carthir Output** → `convert_prompt_to_imn` (Thread-safe)
3. **IMN File** → `Narnion` (Parallel processing ready)
4. **Scene Context** → `CarthirReview` (Persistent memory)
5. **Director's Vision** → `Cenedril` (Atomic operations)
6. **Final Output** → End (Performance metrics logged)

## Security & Performance Considerations

### Authentication & Security
- **Supabase Auth**: JWT token validation with caching
- **Row-Level Security**: Database-level access control
- **Input Sanitization**: Comprehensive input validation
- **File Access Control**: Secure .imn file operations

### Performance Security
- **Resource Management**: CPU and GPU usage monitoring
- **Memory Protection**: Controlled memory allocation
- **Thread Safety**: File locking and atomic operations
- **Error Isolation**: Agent failure doesn't affect others

### Data Validation & Performance
- **Pydantic Models**: High-performance validation
- **Schema Validation**: .imn file structure enforcement
- **Type Safety**: TypeScript and Python type checking
- **Performance Monitoring**: Real-time metrics collection

## Performance Optimization Strategies

### Current Optimizations
1. **GGUF Model Quantization**: 4-bit quantization for speed
2. **CUDA Layer Offloading**: 35 layers on GPU for maximum acceleration
3. **Dynamic Threading**: Environment-aware thread allocation
4. **Memory Mapping**: Faster model loading with `use_mmap`
5. **Half Precision Cache**: 50% memory reduction with `f16_kv`
6. **Batch Optimization**: 512-token batches for GPU efficiency

### Planned Optimizations
1. **Parallel Agent Execution**: Concurrent agent processing
2. **Response Streaming**: Real-time updates to frontend
3. **Intelligent Caching**: Response and intermediate result caching
4. **Load Balancing**: Multiple model instances
5. **Pipeline Optimization**: Sub-10 second dream generation

### Monitoring & Metrics
- **CUDA Utilization**: GPU usage monitoring
- **Memory Usage**: RAM and VRAM tracking
- **Response Times**: End-to-end performance measurement
- **Thread Efficiency**: CPU utilization optimization
- **Error Rates**: Failure tracking and recovery metrics

## Testing Architecture

### Comprehensive Testing Infrastructure

#### 1. **GUI Test Suite**
- **Visual Interface**: `http://localhost:5000`
- **Real-time Testing**: Live pipeline execution
- **Image Generation**: Automatic visual content creation
- **Performance Monitoring**: Response time tracking

#### 2. **Automated Test Pipeline**
- **Unit Tests**: Individual component validation
- **Integration Tests**: Full pipeline execution
- **Performance Tests**: CUDA and threading optimization
- **Error Handling**: Fallback mechanism validation

#### 3. **Load Testing**
- **Concurrent Requests**: Multiple dream generation
- **Resource Monitoring**: CPU/GPU usage under load
- **Memory Leak Detection**: Long-running stability
- **Thread Safety**: Concurrent file operations

### Test Coverage
- ✅ **IMN Utilities**: File operations and locking
- ✅ **Agent Functions**: All four agents with fallbacks
- ✅ **CUDA Integration**: GPU acceleration validation
- ✅ **Threading**: Environment-aware optimization
- ✅ **Performance**: Response time and resource usage

## Development Workflow

### Local Development Setup
1. **Backend**: CUDA-enabled environment setup
2. **Model Installation**: GGUF model deployment
3. **Testing**: Comprehensive test suite execution
4. **Performance Monitoring**: Real-time metrics tracking

### Performance Development Cycle
1. **Code Changes**: Performance-focused development
2. **Testing**: Automated performance validation
3. **Profiling**: CPU/GPU utilization analysis
4. **Optimization**: Iterative performance improvements
5. **Deployment**: Production performance verification

### Deployment Architecture
- **Backend**: FastAPI with CUDA optimization
- **Model Serving**: GGUF with GPU acceleration
- **Frontend**: Optimized React build
- **Database**: Supabase with connection pooling
- **Monitoring**: Performance metrics collection

## Future Architecture Evolution

### Performance Roadmap
1. **Phase 1**: GGUF/CUDA Integration ✅ **COMPLETED**
2. **Phase 2**: Parallel Agent Processing (In Progress)
3. **Phase 3**: Real-time Streaming (Planned)
4. **Phase 4**: Multi-GPU Support (Planned)
5. **Phase 5**: Edge Deployment (Future)

### Scalability Planning
1. **Horizontal Scaling**: Multiple model instances
2. **Load Distribution**: Request routing optimization
3. **Caching Layers**: Multi-level response caching
4. **CDN Integration**: Global content delivery
5. **Mobile Optimization**: React Native implementation

### Advanced Features
1. **Real-time Collaboration**: Multi-user dream creation
2. **Advanced Media Generation**: Video and audio integration
3. **AI-Powered Optimization**: Self-tuning performance
4. **Predictive Loading**: User behavior optimization
5. **Edge Computing**: Local model deployment

---

*This document is maintained as part of the Dreams.ai project and reflects the current high-performance architecture with GGUF/CUDA optimization. Updated regularly to reflect architectural improvements and performance enhancements.* 