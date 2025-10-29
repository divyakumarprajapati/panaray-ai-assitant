# 🏗️ Architecture Documentation

## System Overview

The PANARAY Feature Assistant is a full-stack RAG (Retrieval-Augmented Generation) system with emotion detection and adaptive responses.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                   (React + TypeScript + Tailwind)               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer                             │  │
│  │  • /api/query     • /api/health    • /api/index         │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │                  RAG Service (Orchestrator)              │  │
│  └──┬─────┬─────┬──────┬─────────────────────────────────┬─┘  │
│     │     │     │      │                                  │     │
│     ▼     ▼     ▼      ▼                                  ▼     │
│  ┌────┐┌────┐┌────┐┌──────┐                          ┌──────┐ │
│  │Emb.││Emo.││LLM ││Vector│                          │Data  │ │
│  │Svc ││Svc ││Svc ││Svc   │                          │Loader│ │
│  └─┬──┘└─┬──┘└─┬──┘└──┬───┘                          └──────┘ │
└────┼─────┼─────┼──────┼──────────────────────────────────────┘
     │     │     │      │
     ▼     ▼     ▼      ▼
  ┌────────────────────────────────────────────┐
  │        External Services                   │
  │  • Hugging Face API (LLM + Emotion)       │
  │  • Sentence Transformers (Embeddings)     │
  │  • Pinecone (Vector Database)             │
  └────────────────────────────────────────────┘
```

## Component Architecture

### Backend Architecture (SOLID Design)

#### 1. Service Layer

Each service follows the **Single Responsibility Principle**:

**EmbeddingService** (`embedding_service.py`)
```
Responsibility: Generate vector embeddings
- Uses: sentence-transformers/all-MiniLM-L6-v2
- Methods: generate_embedding(), generate_embeddings_batch()
- Output: 384-dimensional vectors
```

**EmotionService** (`emotion_service.py`)
```
Responsibility: Detect emotions from text
- Uses: distilbert-base-uncased-emotion
- Methods: detect_emotion(), get_tone_for_emotion()
- Output: Emotion label + confidence score
- Maps emotions to response tones
```

**LLMService** (`llm_service.py`)
```
Responsibility: Generate responses using LLM
- Uses: Llama 3 via Hugging Face Inference API
- Methods: generate_response(), _build_prompt()
- Features: Context injection, tone adaptation
```

**VectorService** (`vector_service.py`)
```
Responsibility: Vector database operations
- Uses: Pinecone serverless
- Methods: upsert_vectors(), query_similar(), get_stats()
- Features: Batch operations, similarity search
```

**RAGService** (`rag_service.py`)
```
Responsibility: Orchestrate the RAG pipeline
- Depends on: All other services (Dependency Injection)
- Methods: process_query()
- Pipeline:
  1. Detect emotion
  2. Generate query embedding
  3. Retrieve similar documents
  4. Generate response with adapted tone
```

#### 2. API Layer

**Routes** (`api/routes.py`)
```
Endpoints:
- GET  /api/health     → Health check
- POST /api/query      → Process user query
- POST /api/index      → Index/reindex data
```

#### 3. Data Layer

**Models** (`models/schemas.py`)
```
Pydantic v2 schemas for validation:
- QueryRequest, QueryResponse
- EmotionResult
- HealthResponse, IndexDataResponse
```

**Configuration** (`config.py`)
```
Environment-based configuration:
- API keys (Hugging Face, Pinecone)
- Model names
- RAG parameters (top_k, similarity_threshold)
```

**Data Loader** (`utils/data_loader.py`)
```
Loads and prepares JSONL data:
- Parses conversation format
- Combines Q&A for better retrieval
- Prepares metadata
```

### Frontend Architecture

#### Component Hierarchy

```
App.tsx
├── Header
│   ├── Title
│   └── HealthStatus
│
├── ErrorBanner (conditional)
│
└── ChatContainer
    ├── ChatHeader
    │   ├── Title with Icon
    │   └── ClearButton
    │
    ├── ScrollArea (Messages)
    │   └── ChatMessage[] (mapped)
    │       ├── Avatar (User/Bot)
    │       ├── Content
    │       └── Metadata (emotion, sources, confidence)
    │
    └── ChatInput
        ├── Input
        └── SendButton
