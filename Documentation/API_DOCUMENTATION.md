# Dreams.ai API Documentation

## Overview

The Dreams.ai API provides high-performance endpoints for creating, retrieving, and managing interactive dream experiences. The API is built with **FastAPI** and optimized with **GGUF models and CUDA acceleration** for rapid dream generation. It provides RESTful endpoints for dream creation and management with comprehensive error handling and performance monitoring.

## Performance Features

### 🚀 CUDA-Accelerated Processing
- **GGUF Model**: Meta-Llama-3.1-8B-Instruct with Q4_K_M quantization
- **GPU Acceleration**: 35 GPU layers offloaded for maximum performance
- **Dynamic Threading**: 8-16 threads based on environment detection
- **Memory Optimization**: Half-precision caching and memory mapping
- **Response Time**: Target sub-10 second dream generation

### 🔧 Advanced Error Handling
- **Graceful Degradation**: Intelligent fallback mechanisms
- **JSON Parsing**: Robust parsing with error recovery
- **File Operations**: Thread-safe .imn file management
- **Agent Recovery**: Individual agent failure isolation

## Base URL

```
http://localhost:8000
```

## Interactive API Documentation

Visit the interactive API documentation for live testing and exploration:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Authentication

Currently, the API uses basic authentication. Future versions will implement Supabase Auth integration with JWT token validation.

## Endpoints

### 1. Create Dream

Creates a new dream from a user prompt using the high-performance AI agent pipeline.

**Endpoint:** `POST /api/dream`

**Performance Features:**
- CUDA-accelerated AI generation
- Intelligent error recovery with fallbacks
- Thread-safe .imn file creation
- Real-time performance monitoring

**Request Body:**
```json
{
  "prompt": "A corgi taking a nap on a sunny beach"
}
```

**Response (Success):**
```json
{
  "dream_name": "Sunshine & Snuggles",
  "story_prompt": "A delightful corgi, utterly relaxed, drifts into a dreamscape triggered by a perfect, sun-drenched nap on a pristine beach.",
  "initial_goal": "To experience pure, unadulterated joy and discover the sweet absurdity of being a corgi on an endless summer day.",
  "pitch": "Imagine a single, perfect ray of sunshine. Now imagine a corgi, nestled within it, completely at peace with the warm sand beneath its belly and the gentle rhythm of waves in the distance. This isn't just a nap—this is a gateway to pure bliss...",
  "imn_filename": "a36e6f9c-8222-4680-a560-dd95ce918c2c.imn"
}
```

**Response (With Fallback):**
```json
{
  "dream_name": "Dream: A corgi taking a nap on a sunny beach...",
  "story_prompt": "A corgi taking a nap on a sunny beach",
  "initial_goal": "To explore and discover the dream's meaning",
  "pitch": "A dream journey based on: A corgi taking a nap on a sunny beach",
  "imn_filename": "b7c8d9e0-1234-5678-9abc-def123456789.imn"
}
```

**Status Codes:**
- `200 OK`: Dream created successfully
- `400 Bad Request`: Invalid prompt or request format
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error during dream generation (with fallback data)

