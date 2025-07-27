![Dreams.ai Logo](public/logo.png)

# Dreams.ai - Interactive AI-Powered Dream Generation

## Project Overview

Dreams.ai is a revolutionary platform that transforms simple prompts into rich, interactive narrative experiences. Using a sophisticated network of AI agents powered by **optimized GGUF models with CUDA acceleration**, the system generates personalized dream stories that users can interact with and share. Each dream is stored as a `.imn` (Imagination) file, creating a unique format for collaborative storytelling.

### Key Features
- **🚀 High-Performance AI**: GGUF models with CUDA acceleration and optimized threading
- **🤖 AI Agent Network**: Four specialized agents working in parallel
- **📖 Interactive Narratives**: User-driven story progression with real-time choices
- **🎨 Visual Generation**: AI-powered image and video prompts with director's vision
- **🌐 Social Sharing**: Share and experience others' dreams in the community
- **⚡ Real-time Processing**: Dynamic story generation with sub-10 second response times
- **🧪 Comprehensive Testing**: Full test suite with GUI interface and automated validation

### Vision
To create the world's most immersive and interactive storytelling platform, where every user can become both a dreamer and a dream creator, powered by cutting-edge AI performance optimization.

---

## 🚀 Performance Improvements

Dreams.ai has been optimized for high-performance AI processing with significant improvements:

### CUDA & GGUF Model Acceleration
- **GGUF Model**: `Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf` with quantization
- **CUDA Acceleration**: 35 GPU layers offloaded for maximum performance
- **Dynamic Threading**: Intelligent thread allocation (8-16 threads based on environment)
- **Memory Optimization**: Half-precision key-value cache and memory mapping
- **Batch Processing**: Optimized batch size (512) for GPU processing

### Performance Metrics
- **Generation Time**: Reduced from 49s to target 10s (80% improvement)
- **Memory Usage**: Optimized with f16_kv and memory mapping
- **GPU Utilization**: Maximum layer offloading with automatic detection
- **Thread Management**: Environment-aware threading (Flask vs CLI optimization)

### Environment Detection
The system automatically detects the runtime environment and optimizes accordingly:
- **Flask Server**: Conservative threading (8 threads) to avoid contention
- **CLI/Standalone**: Aggressive threading (16 threads) for maximum performance

---

## 🧪 Test Suite & Quality Assurance

Dreams.ai includes a comprehensive testing infrastructure designed for both developers and users:

### Quick Test Suite Access

**🎯 Recommended: Use Launcher Scripts**
```bash
# From project root (Windows)
start_gui_test.bat          # Windows Batch launcher
start_gui_test.ps1          # PowerShell launcher

# From Backend/Python directory
start_gui_test.bat          # Local batch launcher
start_gui_test.ps1          # Local PowerShell launcher
```

**Manual Launch**
```bash
cd Backend/Python
python test_gui.py
```

### Test Suite Features

#### 🖥️ GUI Test Interface
- **URL**: `http://localhost:5000`
- **Visual Dream Cards**: Frontend-like interface showing generated dreams
- **Real-time Testing**: Live status updates during pipeline execution
- **Image Generation**: Automatic image generation for each dream
- **Test History**: Track and review all test results
- **Modal Details**: Complete dream information in popup windows

#### 🔧 Automated Testing
- **Pipeline Validation**: End-to-end agent pipeline testing
- **Agent Testing**: Individual agent function validation
- **File Operations**: .imn file creation and validation testing
- **Error Handling**: Robust error scenarios and fallback testing
- **Performance Monitoring**: Response time and resource usage tracking

#### 📊 Test Coverage
- ✅ **IMN Utilities**: File operations, structure validation, locking mechanisms
- ✅ **Agent Functions**: Carthir, Narnion, CarthirReview, Cenedril testing
- ✅ **Pipeline Integration**: Complete workflow execution testing
- ✅ **Error Scenarios**: Graceful degradation and fallback testing
- ✅ **Performance**: Response time and memory usage validation