```

#### State Management

**useChat Hook** (`hooks/useChat.ts`)
```typescript
Manages chat state:
- messages: Message[]
- isLoading: boolean
- error: string | null

Methods:
- sendMessage(content: string)
- clearMessages()

Flow:
1. Add user message to state
2. Call API via queryAssistant()
3. Add assistant response to state
4. Handle errors gracefully
```

#### API Service

**api.ts** (`services/api.ts`)
```typescript
HTTP client for backend:
- queryAssistant(query)
- checkHealth()
- indexData(forceReindex)

Features:
- Type-safe responses
- Error handling
- Configurable base URL
```

#### UI Components

Built with **Radix UI** primitives for accessibility:

- **Button**: Multiple variants (default, secondary, outline, ghost)
- **Card**: Container with header, title, content
- **Input**: Text input with focus states
- **ScrollArea**: Smooth scrolling with custom scrollbar

#### Styling

**Tailwind CSS** with custom theme:
- CSS variables for colors
- Consistent spacing and typography
- Responsive design
- Dark mode ready (variables defined)

## Data Flow

### Query Processing Flow

```
1. User Input
   │
   ├─→ Frontend: ChatInput.tsx
   │
   ├─→ Hook: useChat.ts
   │   └─→ Add user message to state
   │
   ├─→ API: services/api.ts
   │   └─→ POST /api/query
   │
   ├─→ Backend: routes.py
   │   └─→ Validate with Pydantic
   │
   ├─→ RAGService: rag_service.py
   │   │
   │   ├─→ EmotionService
   │   │   └─→ Detect emotion + confidence
   │   │
   │   ├─→ EmbeddingService
   │   │   └─→ Generate query vector
   │   │
   │   ├─→ VectorService
   │   │   └─→ Query Pinecone for similar docs
   │   │
   │   └─→ LLMService
   │       └─→ Generate response with context + tone
   │
   ├─→ Response: QueryResponse
   │   ├─→ answer: string
   │   ├─→ emotion: EmotionResult
   │   ├─→ sources_used: int
   │   └─→ confidence: float
   │
   ├─→ Frontend: useChat.ts
   │   └─→ Add assistant message to state
   │
   └─→ UI: ChatMessage.tsx
       └─→ Display with metadata
```

### Indexing Flow

```
1. Index Request
   │
   ├─→ POST /api/index
   │
   ├─→ DataLoader
   │   └─→ Load features.jsonl
   │
   ├─→ EmbeddingService
   │   └─→ Generate embeddings for all docs
   │
   ├─→ VectorService
   │   └─→ Upsert to Pinecone
   │       ├─→ vectors: List[float]
   │       ├─→ metadata: { content, question, answer }
   │       └─→ ids: doc_0, doc_1, ...
   │
   └─→ Response: indexed_count
