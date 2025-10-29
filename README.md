# PANARAY Feature Assistant

A production-ready, full-stack Web App Feature Assistant powered by RAG (Retrieval-Augmented Generation) with emotion-adaptive responses. Built following SOLID and DRY principles.

## 🎯 Features

- **RAG-Powered Responses**: Answers questions using only the provided knowledge base via vector similarity search
- **Emotion Detection**: Detects user emotions and adapts response tone accordingly
- **Modern UI**: Beautiful, responsive interface built with React, TypeScript, and TailwindCSS
- **Production-Ready**: Fully async backend with proper error handling and logging
- **Vector Search**: Pinecone serverless for efficient similarity search
- **Type-Safe**: Full TypeScript implementation on frontend

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Vector DB**: Pinecone (serverless)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **LLM**: Llama 3 (meta-llama/Meta-Llama-3-8B-Instruct) via Hugging Face Inference API
- **Emotion Classifier**: distilbert-base-uncased-emotion (Hugging Face)
- **Design**: SOLID principles, service layer architecture, dependency injection

### Frontend
- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **UI Components**: Radix UI primitives
- **State Management**: React Hooks (custom `useChat` hook)

## 📁 Project Structure

```
/workspace/
├── backend/
│   ├── app/
│   │   ├── models/          # Pydantic schemas
│   │   ├── services/        # Business logic (embedding, emotion, LLM, vector, RAG)
│   │   ├── api/             # API routes
│   │   ├── utils/           # Utilities (data loader)
│   │   ├── config.py        # Configuration management
│   │   └── main.py          # FastAPI application
│   ├── data/
│   │   └── features.jsonl   # Knowledge base data
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Chat/        # Chat components
    │   │   └── UI/          # Reusable UI components
    │   ├── hooks/           # Custom React hooks
    │   ├── services/        # API client
    │   ├── types/           # TypeScript types
    │   ├── lib/             # Utilities
    │   ├── App.tsx          # Main app component
    │   └── main.tsx         # Entry point
    ├── package.json         # Node dependencies
    ├── tsconfig.json        # TypeScript config
    ├── vite.config.ts       # Vite config
    └── tailwind.config.js   # TailwindCSS config
```

## 🚀 Setup & Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Hugging Face API key (free tier available)
- Pinecone API key (free tier available)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

   Required environment variables:
   - `HUGGINGFACE_API_KEY`: Get from https://huggingface.co/settings/tokens
   - `PINECONE_API_KEY`: Get from https://www.pinecone.io/

5. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Index the data** (first time only):
   ```bash
   curl -X POST http://localhost:8000/api/index \
     -H "Content-Type: application/json" \
     -d '{"force_reindex": false}'
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if backend is not on localhost:8000
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

5. **Access the application**:
   Open http://localhost:5173 in your browser

## 📝 API Endpoints

### `GET /api/health`
Check service health and get indexed document count.

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "embedding": "operational",
    "emotion": "operational",
    "llm": "operational",
    "vector_store": "operational",
    "indexed_documents": "58"
  }
}
```

### `POST /api/query`
Query the assistant with a question.

**Request**:
```json
{
  "query": "How do I open a Datagraph chart?"
}
```

**Response**:
```json
{
  "answer": "To open a Datagraph chart for a symbol...",
  "emotion": {
    "emotion": "neutral",
    "confidence": 0.95
  },
  "sources_used": 3,
  "confidence": 0.87
}
```

### `POST /api/index`
Index or reindex the knowledge base data.

**Request**:
```json
{
  "force_reindex": false
}
```

**Response**:
```json
{
  "indexed_count": 58,
  "status": "success"
}
```

## 🔧 Configuration

