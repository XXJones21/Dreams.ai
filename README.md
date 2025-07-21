![Dreams.ai Logo](public/logo.png)

# Dreams.ai - Interactive AI-Powered Dream Generation

## Project Overview

Dreams.ai is a revolutionary platform that transforms simple prompts into rich, interactive narrative experiences. Using a sophisticated network of AI agents, the system generates personalized dream stories that users can interact with and share. Each dream is stored as a `.imn` (Imagination) file, creating a unique format for collaborative storytelling.

### Key Features
- **AI Agent Network**: Four specialized agents working together
- **Interactive Narratives**: User-driven story progression
- **Visual Generation**: AI-powered image and video prompts
- **Social Sharing**: Share and experience others' dreams
- **Real-time Processing**: Dynamic story generation

### Vision
To create the world's most immersive and interactive storytelling platform, where every user can become both a dreamer and a dream creator.

---

## Documentation

### For Developers
- **[Developer Onboarding](Documentation/DEVELOPER_ONBOARDING.md)** - Complete setup guide for new developers
- **[Technical Architecture](Documentation/TECHNICAL_ARCHITECTURE.md)** - Detailed system architecture and design
- **[API Documentation](Documentation/API_DOCUMENTATION.md)** - Complete API reference and examples
- **[Development Workflow](Documentation/DEVELOPMENT_WORKFLOW.md)** - Development guidelines and best practices

### For Users
- **[Project Overview](Backend/Scoping/projectBreakdown.md)** - Detailed project breakdown and vision
- **[Schema Documentation](Backend/Scoping/schema.imn)** - Complete .imn file format specification

### Project Status
- **[Phase 1 Completion](Documentation/ProjectPlanning/PHASE_1_COMPLETION.md)** - Phase 1 completion summary
- **[Phase 2 Completion](Documentation/ProjectPlanning/PHASE_2_COMPLETION.md)** - Phase 2 completion summary

---

## Technology Stack

### Backend
- **Python 3.13+**: Core language for AI agents and API
- **FastAPI**: High-performance web framework
- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM integration and prompt management
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React 18**: UI framework with modern features
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Lightning-fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Supabase Client**: Database and auth integration

### AI/ML
- **Gemma3:12b**: Primary LLM model for creative generation
- **Ollama**: Local LLM serving and management
- **LangChain**: Advanced LLM orchestration

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
│   │   ├── core/                # Shared utilities
│   │   │   └── imn_utils.py     # .imn file operations
│   │   ├── api/                 # FastAPI routes
│   │   │   └── dream_routes.py  # Dream API endpoints
│   │   ├── Dreams/              # Generated .imn files
│   │   ├── main.py              # LangGraph pipeline
│   │   ├── api_server.py        # FastAPI server
│   │   └── test_pipeline.py     # Test suite
│   └── Scoping/                 # Project documentation
│       ├── projectBreakdown.md  # Detailed project overview
│       ├── schema.imn           # .imn file format specification
│       └── CuriOS.md            # Additional documentation
├── Documentation/               # Project documentation
│   ├── DEVELOPER_ONBOARDING.md  # Developer setup guide
│   ├── TECHNICAL_ARCHITECTURE.md # System architecture
│   ├── API_DOCUMENTATION.md     # API reference
│   ├── DEVELOPMENT_WORKFLOW.md  # Development guidelines
│   └── ProjectPlanning/         # Project planning and status
│       ├── PHASE_1_COMPLETION.md # Phase 1 completion summary
│       └── PHASE_2_COMPLETION.md # Phase 2 completion summary
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
├── package.json                 # Frontend dependencies
└── README.md                    # This file
```

---

## AI Agent System

Dreams.ai uses a sophisticated network of four specialized AI agents:

### **Carthir (Creative Director)**
- **Role**: Creative vision and initial story architecture
- **Input**: User's initial prompt
- **Output**: Creative pitch, story structure, and initial .imn file
- **Specialty**: Story concept development and creative direction

### **Narnion (Storyteller)**
- **Role**: Interactive scene generation and narrative progression
- **Input**: .imn file from Carthir
- **Output**: Interactive scenes with user choices and actions
- **Specialty**: Dynamic storytelling and user interaction

### **CarthirReview (Director's Vision)**
- **Role**: Creative consistency and visual direction
- **Input**: Scene context from Narnion
- **Output**: Visual direction and image prompts
- **Specialty**: Visual style guidance and creative consistency

### **Cenedril (Cinematographer)**
- **Role**: Visual prompt generation for media creation
- **Input**: Director's vision from CarthirReview
- **Output**: Final visual prompts for image/video generation
- **Specialty**: Visual media generation and cinematography

## Quick Start

### Prerequisites
- **Python 3.13+** (required for the backend)
- **Node.js 18+** (required for the frontend)
- **Git** (for version control)

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

### 4. Start the Services
```bash
# Terminal 1: Start the backend
cd Backend/Python
python api_server.py

# Terminal 2: Start the frontend
npm run dev
```

### 5. Verify Installation
- Backend should be running on `http://localhost:8000`
- Frontend should be running on `http://localhost:5173`
- Check the API docs at `http://localhost:8000/docs`

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

### GUI Test Suite
The GUI test suite provides a visual interface for testing the complete AI agent pipeline:

#### Quick Start
**Option 1: Use launcher scripts (Recommended)**
```bash
# From project root
start_gui_test.bat          # Windows Batch
start_gui_test.ps1          # PowerShell

# From Backend/Python directory
start_gui_test.bat          # Windows Batch
start_gui_test.ps1          # PowerShell
```

**Option 2: Manual start**
```bash
cd Backend/Python
python test_gui.py
```

#### Features
- **Visual Dream Cards**: See generated dreams in a frontend-like interface
- **Real-time Testing**: Run pipeline tests with live status updates
- **Image Generation**: Automatic image generation for each dream
- **Detailed Views**: Modal windows with complete dream information
- **Test History**: Track and review all test results
- **Server Management**: Automatic dependency checking and server status monitoring

#### Access
Open `http://localhost:5000` in your browser

#### Launcher Features
- **Dependency Check**: Automatically installs required packages
- **Server Status**: Checks if server is already running
- **Browser Launch**: Automatically opens the test interface
- **Graceful Shutdown**: Properly stops the server when done

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
    }
  },
  "in_production": [
    {
      "scene_id": 1,
      "scene_context": "Scene description",
      "actions": ["Choice 1", "Choice 2", "Choice 3"],
      "user_action": "Selected choice",
      "tap_location": {"x": 100, "y": 200}
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

For complete schema documentation, see `Backend/Scoping/schema.imn`.

---

## Testing

### Run Test Suite
```bash
cd Backend/Python
python test_pipeline.py
```

### Test Individual Components
```bash
# Test .imn utilities
python -c "from core.imn_utils import *; print('Utilities working')"

# Test agent pipeline
python main.py
# Enter test prompt: "A magical forest adventure"
```

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

3. **Environment Variables**
   - Configure Supabase credentials
   - Set up Ollama server
   - Configure CORS settings


---

## Acknowledgments

- **LangGraph Team**: For the amazing agent orchestration framework
- **Supabase Team**: For the powerful backend-as-a-service platform
- **Ollama Team**: For making local LLM deployment accessible
- **Open Source Community**: For all the amazing tools and libraries

---

**Made with passion by the Dreams.ai team** 