```

## Design Patterns

### 1. Dependency Injection

RAGService receives all dependencies in constructor:

```python
def __init__(
    self,
    embedding_service: EmbeddingService,
    emotion_service: EmotionService,
    llm_service: LLMService,
    vector_service: VectorService
)
```

Benefits:
- Testable (can mock services)
- Flexible (can swap implementations)
- Clear dependencies

### 2. Service Locator

API routes use a `get_services()` dependency:

```python
@router.post("/query")
async def query_assistant(
    request: QueryRequest,
    services: Annotated[dict, Depends(get_services)]
)
```

Benefits:
- Singleton services (created once)
- Lazy initialization
- Easy to mock in tests

### 3. Repository Pattern

VectorService abstracts Pinecone operations:

```python
# Instead of direct Pinecone calls
vector_service.upsert_vectors(vectors, metadatas)
vector_service.query_similar(vector, top_k)
```

Benefits:
- Can swap vector DB without changing business logic
- Consistent interface
- Easier testing

### 4. Custom Hook Pattern (React)

useChat hook encapsulates chat logic:

```typescript
const { messages, isLoading, sendMessage } = useChat();
```

Benefits:
- Reusable logic
- Separation of concerns
- Clean component code

## Technology Choices

### Why FastAPI?
- ✅ Async/await support
- ✅ Automatic OpenAPI docs
- ✅ Type validation with Pydantic
- ✅ High performance
- ✅ Easy dependency injection

### Why Pinecone?
- ✅ Serverless (no infrastructure)
- ✅ Fast similarity search
- ✅ Free tier available
- ✅ Simple API

### Why Llama 3?
- ✅ Strong instruction following
- ✅ Good context understanding
- ✅ Available via Hugging Face API
- ✅ Reasonable latency

### Why Sentence Transformers?
- ✅ High-quality embeddings
- ✅ Small model size (all-MiniLM-L6-v2)
- ✅ Fast inference
- ✅ Well-documented

### Why React + TypeScript?
- ✅ Type safety
- ✅ Large ecosystem
- ✅ Component reusability
- ✅ Great developer experience

### Why Radix UI?
- ✅ Accessible by default
- ✅ Unstyled (flexible styling)
- ✅ Composable primitives
- ✅ Well-maintained

### Why TailwindCSS?
- ✅ Utility-first approach
- ✅ Fast development
- ✅ Consistent design
- ✅ Small bundle size (with purge)

## Scalability Considerations

### Current Limitations

1. **Single Process**: Both frontend and backend run as single processes
2. **In-Memory State**: Service instances are in-memory
3. **No Caching**: Every query generates embeddings
4. **Rate Limits**: Hugging Face API has rate limits

### Scaling Strategies

**Horizontal Scaling:**
- Add load balancer
- Multiple FastAPI workers
- Session affinity not needed (stateless)

**Caching:**
- Redis for query embeddings
- Cache similar queries
- LRU cache for frequent questions

**Database:**
- PostgreSQL for user sessions
- Track query history
- Analytics

**Message Queue:**
- Celery for async indexing
- Background embedding generation
- Scheduled reindexing

**Monitoring:**
- Prometheus metrics
- Grafana dashboards
- Error tracking (Sentry)

## Security Considerations

### Current Implementation

✅ Environment variables for secrets
✅ CORS configuration
✅ Input validation (Pydantic)
✅ Error message sanitization

### Production Recommendations

1. **Authentication**: Add JWT tokens
2. **Rate Limiting**: Implement per-user limits
3. **HTTPS**: Use TLS in production
4. **API Key Rotation**: Rotate keys regularly
5. **Input Sanitization**: Additional validation
6. **Logging**: Audit logs for queries
7. **Secrets Management**: Use Vault or AWS Secrets Manager

## Performance Optimization

### Current Performance

- **Query latency**: 2-5 seconds (depends on LLM API)
- **Embedding generation**: ~100ms per query
- **Vector search**: ~50ms
- **Emotion detection**: ~200ms

### Optimization Opportunities

1. **Parallel Operations**: Run emotion detection + embedding in parallel
2. **Model Caching**: Cache model instances
3. **Batch Processing**: Process multiple queries together
4. **CDN**: Serve frontend from CDN
5. **Database Indexes**: Optimize Pinecone queries

## Testing Strategy

### Unit Tests

- Test each service independently
- Mock external APIs
- Test edge cases

### Integration Tests

- Test RAG pipeline end-to-end
- Test API endpoints
- Test error handling

### E2E Tests

- Test UI flows
- Test full query pipeline
- Test error states

## Future Enhancements

1. **Multi-language Support**: Translate queries and responses
2. **Voice Input**: Speech-to-text integration
3. **Document Upload**: Allow users to upload docs
4. **Conversation Memory**: Remember context across queries
5. **Admin Dashboard**: Monitor usage, performance
6. **A/B Testing**: Test different models/prompts
7. **Feedback Loop**: Learn from user feedback

---

This architecture is designed for **maintainability**, **scalability**, and **extensibility** while following industry best practices and SOLID principles.
