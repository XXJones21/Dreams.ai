# Dreams.ai Technical Architecture

## System Overview

Dreams.ai is a multi-agent AI system that generates interactive narrative experiences. The platform uses a sophisticated pipeline of specialized AI agents to transform user prompts into rich, interactive dream stories stored in `.imn` (Imagination) files.

## Architecture Components

### 1. AI Agent Network

The system employs four specialized AI agents, each with distinct responsibilities:

#### **Carthir (Creative Director)**
- **Role**: Creative vision and initial story architecture
- **Input**: User's initial prompt
- **Output**: Creative pitch, story structure, and initial .imn file
- **Key Functions**: `Carthir()`, `convert_prompt_to_imn()`
- **LLM Model**: Gemma3:12b via Ollama

#### **Narnion (Storyteller)**
- **Role**: Interactive scene generation and narrative progression
- **Input**: .imn file from Carthir
- **Output**: Interactive scenes with user choices and actions
- **Key Functions**: `Narnion()`
- **Features**: Scene context generation, user action suggestions

#### **CarthirReview (Director's Vision)**
- **Role**: Creative consistency and visual direction
- **Input**: Scene context from Narnion
- **Output**: Visual direction and image prompts
- **Key Functions**: `CarthirReview()`
- **Features**: Director's vision generation, visual style guidance

#### **Cenedril (Cinematographer)**
- **Role**: Visual prompt generation for media creation
- **Input**: Director's vision from CarthirReview
- **Output**: Final visual prompts for image/video generation
- **Key Functions**: `Cenedril()`
- **Features**: Image prompt generation, visual style specification

### 2. Data Flow Architecture

```
User Prompt
    ↓
Carthir (Creative Director)
    ↓
convert_prompt_to_imn (.imn file creation)
    ↓
Narnion (Storyteller)
    ↓
CarthirReview (Director's Vision)
    ↓
Cenedril (Cinematographer)
    ↓
Final Output (.imn file with complete story)
```

### 3. State Management

The system uses LangGraph for state management with the following structure:

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]          # Agent communication
    imn_filename: Annotated[str | None, last_value]  # Current .imn file
    id: Annotated[str | None, last_value]            # Dream ID
    user_id: str | None                              # User identifier
    carthir_memory: dict | None                      # Persistent creative memory
```

### 4. File Structure

```
Dreams.ai/
├── Backend/
│   ├── Python/
│   │   ├── agents/              # AI agent implementations
│   │   │   └── __init__.py
│   │   ├── core/                # Shared utilities
│   │   │   ├── __init__.py
│   │   │   └── imn_utils.py     # .imn file operations
│   │   ├── api/                 # FastAPI routes
│   │   │   ├── __init__.py
│   │   │   └── dream_routes.py  # Dream API endpoints
│   │   ├── Dreams/              # Generated .imn files
│   │   ├── main.py              # LangGraph pipeline
│   │   ├── api_server.py        # FastAPI server
│   │   └── test_pipeline.py     # Test suite
│   └── Scoping/                 # Project documentation
│       ├── projectBreakdown.md
│       ├── schema.imn
│       └── CuriOS.md
├── src/                         # React frontend
├── supabase/                    # Database migrations
└── README.md
```

## Technology Stack

### Backend
- **Python 3.13+**: Core language for AI agents and API
- **FastAPI**: High-performance web framework
- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: LLM integration and prompt management
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **Supabase Client**: Database and auth integration

### AI/ML
- **Gemma3:12b**: Primary LLM model
- **Ollama**: Local LLM serving
- **LangChain**: LLM orchestration

### Database & Storage
- **Supabase**: PostgreSQL database
- **Supabase Auth**: User authentication
- **Supabase Storage**: File storage

## API Architecture

### Endpoints

#### `POST /api/dream`
Creates a new dream from a user prompt.

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
Retrieves a specific dream by ID.

#### `GET /api/dreams`
Lists available dreams with pagination.

### Error Handling

The API implements comprehensive error handling:
- **400 Bad Request**: Invalid input data
- **404 Not Found**: Dream not found
- **500 Internal Server Error**: Server-side errors

## .imn File Format

The `.imn` (Imagination) file is the central data structure:

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
      "frame_image": "path/to/image.png",
      "timestamp": "00:05",
      "scene_context": "Scene description",
      "user_action": "Selected action",
      "tap_location": {"x": 100, "y": 200},
      "object_tapped": "tapped object",
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

## Agent Communication Protocol

### Message Format
Agents communicate through structured messages:

```python
{
  "role": "user|assistant",
  "content": "message content",
  "additional_kwargs": {},
  "response_metadata": {},
  "id": "message-id"
}
```

### State Transitions
1. **User Input** → `Carthir`
2. **Carthir Output** → `convert_prompt_to_imn`
3. **IMN File** → `Narnion`
4. **Scene Context** → `CarthirReview`
5. **Director's Vision** → `Cenedril`
6. **Final Output** → End

## Security Considerations

### Authentication
- Supabase Auth integration
- JWT token validation
- User session management

### Data Validation
- Pydantic models for request/response validation
- .imn file structure validation
- Input sanitization

### Error Handling
- Graceful degradation on agent failures
- Fallback mechanisms for LLM errors
- Comprehensive logging

## Performance Optimization

### Caching Strategy
- .imn file caching for frequently accessed dreams
- Agent memory persistence
- LLM response caching

### Scalability
- Stateless agent design
- Horizontal scaling capability
- Database connection pooling

### Monitoring
- Agent performance metrics
- Pipeline execution times
- Error rate tracking

## Development Workflow

### Local Development
1. **Backend**: `python api_server.py`
2. **Frontend**: `npm run dev`
3. **Database**: Supabase local development
4. **LLM**: Ollama with Gemma3:12b

### Testing Strategy
- **Unit Tests**: Individual agent functions
- **Integration Tests**: Full pipeline execution
- **API Tests**: Endpoint validation
- **End-to-End Tests**: Complete user workflows

### Deployment
- **Backend**: FastAPI with Uvicorn
- **Frontend**: Vite build to static files
- **Database**: Supabase cloud hosting
- **LLM**: Ollama server deployment

## Future Architecture Considerations

### Planned Enhancements
1. **Parallel Agent Execution**: Concurrent agent processing
2. **Peer Review System**: Agent cross-validation
3. **Real-time Collaboration**: Multi-user dream creation
4. **Advanced Media Generation**: Video and audio integration
5. **Social Features**: Dream sharing and collaboration

### Scalability Roadmap
1. **Microservices**: Agent service separation
2. **Message Queues**: Asynchronous processing
3. **Load Balancing**: Multiple LLM instances
4. **CDN Integration**: Global content delivery
5. **Mobile Support**: React Native implementation

---

*This document is maintained as part of the Dreams.ai project and should be updated as the architecture evolves.* 