**Performance Metrics:**
- **Average Response Time**: 2-8 seconds (CUDA-optimized)
- **Memory Usage**: Optimized with GGUF quantization
- **GPU Utilization**: Automatic CUDA layer offloading
- **Fallback Rate**: <5% with intelligent error recovery

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/api/dream" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A magical forest adventure with talking animals"}'
```

### 2. Get Dream by ID

Retrieves a specific dream by its unique identifier with optimized caching.

**Endpoint:** `GET /api/dreams/{dream_id}`

**Path Parameters:**
- `dream_id` (string): Unique identifier for the dream (UUID format)

**Performance Features:**
- Optimized .imn file reading with file locking
- Intelligent caching for frequently accessed dreams
- Structured data transformation

**Response:**
```json
{
  "id": "a36e6f9c-8222-4680-a560-dd95ce918c2c",
  "title": "Sunshine & Snuggles",
  "excerpt": "A delightful corgi, utterly relaxed, drifts into a dreamscape...",
  "content": "Imagine a single, perfect ray of sunshine...",
  "creator": {
    "id": "user-uuid-placeholder",
    "name": "Dreamer",
    "avatar": null,
    "verified": false
  },
  "engagement": {
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "views": 0
  },
  "tags": [],
  "category": "",
  "emotion": "",
  "theme": "",
  "created_at": "2024-07-20T18:05:43Z",
  "is_trending": false,
  "is_featured": false,
  "similarity_score": null
}
```

**Status Codes:**
- `200 OK`: Dream retrieved successfully
- `404 Not Found`: Dream not found or .imn file missing
- `500 Internal Server Error`: Server error reading dream data

**Performance Optimization:**
- **File Locking**: Thread-safe .imn file access
- **Caching**: Intelligent response caching
- **Error Recovery**: Graceful handling of corrupted files

**Example Usage:**
```bash
curl "http://localhost:8000/api/dreams/a36e6f9c-8222-4680-a560-dd95ce918c2c"
```

### 3. List Dreams

Retrieves a paginated list of available dreams with efficient filtering and sorting.

**Endpoint:** `GET /api/dreams`

**Query Parameters:**
- `limit` (integer, optional): Maximum number of dreams to return (default: 10, max: 100)
- `offset` (integer, optional): Number of dreams to skip for pagination (default: 0)

**Performance Features:**
- Efficient file system scanning
- Parallel .imn file processing
- Intelligent pagination with metadata

**Response:**
```json
{
  "dreams": [
    {
      "id": "a36e6f9c-8222-4680-a560-dd95ce918c2c",
      "title": "Sunshine & Snuggles",
      "excerpt": "A delightful corgi...",
      "content": "Imagine a single, perfect ray of sunshine...",
      "creator": {
        "id": "user-uuid-placeholder",
        "name": "Dreamer",
        "avatar": null,
        "verified": false
      },
      "engagement": {
        "likes": 0,
        "comments": 0,
        "shares": 0,
        "views": 0
      },
      "tags": [],
      "category": "",
      "emotion": "",
      "theme": "",
      "created_at": "2024-07-20T18:05:43Z",
      "is_trending": false,
      "is_featured": false,
      "similarity_score": null
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

**Status Codes:**
- `200 OK`: Dreams retrieved successfully
- `400 Bad Request`: Invalid pagination parameters
- `500 Internal Server Error`: Server error during dream listing

**Performance Metrics:**
- **File Scanning**: Optimized directory traversal
- **Parallel Processing**: Concurrent .imn file reading
- **Memory Efficiency**: Streaming responses for large datasets

**Example Usage:**
```bash
curl "http://localhost:8000/api/dreams?limit=5&offset=0"
```

### 4. Health Check

Provides system health and performance status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-07-20T18:05:43Z",
  "version": "1.0.0",
  "performance": {
    "cuda_available": true,
    "gpu_layers": 35,
    "threading_mode": "cli",
    "optimal_threads": 16
  }
}
```

**Status Codes:**
- `200 OK`: System is healthy
- `503 Service Unavailable`: System issues detected

## Data Models

### DreamPrompt
```python
class DreamPrompt(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="User's dream prompt")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "A magical forest adventure with talking animals"
            }
        }
```

### DreamResponse
```python
class DreamResponse(BaseModel):
    dream_name: str
    story_prompt: str
    initial_goal: str
    pitch: str
    imn_filename: str
    
    class Config:
        schema_extra = {
            "example": {
                "dream_name": "Woodland Whispers",
                "story_prompt": "You are an explorer in a magical forest...",
                "initial_goal": "To discover the secret of the talking animals",
                "pitch": "Deep in an enchanted forest...",
                "imn_filename": "abc123.imn"
            }
        }
```

### DreamCard
```python
class DreamCard(BaseModel):
    id: str
    title: str
    excerpt: str
    content: str
    creator: Creator
    engagement: Engagement
    tags: List[str]
    category: str
    emotion: str
    theme: str
    created_at: str
    is_trending: bool
    is_featured: bool
    similarity_score: Optional[float]
```

### Creator
```python
class Creator(BaseModel):
    id: str
    name: str
    avatar: Optional[str]
    verified: bool
```

### Engagement
```python
class Engagement(BaseModel):
    likes: int
    comments: int
    shares: int
    views: int