### Backend Configuration (backend/.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACE_API_KEY` | Hugging Face API key (required) | - |
| `PINECONE_API_KEY` | Pinecone API key (required) | - |
| `PINECONE_ENVIRONMENT` | Pinecone region | `us-east-1` |
| `PINECONE_INDEX_NAME` | Index name | `feature-assistant` |
| `EMBEDDING_MODEL` | Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| `LLM_MODEL` | LLM model | `meta-llama/Meta-Llama-3-8B-Instruct` |
| `EMOTION_MODEL` | Emotion detection model | `bhadresh-savani/distilbert-base-uncased-emotion` |
| `TOP_K_RESULTS` | Number of results to retrieve | `3` |
| `SIMILARITY_THRESHOLD` | Minimum similarity score | `0.7` |

### Frontend Configuration (frontend/.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api` |

## 🎨 Design Principles

### SOLID Principles

1. **Single Responsibility Principle**: Each service class has one responsibility
   - `EmbeddingService`: Only handles embedding generation
   - `EmotionService`: Only handles emotion detection
   - `LLMService`: Only handles LLM inference
   - `VectorService`: Only handles vector operations
   - `RAGService`: Orchestrates the pipeline

2. **Open/Closed Principle**: Services are extensible without modification
   - New emotion mappings can be added
   - New models can be swapped via configuration

3. **Liskov Substitution Principle**: Services can be replaced with compatible implementations

4. **Interface Segregation Principle**: Clean, focused interfaces for each service

5. **Dependency Inversion Principle**: RAGService depends on abstractions (service instances)

### DRY Principles

- Reusable UI components (Button, Card, Input, etc.)
- Centralized configuration management
- Shared utility functions
- Type definitions for consistency

## 🧪 Testing the Application

### Example Queries

Try these questions to test the assistant:

1. "How do I open a Datagraph chart for a symbol?"
2. "What does the Track Price Box do?"
3. "How do I change the chart interval?"
4. "What are the keyboard shortcuts?"
5. "How do I set alerts on crosses?"

### Expected Behavior

- The assistant will detect your emotion from the query text
- It will adapt its response tone based on the detected emotion
- Responses are generated only from the provided knowledge base
- The UI displays emotion, confidence, and number of sources used

## 📊 Emotion Adaptation

The system detects emotions and adapts tone:

| Emotion | Tone |
|---------|------|
| Joy | Enthusiastic and positive |
| Sadness | Empathetic and supportive |
| Anger | Calm and understanding |
| Fear | Reassuring and gentle |
| Surprise | Informative and clear |
| Love | Warm and friendly |
| Neutral | Professional and straightforward |

## 🔒 Security Considerations

- API keys are stored in environment variables, never committed to git
- CORS is configured to allow only specified origins
- Input validation using Pydantic v2
- Error handling prevents information leakage

## 🚢 Production Deployment

### Backend

1. Use a production ASGI server (uvicorn with multiple workers)
2. Set up proper logging and monitoring
3. Use environment-specific configuration
4. Implement rate limiting
5. Add authentication if needed

Example production command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

1. Build for production:
   ```bash
   npm run build
   ```

2. Serve the `dist` folder with a web server (nginx, Apache, etc.)

3. Configure environment variables for production API URL

## 📦 Dependencies

### Backend (Python)
- fastapi - Web framework
- uvicorn - ASGI server
- pydantic - Data validation
- sentence-transformers - Embedding generation
- transformers - Emotion detection
- torch - ML backend
- pinecone-client - Vector database
- httpx - Async HTTP client

### Frontend (Node.js)
- react - UI framework
- typescript - Type safety
- vite - Build tool
- tailwindcss - Styling
- @radix-ui/* - UI primitives
- lucide-react - Icons

## 🤝 Contributing

This is a production-ready template. To extend:

1. Add more data to `backend/data/features.jsonl`
2. Customize emotion mappings in `EmotionService`
3. Add new UI components following the existing pattern
4. Implement additional API endpoints in `backend/app/api/routes.py`

## 📄 License

This project is provided as-is for educational and production use.

## 🙏 Acknowledgments

- Hugging Face for model hosting
- Pinecone for vector database
- Meta AI for Llama 3
- Sentence Transformers team
- Radix UI for accessible components
