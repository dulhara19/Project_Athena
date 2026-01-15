# Athena API Documentation

## Overview

Athena API provides REST endpoints and WebSocket support for interacting with the Athena AI agent system.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently no authentication required. Add authentication middleware for production use.

## Endpoints

### Chat Endpoints

#### POST `/chat`

Process user chat input and return complete response.

**Request Body**:
```json
{
  "user_id": "user123",
  "session_id": "session1",
  "text": "I feel happy today"
}
```

**Response**:
```json
{
  "workflow_id": "uuid",
  "user_id": "user123",
  "session_id": "session1",
  "user_input": "I feel happy today",
  "athena_response": "That's wonderful to hear!",
  "workflow_steps": [...],
  "metrics": {
    "user_pain": 0.7,
    "athena_pain": 0.8,
    "empathy_metrics": {...},
    "ego_metrics": {...}
  },
  "ego_state": {...},
  "crisis_mode": false,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### POST `/chat/stream`

Start streaming workflow and return workflow ID for WebSocket connection.

**Request Body**: Same as `/chat`

**Response**:
```json
{
  "workflow_id": "uuid",
  "websocket_url": "/api/v1/ws/{workflow_id}",
  "status": "started"
}
```

#### WebSocket `/ws/{workflow_id}`

Real-time workflow updates via WebSocket.

**Events**:
- `workflow_progress`: Step-by-step progress updates
- `workflow_complete`: Workflow completion with full result
- `workflow_error`: Error occurred during workflow

### Metrics Endpoints

#### GET `/metrics`

Get current system metrics.

**Response**:
```json
{
  "ego_metrics": {...},
  "empathy_metrics": {...},
  "interaction_count": 42,
  "session_duration": null
}
```

#### GET `/metrics/research`

Get research-ready metrics export.

**Response**: Complete research data including ego state, evolution history, defense history.

### Ego Endpoints

#### GET `/ego/state`

Get current ego state.

**Response**:
```json
{
  "ego_strength": 0.75,
  "ego_fragility": 0.25,
  "consistency": 0.85,
  "evolution_trend": "stable",
  "dimensions": {...},
  "defense_stats": {...}
}
```

#### POST `/ego/reset`

Reset ego system to initial state.

**Request Body** (optional):
```json
{
  "initial_strength": 0.75
}
```

## WebSocket Protocol

### Connection

Connect to: `ws://localhost:8000/api/v1/ws/{workflow_id}`

### Message Format

All messages are JSON:

```json
{
  "type": "workflow_progress",
  "progress": {
    "workflow_id": "uuid",
    "current_step": 3,
    "total_steps": 9,
    "progress_percentage": 33.33,
    "steps": [...]
  }
}
```

### Event Types

- `workflow_progress`: Progress update with current step
- `workflow_complete`: Complete result with all data
- `workflow_error`: Error information

## Error Responses

All errors follow this format:

```json
{
  "error": true,
  "error_type": "ErrorClassName",
  "error_message": "Human-readable error message",
  "context": {
    "endpoint": "/chat",
    "user_id": "user123"
  }
}
```

## Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