```

## Error Responses

### Standard Error Format
All API errors follow a consistent format with detailed information:

```json
{
  "detail": "Error message description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-07-20T18:05:43Z",
  "request_id": "req_abc123"
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid prompt format. Prompt must be a non-empty string with maximum 1000 characters.",
  "error_code": "INVALID_PROMPT",
  "timestamp": "2024-07-20T18:05:43Z",
  "request_id": "req_abc123"
}
```

#### 404 Not Found
```json
{
  "detail": "Dream not found. The specified dream ID does not exist or the .imn file is missing.",
  "error_code": "DREAM_NOT_FOUND",
  "timestamp": "2024-07-20T18:05:43Z",
  "request_id": "req_abc123"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-07-20T18:05:43Z",
  "request_id": "req_abc123"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Error generating dream. CUDA acceleration failed, using CPU fallback. Please try again later.",
  "error_code": "GENERATION_ERROR",
  "timestamp": "2024-07-20T18:05:43Z",
  "request_id": "req_abc123"
}
```

## Performance Optimization

### GGUF Model Configuration
The API leverages optimized GGUF models for maximum performance:

```python
# Model configuration for optimal performance
llm = ChatLlamaCpp(
    model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=1024,      # Optimized for speed
    n_ctx=2048,           # Reduced context for faster processing
    n_threads=optimal_threads,  # Dynamic 8-16 threads
    n_batch=512,          # GPU-optimized batch size
    n_gpu_layers=35,      # Maximum GPU offloading
    use_mmap=True,        # Memory mapping
    f16_kv=True,          # Half precision cache
    verbose=True          # CUDA status monitoring
)
```

### Environment Detection
The system automatically optimizes based on runtime environment:
- **Flask Server**: Conservative 8-thread allocation
- **CLI/Standalone**: Aggressive 16-thread allocation
- **CUDA Detection**: Automatic GPU utilization
- **Memory Management**: Dynamic resource allocation

### Caching Strategy
- **Response Caching**: Intelligent caching for frequently accessed dreams
- **Model Caching**: Persistent model loading
- **File Caching**: .imn file caching with invalidation
- **Memory Optimization**: Efficient memory usage patterns

## Rate Limiting

Currently, no rate limiting is implemented. Future versions will include:
- **User-based Rate Limiting**: Requests per user per time period
- **IP-based Rate Limiting**: Requests per IP address
- **Endpoint-specific Limits**: Different limits for different endpoints
- **Sliding Window**: Advanced rate limiting algorithms

## CORS

The API supports CORS for the following origins:
- `https://sparkling-souffle-39b291.netlify.app` (Production frontend)
- `http://localhost:5173` (Development frontend)
- `http://localhost:3000` (Alternative development frontend)

## Testing Integration

### GUI Test Suite Integration
The API integrates with the comprehensive GUI test suite:

**Test Endpoints:**
- `GET /api/status` - Test suite status and metrics
- `POST /api/test/dream` - Test dream generation with monitoring
- `GET /api/test/dreams` - Test dream listing functionality

**GUI Test Interface:**
- **URL**: `http://localhost:5000` (when test suite is running)
- **Features**: Visual dream cards, real-time testing, performance monitoring
- **Usage**: Run `start_gui_test.bat` or `start_gui_test.ps1`

### Performance Testing
```bash
# Run comprehensive API tests
cd Backend/Python
python test_pipeline.py

# Run GUI test suite
start_gui_test.bat

# Simple API validation
python test_gui_simple.py
```

## WebSocket Support

Future versions will include WebSocket support for:
- **Real-time Dream Generation**: Live progress updates
- **Streaming Responses**: Progressive dream content delivery
- **Collaborative Features**: Multi-user dream creation
- **Performance Monitoring**: Real-time metrics streaming

## SDK Examples

### Python
```python
import requests
import json

# Configure API client
API_BASE = "http://localhost:8000"

def create_dream(prompt):
    """Create a new dream with error handling"""
    try:
        response = requests.post(
            f"{API_BASE}/api/dream",
            json={"prompt": prompt},
            timeout=30  # Account for CUDA processing time
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating dream: {e}")
        return None

def get_dream(dream_id):
    """Get a specific dream"""
    try:
        response = requests.get(f"{API_BASE}/api/dreams/{dream_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving dream: {e}")
        return None

# Example usage
dream = create_dream("A magical forest adventure")
if dream:
    dream_id = dream["imn_filename"].replace(".imn", "")
    dream_data = get_dream(dream_id)
    print(f"Created dream: {dream_data['title']}")
```