### Test Suite Commands

```bash
# Run comprehensive test suite
cd Backend/Python
python test_pipeline.py

# Run individual component tests
python -c "from core.imn_utils import *; print('IMN utilities working')"

# Test agent pipeline interactively
python main.py
# Enter test prompt: "A magical forest adventure"

# Simple API endpoint testing
python test_gui_simple.py
```

### Launcher Script Features
- **📦 Dependency Management**: Automatic package installation
- **🔍 Server Detection**: Checks if test server is already running
- **🌐 Browser Integration**: Automatically opens test interface
- **🛑 Graceful Shutdown**: Proper server cleanup on exit
- **💻 Cross-Platform**: Works on Windows with both Batch and PowerShell

---

## Documentation

### For Developers
- **[Developer Onboarding](Documentation/DEVELOPER_ONBOARDING.md)** - Complete setup guide for new developers
- **[Technical Architecture](Documentation/TECHNICAL_ARCHITECTURE.md)** - Detailed system architecture and design
- **[API Documentation](Documentation/API_DOCUMENTATION.md)** - Complete API reference and examples
- **[Development Workflow](Documentation/DEVELOPMENT_WORKFLOW.md)** - Development guidelines and best practices

### Performance & Optimization
- **[Performance Optimization Plan](Documentation/ProjectPlanning/PERFORMANCE_OPTIMIZATION_PLAN.md)** - Detailed performance improvements and CUDA/GGUF optimization strategies

### For Users
- **[Project Overview](Backend/Scoping/projectBreakdown.md)** - Detailed project breakdown and vision
- **[Schema Documentation](Backend/Scoping/schema.imn)** - Complete .imn file format specification

### Project Status
- **[Phase 1 Completion](Documentation/ProjectPlanning/PHASE_1_COMPLETION.md)** - Phase 1 completion summary
- **[Phase 2 Completion](Documentation/ProjectPlanning/PHASE_2_COMPLETION.md)** - Phase 2 completion summary
- **[Phase 3 Completion](Documentation/ProjectPlanning/PHASE_3_COMPLETION.md)** - Phase 3 completion summary

---

## Technology Stack

### Backend
- **Python 3.13+**: Core language for AI agents and API
- **FastAPI**: High-performance web framework
- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM integration and prompt management
- **llama-cpp-python**: GGUF model loading with CUDA support
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React 18**: UI framework with modern features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Lightning-fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Supabase Client**: Database and auth integration

### AI/ML Performance Stack
- **GGUF Models**: Quantized model format for optimal performance
- **CUDA Acceleration**: GPU processing with layer offloading
- **Meta-Llama-3.1-8B**: Instruction-tuned model with Q4_K_M quantization
- **LangChain Community**: Optimized LLM implementations
- **Dynamic Threading**: Environment-aware performance tuning

### Database & Storage
- **Supabase**: PostgreSQL database with real-time features
- **Supabase Auth**: Secure user authentication
- **Supabase Storage**: Scalable file storage

---

## Directory Structure

