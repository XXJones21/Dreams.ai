# Dreams.ai API Documentation

## Overview

The Dreams.ai API provides endpoints for creating, retrieving, and managing interactive dream experiences. The API is built with FastAPI and provides RESTful endpoints for dream generation and management.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses basic authentication. Future versions will implement Supabase Auth integration.

## Endpoints

### 1. Create Dream

Creates a new dream from a user prompt using the AI agent pipeline.

**Endpoint:** `POST /api/dream`

**Request Body:**
```json
{
  "prompt": "A corgi taking a nap on a sunny beach"
}
```

**Response:**
```json
{
  "dream_name": "Sunshine & Snuggles",
  "story_prompt": "A delightful corgi, utterly relaxed, drifts into a dreamscape triggered by a perfect, sun-drenched nap on a pristine beach.",
  "initial_goal": "To experience pure, unadulterated joy and discover the sweet absurdity of being a corgi on an endless summer day.",
  "pitch": "Imagine a single, perfect ray of sunshine. Now imagine a corgi, nestled within it, completely at peace...",
  "imn_filename": "a36e6f9c-8222-4680-a560-dd95ce918c2c.imn"
}
```

**Status Codes:**
- `200 OK`: Dream created successfully
- `400 Bad Request`: Invalid prompt or request format
- `500 Internal Server Error`: Server error during dream generation

**Example Usage:**
```bash
curl -X POST "http://localhost:8000/api/dream" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A magical forest adventure"}'
```

### 2. Get Dream by ID

Retrieves a specific dream by its unique identifier.

**Endpoint:** `GET /api/dreams/{dream_id}`

**Path Parameters:**
- `dream_id` (string): Unique identifier for the dream

**Response:**
```json
{
  "id": "a36e6f9c-8222-4680-a560-dd95ce918c2c",
  "title": "Sunshine & Snuggles",
  "excerpt": "A delightful corgi, utterly relaxed, drifts into a dreamscape...",
  "content": "Imagine a single, perfect ray of sunshine...",
  "creator": {
    "id": "user-123",
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
  "created_at": "2024-01-01T12:00:00Z",
  "is_trending": false,
  "is_featured": false,
  "similarity_score": null
}
```

**Status Codes:**
- `200 OK`: Dream retrieved successfully
- `404 Not Found`: Dream not found
- `500 Internal Server Error`: Server error

**Example Usage:**
```bash
curl "http://localhost:8000/api/dreams/a36e6f9c-8222-4680-a560-dd95ce918c2c"
```

### 3. List Dreams

Retrieves a paginated list of available dreams.

**Endpoint:** `GET /api/dreams`

**Query Parameters:**
- `limit` (integer, optional): Maximum number of dreams to return (default: 10, max: 100)
- `offset` (integer, optional): Number of dreams to skip (default: 0)

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
        "id": "user-123",
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
      "created_at": "2024-01-01T12:00:00Z",
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
- `500 Internal Server Error`: Server error

**Example Usage:**
```bash
curl "http://localhost:8000/api/dreams?limit=5&offset=0"
```

## Data Models

### DreamPrompt
```python
class DreamPrompt(BaseModel):
    prompt: str
```

### DreamResponse
```python
class DreamResponse(BaseModel):
    dream_name: str
    story_prompt: str
    initial_goal: str
    pitch: str
    imn_filename: str
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
```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid prompt format. Prompt must be a non-empty string."
}
```

#### 404 Not Found
```json
{
  "detail": "Dream not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Error generating dream. Please try again later."
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Future versions will include rate limiting based on user authentication.

## CORS

The API supports CORS for the following origins:
- `https://sparkling-souffle-39b291.netlify.app` (Production frontend)
- `http://localhost:5173` (Development frontend)

## WebSocket Support

Future versions will include WebSocket support for real-time dream generation updates.

## SDK Examples

### Python
```python
import requests

# Create a dream
response = requests.post(
    "http://localhost:8000/api/dream",
    json={"prompt": "A magical forest adventure"}
)
dream = response.json()

# Get a dream
dream_id = dream["imn_filename"].replace(".imn", "")
response = requests.get(f"http://localhost:8000/api/dreams/{dream_id}")
dream_data = response.json()
```

### JavaScript
```javascript
// Create a dream
const response = await fetch('http://localhost:8000/api/dream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'A magical forest adventure'
  })
});
const dream = await response.json();

// Get a dream
const dreamId = dream.imn_filename.replace('.imn', '');
const dreamResponse = await fetch(`http://localhost:8000/api/dreams/${dreamId}`);
const dreamData = await dreamResponse.json();
```

### cURL
```bash
# Create dream
curl -X POST "http://localhost:8000/api/dream" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A magical forest adventure"}'

# Get dream
curl "http://localhost:8000/api/dreams/a36e6f9c-8222-4680-a560-dd95ce918c2c"

# List dreams
curl "http://localhost:8000/api/dreams?limit=5&offset=0"
```

## Testing

### Health Check
```bash
curl "http://localhost:8000/health"
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### OpenAPI Schema
The OpenAPI schema is available at `http://localhost:8000/openapi.json`.

## Future Endpoints

### Planned Features
1. **User Authentication**: `/api/auth/*` endpoints
2. **Dream Sharing**: `/api/dreams/{id}/share`
3. **Dream Collections**: `/api/collections/*`
4. **User Profiles**: `/api/users/*`
5. **Dream Analytics**: `/api/analytics/*`
6. **Real-time Updates**: WebSocket endpoints

### Versioning
Future API versions will be available at `/api/v2/*`, `/api/v3/*`, etc.

---

*This documentation is maintained as part of the Dreams.ai project and should be updated as the API evolves.* 