### JavaScript
```javascript
class DreamsAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    async createDream(prompt) {
        try {
            const response = await fetch(`${this.baseURL}/api/dream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating dream:', error);
            throw error;
        }
    }

    async getDream(dreamId) {
        try {
            const response = await fetch(`${this.baseURL}/api/dreams/${dreamId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error retrieving dream:', error);
            throw error;
        }
    }

    async listDreams(limit = 10, offset = 0) {
        try {
            const response = await fetch(
                `${this.baseURL}/api/dreams?limit=${limit}&offset=${offset}`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error listing dreams:', error);
            throw error;
        }
    }
}

// Example usage
const api = new DreamsAPI();

async function generateDream() {
    try {
        const dream = await api.createDream('A corgi taking a nap on a sunny beach');
        console.log('Dream created:', dream);
        
        const dreamId = dream.imn_filename.replace('.imn', '');
        const dreamData = await api.getDream(dreamId);
        console.log('Dream details:', dreamData);
    } catch (error) {
        console.error('Error:', error);
    }
}
```

### cURL Examples
```bash
# Create dream with detailed error handling
curl -X POST "http://localhost:8000/api/dream" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A magical forest adventure with talking animals"}' \
  -w "\nResponse Time: %{time_total}s\nHTTP Code: %{http_code}\n"

# Get dream with error handling
curl "http://localhost:8000/api/dreams/a36e6f9c-8222-4680-a560-dd95ce918c2c" \
  -w "\nResponse Time: %{time_total}s\nHTTP Code: %{http_code}\n" \
  -f

# List dreams with pagination
curl "http://localhost:8000/api/dreams?limit=5&offset=0" \
  -w "\nResponse Time: %{time_total}s\nHTTP Code: %{http_code}\n"

# Health check
curl "http://localhost:8000/health" \
  -w "\nResponse Time: %{time_total}s\nHTTP Code: %{http_code}\n"
```

## Monitoring & Observability

### Performance Metrics
The API automatically tracks and reports:
- **Response Times**: End-to-end request processing
- **CUDA Utilization**: GPU usage during dream generation
- **Memory Usage**: RAM and VRAM consumption
- **Error Rates**: Success/failure ratios with categorization
- **Thread Efficiency**: CPU utilization patterns

### Logging
Comprehensive logging includes:
- **Request/Response Logging**: Full API interaction tracking
- **Performance Logging**: Timing and resource usage
- **Error Logging**: Detailed error information with stack traces
- **CUDA Status Logging**: GPU acceleration status and issues

### Health Monitoring
- **System Health**: CPU, memory, and GPU status
- **Model Status**: GGUF model loading and performance
- **Database Connectivity**: Supabase connection health
- **File System**: .imn file storage health

## Future Endpoints

### Planned Features
1. **User Authentication**: `/api/auth/*` endpoints with Supabase integration
2. **Dream Sharing**: `/api/dreams/{id}/share` for social features
3. **Dream Collections**: `/api/collections/*` for organized dream groups
4. **User Profiles**: `/api/users/*` for user management
5. **Dream Analytics**: `/api/analytics/*` for usage insights
6. **Real-time Updates**: WebSocket endpoints for live updates
7. **Dream Collaboration**: `/api/dreams/{id}/collaborate` for multi-user editing
8. **Performance Metrics**: `/api/metrics/*` for system monitoring

### Versioning Strategy
Future API versions will be available with backward compatibility:
- **v1**: `/api/v1/*` (Current)
- **v2**: `/api/v2/*` (Planned with WebSocket support)
- **v3**: `/api/v3/*` (Future with advanced AI features)

### Enhanced Features
- **Streaming Responses**: Real-time dream generation updates
- **Batch Processing**: Multiple dream creation in single request
- **Advanced Filtering**: Content-based dream search and filtering
- **Caching Control**: Client-side caching directives
- **Rate Limiting**: Sophisticated rate limiting with quotas

---

*This documentation is maintained as part of the Dreams.ai project and reflects the current high-performance API with GGUF/CUDA optimization. Updated regularly to reflect API improvements and new features.* 