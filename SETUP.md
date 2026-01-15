# Athena Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Redis server
- Ollama with qwen3:8b model

## Backend Setup

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start Redis**:
```bash
# Windows
redis-server

# Linux/Mac
sudo systemctl start redis
```

4. **Start Ollama** (if not already running):
```bash
ollama serve
```

5. **Run the API server**:
```bash
python run_api.py
# Or
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at `http://localhost:8000`

## Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## First Run

1. Start Redis
2. Start Ollama
3. Start backend API (`python run_api.py`)
4. Start frontend (`cd frontend && npm run dev`)
5. Open browser to `http://localhost:3000`
6. Start chatting with Athena!

## Troubleshooting

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check REDIS_HOST and REDIS_PORT in .env

### LLM Connection Error
- Ensure Ollama is running: `curl http://localhost:11434/api/tags`
- Check LLM_URL and LLM_MODEL in .env

### Frontend Connection Error
- Ensure backend API is running on port 8000
- Check API proxy settings in vite.config.ts

### Emotion Model Loading
- First run will download the emotion model (~500MB)
- Ensure stable internet connection
- Model will be cached for future runs

## Production Deployment

### Backend
```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
cd frontend
npm run build
# Serve dist/ directory with nginx or similar
```