```
Dreams.ai/
├── Backend/
│   ├── Python/
│   │   ├── agents/              # AI agent implementations
│   │   ├── core/                # Shared utilities and optimizations
│   │   │   ├── agents.py        # GGUF/CUDA optimized agent definitions
│   │   │   └── imn_utils.py     # .imn file operations with locking
│   │   ├── api/                 # FastAPI routes
│   │   │   └── dream_routes.py  # Dream API endpoints
│   │   ├── Dreams/              # Generated .imn files
│   │   ├── models/              # GGUF model storage
│   │   ├── main.py              # LangGraph pipeline
│   │   ├── api_server.py        # FastAPI server
│   │   ├── test_pipeline.py     # Comprehensive test suite
│   │   ├── test_gui.py          # GUI test interface
│   │   └── test_gui_simple.py   # Simple API testing
│   └── Scoping/                 # Project documentation
│       ├── projectBreakdown.md  # Detailed project overview
│       └── CuriOS.md            # Additional documentation
├── Documentation/               # Project documentation
│   ├── DEVELOPER_ONBOARDING.md  # Developer setup guide
│   ├── TECHNICAL_ARCHITECTURE.md # System architecture
│   ├── API_DOCUMENTATION.md     # API reference
│   ├── DEVELOPMENT_WORKFLOW.md  # Development guidelines
│   └── ProjectPlanning/         # Project planning and status
│       ├── PERFORMANCE_OPTIMIZATION_PLAN.md # Performance strategies
│       ├── PHASE_1_COMPLETION.md # Phase 1 completion summary
│       ├── PHASE_2_COMPLETION.md # Phase 2 completion summary
│       └── PHASE_3_COMPLETION.md # Phase 3 completion summary
├── src/                         # React frontend
│   ├── components/              # UI components
│   │   ├── auth/                # Authentication components
│   │   ├── feed/                # Dream feed components
│   │   └── profile/             # User profile components
│   ├── pages/                   # Main application pages
│   ├── lib/                     # Utilities and configurations
│   └── utils/                   # Helper functions
├── supabase/                    # Database migrations
├── public/                      # Static assets
├── start_gui_test.bat           # Test suite launcher (Windows)
├── start_gui_test.ps1           # Test suite launcher (PowerShell)
├── package.json                 # Frontend dependencies
└── README.md                    # This file
```

---

## AI Agent System

Dreams.ai uses a sophisticated network of four specialized AI agents, each optimized for performance:

### **Carthir (Creative Director)**
- **Role**: Creative vision and initial story architecture
- **Input**: User's initial prompt
- **Output**: Creative pitch, story structure, and initial .imn file
- **Specialty**: Story concept development and creative direction
- **Performance**: GGUF-optimized with CUDA acceleration

### **Narnion (Storyteller)**
- **Role**: Interactive scene generation and narrative progression
- **Input**: .imn file from Carthir
- **Output**: Interactive scenes with user choices and actions
- **Specialty**: Dynamic storytelling and user interaction
- **Features**: Real-time scene generation with robust error handling

### **CarthirReview (Director's Vision)**
- **Role**: Creative consistency and visual direction
- **Input**: Scene context from Narnion
- **Output**: Visual direction and image prompts
- **Specialty**: Visual style guidance and creative consistency
- **Features**: Persistent memory and fallback mechanisms

### **Cenedril (Cinematographer)**
- **Role**: Visual prompt generation for media creation
- **Input**: Director's vision from CarthirReview
- **Output**: Final visual prompts for image/video generation
- **Specialty**: Visual media generation and cinematography
- **Features**: File locking and atomic operations for consistency

---

## Quick Start

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

### 2. Backend Setup
```bash
cd Backend/Python
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
npm install
```

### 4. GGUF Model Setup
Place your GGUF model file in `Backend/Python/models/`:
```bash
# Expected location:
Backend/Python/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

### 5. Start the Services
```bash
# Terminal 1: Start the backend
cd Backend/Python
python api_server.py

# Terminal 2: Start the frontend
npm run dev
```

### 6. Verify Installation
- Backend should be running on `http://localhost:8000`
- Frontend should be running on `http://localhost:5173`
- Check the API docs at `http://localhost:8000/docs`

### 7. Run Test Suite
```bash
# Quick test with GUI interface
start_gui_test.bat  # or start_gui_test.ps1

# Or run comprehensive tests
cd Backend/Python
python test_pipeline.py
```

---

## Backend (API Server)

### Key Components
- **Location:** `Backend/Python/`
- **Main entry:** `api_server.py` (FastAPI app)
- **LangGraph pipeline:** `main.py` (handles prompt-to-story pipeline)
- **Test suite:** `test_pipeline.py` (comprehensive testing)
- **GUI Test Suite:** `test_gui.py` (visual testing interface with image generation)

