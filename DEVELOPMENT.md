# 🛠️ Development Guide

This guide is for developers who want to understand, modify, or extend the PANARAY Feature Assistant.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Code Style & Standards](#code-style--standards)
4. [Adding New Features](#adding-new-features)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

## Development Setup

### Backend Development

1. **Install development dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install pytest black flake8 mypy  # Optional dev tools
   ```

2. **Enable hot reload**:
   ```bash
   uvicorn app.main:app --reload --log-level debug
   ```

3. **View API docs**:
   - OpenAPI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Development

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start dev server with HMR**:
   ```bash
   npm run dev
   ```

3. **TypeScript checking**:
   ```bash
   npm run build  # Compiles and checks types
   ```

## Project Structure

### Backend (`/workspace/backend/`)

```
backend/
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI app, CORS, lifespan
│   ├── config.py             # Settings management (Pydantic)
│   │
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   └── schemas.py        # Request/response schemas
│   │
│   ├── services/             # Business logic (SOLID)
│   │   ├── __init__.py
│   │   ├── embedding_service.py    # Sentence Transformers
│   │   ├── llm_service.py          # Llama 3 inference
│   │   ├── vector_service.py       # Pinecone operations
│   │   └── rag_service.py          # RAG orchestration
│   │
│   ├── api/                  # HTTP endpoints
│   │   ├── __init__.py
│   │   └── routes.py         # Query, health, index endpoints
│   │
│   └── utils/                # Utilities
│       ├── __init__.py
│       └── data_loader.py    # JSONL data loading
│
├── data/
│   └── features.jsonl        # Knowledge base
│
├── requirements.txt          # Python dependencies
└── .env.example              # Environment template
```

### Frontend (`/workspace/frontend/`)

```
frontend/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Root component
│   ├── index.css             # Global styles, Tailwind
│   │
│   ├── components/           # React components
│   │   ├── Chat/
│   │   │   ├── ChatContainer.tsx   # Main chat UI
│   │   │   ├── ChatMessage.tsx     # Message display
│   │   │   └── ChatInput.tsx       # Input field
│   │   │
│   │   └── UI/               # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Input.tsx
│   │       └── ScrollArea.tsx
│   │
│   ├── hooks/                # Custom React hooks
│   │   └── useChat.ts        # Chat state management
│   │
│   ├── services/             # API communication
│   │   └── api.ts            # HTTP client
│   │
│   ├── types/                # TypeScript types
│   │   └── index.ts          # Shared types
│   │
│   └── lib/                  # Utilities
│       └── utils.ts          # Helper functions
│
├── index.html                # HTML template
├── package.json              # Node dependencies
├── tsconfig.json             # TypeScript config
├── vite.config.ts            # Vite config
├── tailwind.config.js        # Tailwind config
└── postcss.config.js         # PostCSS config
```

## Code Style & Standards

### Python (Backend)

**Style Guide**: PEP 8

**Key Conventions**:
- 4 spaces indentation
- Max line length: 100 characters
- Type hints everywhere
- Docstrings for public methods
- Descriptive variable names

**Example**:
```python
async def process_query(self, query: str) -> QueryResponse:
    """Process a user query through the RAG pipeline.
    
    Args:
        query: User's question
        
    Returns:
        QueryResponse with answer and metadata
    """
    # Implementation
```

**Tools**:
```bash
# Format code
black app/

# Check style
flake8 app/

# Type check
mypy app/
```

### TypeScript (Frontend)

**Style Guide**: Airbnb (modified)

**Key Conventions**:
- 2 spaces indentation
- Single quotes for strings
- Semicolons required
- Interfaces for object shapes
- Functional components with hooks

**Example**:
```typescript
interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
}

export function ChatInput({ onSend, disabled, isLoading }: ChatInputProps) {
  // Implementation
}
```

**Tools**:
```bash
# Lint
npm run lint

# Type check
npm run build
```

### Component Structure

**React Component Template**:
```typescript
/**
 * Component description
 */

import { useState } from 'react';
import { ComponentProps } from '@/types';

interface MyComponentProps {
  // Props
}

export function MyComponent({ prop1, prop2 }: MyComponentProps) {
  // Hooks
  const [state, setState] = useState();

  // Event handlers
  const handleClick = () => {
    // Logic
  };

  // Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

## Adding New Features

### 1. Add New Backend Service

**Example**: Add a translation service

1. Create `app/services/translation_service.py`:
   ```python
   class TranslationService:
       """Service for translating text."""
       
       def __init__(self):
           # Initialize translation model
           pass
       
       def translate(self, text: str, target_lang: str) -> str:
           """Translate text to target language."""
           # Implementation
           pass
   ```

2. Update `app/services/__init__.py`:
   ```python
   from .translation_service import TranslationService
   
   __all__ = [..., "TranslationService"]
   ```

3. Inject into RAGService:
   ```python
   def __init__(
       self,
       # ... existing services
       translation_service: TranslationService
   ):
       self._translation_service = translation_service
   ```

4. Update `routes.py` to create instance:
   ```python
   _services["translation"] = TranslationService()
   ```

### 2. Add New API Endpoint

**Example**: Add a feedback endpoint

1. Add schema to `models/schemas.py`:
   ```python
   class FeedbackRequest(BaseModel):
       query_id: str
       rating: int = Field(..., ge=1, le=5)
       comment: str = ""
   ```

2. Add route to `api/routes.py`:
   ```python
   @router.post("/feedback")
   async def submit_feedback(request: FeedbackRequest):
       # Process feedback
       return {"status": "success"}
   ```

### 3. Add New UI Component

**Example**: Add a rating widget

1. Create `components/UI/Rating.tsx`:
   ```typescript
   interface RatingProps {
     value: number;
     onChange: (value: number) => void;
   }
   
   export function Rating({ value, onChange }: RatingProps) {
     // Component logic
   }
   ```

2. Use in parent component:
   ```typescript
   import { Rating } from '@/components/UI/Rating';
   
   function MyComponent() {
     const [rating, setRating] = useState(0);
     
     return <Rating value={rating} onChange={setRating} />;
   }
   ```

### 4. Customize Knowledge Base

1. **Edit data file** (`backend/data/features.jsonl`):
   ```json
   {"messages": [
     {"role": "system", "content": "System prompt..."},
     {"role": "user", "content": "Question?"},
     {"role": "assistant", "content": "Answer."}
   ]}
   ```

2. **Reindex**:
   ```bash
   curl -X POST http://localhost:8000/api/index \
     -H "Content-Type: application/json" \
     -d '{"force_reindex": true}'
   ```

## Testing

### Backend Tests

**Create** `backend/tests/test_services.py`:
```python
import pytest
from app.services import EmbeddingService

@pytest.fixture
def embedding_service():
    return EmbeddingService()

def test_generate_embedding(embedding_service):
    text = "test query"
    embedding = embedding_service.generate_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(x, float) for x in embedding)
```

**Run tests**:
```bash
cd backend
pytest tests/
```

### Frontend Tests

**Create** `frontend/src/components/__tests__/Button.test.tsx`:
```typescript
import { render, screen } from '@testing-library/react';
import { Button } from '../UI/Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
```

**Run tests**:
```bash
cd frontend
npm test
```

## Debugging

### Backend Debugging

**Enable debug logging**:
```python
# In main.py
logging.basicConfig(level=logging.DEBUG)
```

**Use debugger**:
```python
import pdb; pdb.set_trace()  # Breakpoint
```

**View logs**:
```bash
uvicorn app.main:app --reload --log-level debug
```

### Frontend Debugging

**Browser DevTools**:
- Console: `console.log()`, `console.error()`
- Network tab: Check API calls
- React DevTools: Inspect component state

**VS Code debugging**:
```json
// .vscode/launch.json
{
  "type": "chrome",
  "request": "launch",
  "name": "Debug Frontend",
  "url": "http://localhost:5173",
  "webRoot": "${workspaceFolder}/frontend/src"
}
```

### Common Debug Tasks

**Check vector similarity**:
```python
# In Python shell
from app.services import EmbeddingService, VectorService

embedding_svc = EmbeddingService()
vector_svc = VectorService()

query = "How do I open a chart?"
vector = embedding_svc.generate_embedding(query)
results = vector_svc.query_similar(vector, top_k=5)

for r in results:
    print(f"Score: {r['score']:.2f}")
    print(f"Content: {r['metadata']['content'][:100]}...")
```

**Test LLM prompt**:
```python
from app.services import LLMService

llm_svc = LLMService()
response = await llm_svc.generate_response(
    query="test",
    context=[{"content": "test context"}],
    tone="professional"
)
print(response)
```

## Common Tasks

### Update Embedding Model

1. Change in `.env`:
   ```env
   EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
   ```

2. Update dimension in config if needed:
   ```env
   PINECONE_DIMENSION=768  # mpnet dimension
   ```

3. Force reindex:
   ```bash
   curl -X POST http://localhost:8000/api/index \
     -d '{"force_reindex": true}'
   ```

### Change LLM Model

1. Update in `.env`:
   ```env
   LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.1
   ```

2. Adjust prompt template in `llm_service.py` if needed

### Customize UI Theme

1. Edit `frontend/tailwind.config.js`:
   ```javascript
   theme: {
     extend: {
       colors: {
         primary: {
           DEFAULT: "hsl(220, 90%, 56%)",  // Custom blue
         },
       },
     },
   }
   ```

2. Update CSS variables in `index.css`

## Troubleshooting

### Backend Issues

**Problem**: Model downloads are slow
**Solution**: Pre-download models:
```python
from sentence_transformers import SentenceTransformer

SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

**Problem**: Pinecone index errors
**Solution**: Delete and recreate:
```python
from app.services import VectorService
vector_svc = VectorService()
# Delete via Pinecone console, then restart
```

**Problem**: Out of memory
**Solution**: Reduce batch size in `embedding_service.py`

### Frontend Issues

**Problem**: Module not found errors
**Solution**: Check path aliases in `tsconfig.json` and `vite.config.ts`

**Problem**: Styles not applying
**Solution**: Ensure Tailwind directives are in `index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Problem**: API calls failing
**Solution**: Check CORS settings in `backend/app/main.py`

## Performance Profiling

### Backend Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Frontend Profiling

Use React DevTools Profiler:
1. Open React DevTools
2. Go to Profiler tab
3. Record interaction
4. Analyze render times

## Best Practices

### Backend

1. **Always use type hints**
2. **Handle errors gracefully**
3. **Log important events**
4. **Validate inputs with Pydantic**
5. **Use async/await for I/O operations**
6. **Keep services focused (SRP)**

### Frontend

1. **Use TypeScript strictly**
2. **Memoize expensive computations**
3. **Split code with lazy loading**
4. **Handle loading and error states**
5. **Keep components small and focused**
6. **Use custom hooks for reusable logic**

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Radix UI Docs](https://www.radix-ui.com/)
- [Pinecone Docs](https://docs.pinecone.io/)

---

Happy coding! 🚀
