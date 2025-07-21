# Dreams.ai Developer Onboarding

Welcome to Dreams.ai! This guide will help you get up and running quickly.

## Quick Start (5 minutes)

### Prerequisites
- **Python 3.13+** (required for the backend)
- **Node.js 18+** (required for the frontend)
- **Git** (for version control)

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

---

## 🏗️ Architecture Overview

### Technology Stack
- **Frontend**: React + TypeScript + TailwindCSS + Vite
- **Backend**: FastAPI + LangGraph + LangChain + Python 3.13
- **Database**: Supabase (PostgreSQL + Auth + Storage)
- **AI Pipeline**: Multi-agent system with specialized roles

### Key Components

#### AI Agent Network
- **Carthir** (Creative Director): Generates initial story concepts and creative vision
- **Narnion** (Storyteller): Creates interactive scenes and user choices
- **CarthirReview** (Director's Vision): Ensures creative consistency and provides visual direction
- **Cenedril** (Cinematographer): Generates visual prompts for video/image generation

#### Data Flow
1. User prompt → Carthir → .imn file creation
2. .imn file → Narnion → scene generation
3. Scene → CarthirReview → visual direction
4. Direction → Cenedril → video/image prompts

#### File Structure
```
Dreams.ai/
├── Backend/
│   ├── Python/
│   │   ├── agents/          # AI agent implementations
│   │   ├── core/            # Shared utilities
│   │   ├── api/             # FastAPI routes
│   │   ├── Dreams/          # Generated .imn files
│   │   ├── main.py          # LangGraph pipeline
│   │   └── api_server.py    # FastAPI server
│   └── Scoping/             # Project documentation
├── src/                     # React frontend
├── supabase/                # Database migrations
└── README.md
```

---

## 🔧 Key Files to Know

### Backend
- `Backend/Python/main.py` - LangGraph agent pipeline (the heart of the system)
- `Backend/Python/api_server.py` - FastAPI server entry point
- `Backend/Python/core/imn_utils.py` - Utilities for .imn file operations
- `Backend/Python/api/dream_routes.py` - API endpoints for dream operations

### Frontend
- `src/App.tsx` - Main React application
- `src/components/` - UI components organized by feature
- `src/lib/supabase.ts` - Supabase client configuration

### Documentation
- `Backend/Scoping/` - Comprehensive project documentation
- `Backend/Scoping/schema.imn` - .imn file format specification
- `Backend/Scoping/projectBreakdown.md` - Detailed project overview

---

## Understanding the Agent Workflow

### Agent Responsibilities

#### Carthir (Creative Director)
- **Input**: User's initial prompt
- **Output**: Creative vision, story structure, and initial .imn file
- **Key Functions**: `Carthir()`, `convert_prompt_to_imn()`

#### Narnion (Storyteller)
- **Input**: .imn file from Carthir
- **Output**: Interactive scenes with user choices
- **Key Functions**: `Narnion()`

#### CarthirReview (Director's Vision)
- **Input**: Scene context from Narnion
- **Output**: Visual direction and image prompts
- **Key Functions**: `CarthirReview()`

#### Cenedril (Cinematographer)
- **Input**: Director's vision from CarthirReview
- **Output**: Final visual prompts for generation
- **Key Functions**: `Cenedril()`

### LangGraph Workflow
```python
# Current workflow in main.py
graph_builder.add_edge(START, "carthir")
graph_builder.add_edge("carthir", "convert_prompt")
graph_builder.add_edge("convert_prompt", "narnion")
graph_builder.add_edge("narnion", "carthir_review")
graph_builder.add_edge("carthir_review", "cenedril")
graph_builder.add_edge("cenedril", END)
```

---

## 📁 .imn File Format

The .imn (Imagination) file is the central data structure that stores all dream information:

```json
{
  "pre_production": {
    "id": "unique-dream-id",
    "user_id": "user-id",
    "dream_name": "Dream Title",
    "story_prompt": "Initial story description",
    "initial_goal": "User's goal",
    "pitch": "Creative pitch",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "in_production": [
    {
      "scene_id": 1,
      "scene_context": "Scene description",
      "actions": ["Choice 1", "Choice 2"],
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

---

## Development Workflow

### Daily Development Process
1. **Morning**: Pull latest changes, check agent pipeline status
2. **Development**: Work on assigned agent or feature
3. **Testing**: Test with sample prompts, verify .imn file generation
4. **Evening**: Commit changes, update documentation

### Testing the Agent Pipeline
```bash
cd Backend/Python
python main.py
# Enter a test prompt like: "A corgi taking a nap on a sunny beach"
```

### Common Development Tasks

#### Adding a New Agent
1. Create agent function in `main.py`
2. Add to LangGraph workflow
3. Update state management
4. Test with sample prompts

#### Modifying .imn Schema
1. Update `Backend/Scoping/schema.imn`
2. Modify agent functions to handle new fields
3. Update utility functions in `core/imn_utils.py`
4. Test with existing .imn files

#### Debugging Agent Issues
1. Check console output for error messages
2. Verify .imn file structure with `validate_imn_structure()`
3. Test individual agents with mock data
4. Check LangGraph state transitions

---

## 🐛 Common Issues & Solutions

### Backend Issues
- **JSON Parsing Errors**: Check CarthirReview function for control characters
- **Import Errors**: Ensure all dependencies are installed
- **File Path Issues**: Verify Dreams directory exists

### Frontend Issues
- **Build Errors**: Check Node.js version and dependencies
- **API Connection**: Verify backend is running and CORS is configured
- **Supabase Issues**: Check environment variables

### Agent Pipeline Issues
- **LLM Connection**: Verify Ollama is running at `http://10.1.95.9:11434`
- **State Management**: Check LangGraph state transitions
- **File I/O**: Verify write permissions for Dreams directory

---

## 📚 Learning Resources

### Documentation
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)

### Code Examples
- Check existing agent implementations in `main.py`
- Review .imn file examples in `Backend/Dreams/`
- Study API patterns in `api/dream_routes.py`

---

## 🎯 Next Steps

1. **Read the Scoping Documentation**: Start with `Backend/Scoping/projectBreakdown.md`
2. **Run a Test Dream**: Use the chatbot interface to generate a sample dream
3. **Explore the Codebase**: Familiarize yourself with the agent implementations
4. **Join the Team**: Ask questions, share ideas, and contribute!

---

## Getting Help

- **Technical Issues**: Check the troubleshooting section above
- **Architecture Questions**: Review the Scoping documentation
- **Code Reviews**: Submit pull requests for review
- **General Questions**: Reach out to the team

Welcome to the Dreams.ai team! 