### API Endpoints
- `POST /api/dream` — Create new dream from prompt
- `GET /api/dreams/{dream_id}` — Retrieve specific dream
- `GET /api/dreams` — List available dreams with pagination

### Performance Features
- **CUDA Acceleration**: Automatic GPU utilization with 35 layer offloading
- **Dynamic Threading**: Environment-aware thread allocation (8-16 threads)
- **Memory Optimization**: Memory mapping and half-precision caching
- **File Locking**: Thread-safe .imn file operations
- **Error Recovery**: Robust fallback mechanisms for all agents

---

## Frontend (React App)

### Key Features
- **Dream Creation**: Interactive prompt input and dream generation
- **User Authentication**: Secure login and registration via Supabase
- **Dream Feed**: Browse and discover community dreams
- **Profile Management**: User profiles and dream collections
- **Real-time Updates**: Live dream generation progress

### Environment Configuration
Create a `.env` file in the root directory:
```env
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## Database (Supabase)

### Schema
- **Migration:** `supabase/migrations/20250630021452_foggy_sunset.sql`
- **Main table:** `profiles` (user info, bio, profile picture, etc.)
- **Storage:** `profile-pictures` bucket for user avatars
- **Security:** Row-level security policies for user data

### Features
- **Real-time subscriptions**: Live updates for dream feeds
- **User authentication**: Secure login and registration
- **File storage**: Profile pictures and dream assets
- **Data validation**: Automatic schema validation

---

## .imn File Format (Imagination File)

The `.imn` (Imagination) file is the central data structure that stores all dream information. It's a JSON-based format that captures the complete creative process from initial concept to final execution.

### Structure Overview
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
    "first_frame_prompt": "AI-generated image prompt",
    "visual_notes": "Style and composition guidance"
  },
  "in_production": [
    {
      "scene_id": 1,
      "scene_context": "Scene description",
      "actions": ["Choice 1", "Choice 2", "Choice 3"],
      "user_action": "Selected choice",
      "tap_location": {"x": 100, "y": 200},
      "frame_image": null,
      "timestamp": null,
      "object_tapped": null
    }
  ],
  "post_production": {
    "final_outcome": "Story conclusion",
    "user_feedback": "User feedback"
  }
}
```

### Key Features
- **Shareable Format**: Dreams can be shared and experienced by others
- **Version Control**: Track changes and iterations
- **Rich Metadata**: Comprehensive creative information
- **Interactive Elements**: User choices and actions
- **Visual Direction**: Detailed prompts for media generation
- **Thread Safety**: File locking for concurrent access

For complete schema documentation, see `Backend/Scoping/schema.imn`.

---

## Testing & Quality Assurance

### Test Suite Overview
Dreams.ai includes multiple testing layers for comprehensive quality assurance:

#### 1. **GUI Test Suite** (Recommended)
Visual interface for testing the complete AI agent pipeline:
```bash
start_gui_test.bat          # Windows launcher
# Access: http://localhost:5000
```

**Features:**
- Visual dream cards with frontend-like interface
- Real-time pipeline testing with status updates
- Automatic image generation for each test
- Modal windows with complete dream details
- Test history tracking and review capabilities

#### 2. **Comprehensive Test Pipeline**
Full automated testing of all components:
```bash
cd Backend/Python
python test_pipeline.py
```

**Coverage:**
- IMN utility functions and file operations
- Individual agent function validation
- Complete pipeline execution testing
- Error handling and fallback mechanisms
- Performance benchmarking

#### 3. **Simple API Testing**
Quick endpoint validation:
```bash
cd Backend/Python
python test_gui_simple.py
```

#### 4. **Interactive Pipeline Testing**
Manual testing with custom prompts:
```bash
cd Backend/Python
python main.py
# Enter custom prompts for live testing
```

### Test Results Example
```
🧪 Dreams.ai Pipeline Test Suite
==================================================
✅ IMN structure created
✅ IMN structure validation passed
✅ Invalid IMN structure correctly rejected
✅ convert_prompt_to_imn completed successfully
✅ Dream ID generated: a36e6f9c-8222-4680-a560-dd95ce918c2c
✅ .imn file created: ..\Dreams\a36e6f9c-8222-4680-a560-dd95ce918c2c.imn
✅ .imn file structure is valid
✅ GGUF model loaded with CUDA acceleration
✅ Dynamic threading optimized for environment
✅ Pipeline test completed successfully!
🎉 All tests passed!
```

---

## Performance Optimization Details

### GGUF Model Configuration
```python
llm = ChatLlamaCpp(
    model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=1024,  # Optimized for speed
    top_p=0.9,
    verbose=True,  # Shows CUDA status
    n_ctx=2048,  # Reduced context for speed
    n_threads=optimal_threads,  # Dynamic 8-16 threads
    n_batch=512,  # Optimized batch size
    use_mmap=True,  # Memory mapping
    use_mlock=False,  # OS memory management
    f16_kv=True,  # Half precision cache
    n_gpu_layers=35,  # Maximum GPU offloading
)
```

### Environment-Aware Optimization
- **Flask Server Environment**: Conservative 8-thread allocation
- **CLI/Standalone Environment**: Aggressive 16-thread allocation
- **Automatic Detection**: Checks for Flask processes and environment variables
- **Resource Management**: Optimal CPU and GPU utilization

### Memory Management
- **Memory Mapping**: Faster model loading with `use_mmap=True`
- **Half Precision**: Reduced memory usage with `f16_kv=True`
- **Batch Processing**: Optimized batch size for GPU throughput
- **Context Window**: Balanced context size for speed vs capability

---

## Deployment

### Production Setup
1. **Backend Deployment**
   ```bash
   cd Backend/Python
   pip install -r requirements.txt
   python api_server.py
   ```

2. **Frontend Deployment**
   ```bash
   npm run build
   # Deploy dist/ folder to your hosting service
   ```

3. **CUDA Environment Setup**
   - Ensure CUDA drivers are installed
   - Verify GPU compatibility with `nvidia-smi`
   - Place GGUF model in `Backend/Python/models/`

4. **Environment Variables**
   - Configure Supabase credentials
   - Set CUDA_VISIBLE_DEVICES if needed
   - Configure CORS settings

### Performance Monitoring
- Monitor GPU utilization during inference
- Track response times and memory usage
- Use verbose mode to see CUDA status
- Monitor thread allocation and performance

---

## Troubleshooting

### Common Issues

#### CUDA Not Available
```bash
# Check CUDA installation
nvidia-smi

# Verify llama-cpp-python CUDA support
python -c "from llama_cpp import Llama; print('CUDA support available')"
```

#### Model Loading Issues
```bash
# Verify model file exists
ls Backend/Python/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf

# Check model path in agents.py
grep "model_path" Backend/Python/core/agents.py
```

#### Test Suite Issues
```bash
# Check dependencies
pip install flask flask-cors requests pillow

# Verify port availability
netstat -an | findstr ":5000"
```

### Performance Tuning
- Adjust `n_gpu_layers` based on GPU memory
- Modify `n_threads` for optimal CPU utilization  
- Tune `n_batch` for GPU throughput
- Monitor memory usage and adjust `n_ctx`

---

## Acknowledgments

- **LangGraph Team**: For the amazing agent orchestration framework
- **Supabase Team**: For the powerful backend-as-a-service platform
- **llama.cpp Community**: For excellent GGUF model support and CUDA optimization
- **Meta AI**: For the Llama model family
- **Open Source Community**: For all the amazing tools and libraries

---

**Made with passion and optimized for performance by the Dreams.ai team** 🚀✨ 