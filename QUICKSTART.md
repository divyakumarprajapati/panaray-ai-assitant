# 🚀 Quick Start Guide

Get the PANARAY Feature Assistant running in 5 minutes!

## Prerequisites Check

Ensure you have:
- ✅ Python 3.11+ installed (`python3 --version`)
- ✅ Node.js 18+ installed (`node --version`)
- ✅ Git installed (optional)

## Step 1: Get API Keys (2 minutes)

### Hugging Face API Key
1. Go to https://huggingface.co/
2. Sign up / Log in
3. Go to Settings → Access Tokens
4. Create a new token (read permissions are sufficient)
5. Copy the token

### Pinecone API Key
1. Go to https://www.pinecone.io/
2. Sign up for free tier
3. Create a new project
4. Go to API Keys section
5. Copy your API key

## Step 2: Automated Setup (1 minute)

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create Python virtual environment
- Install all backend dependencies
- Install all frontend dependencies
- Create .env files

## Step 3: Configure API Keys (1 minute)

Edit `backend/.env`:

```bash
nano backend/.env  # or use your favorite editor
```

Add your API keys:

```env
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Save and exit.

## Step 4: Start Backend (30 seconds)

In a terminal:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Step 5: Index Data (30 seconds)

In a new terminal:

```bash
curl -X POST http://localhost:8000/api/index \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}'
```

Wait for indexing to complete (you'll see a success message).

## Step 6: Start Frontend (30 seconds)

In another terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

## Step 7: Use the App! 🎉

1. Open http://localhost:5173 in your browser
2. Try asking: "How do I open a Datagraph chart?"
3. Watch the emotion detection and adaptive response!

## Troubleshooting

### Backend won't start
- Check API keys are correct in `backend/.env`
- Ensure Python 3.11+ is installed
- Try: `pip install -r requirements.txt` again

### Frontend won't start
- Ensure Node.js 18+ is installed
- Try: `rm -rf node_modules && npm install`

### "Model not found" error
- Wait a few minutes - models are downloading on first use
- Check your Hugging Face API key

### Indexing fails
- Verify Pinecone API key is correct
- Check if index already exists (it's okay, it will be reused)

### Can't connect to backend from frontend
- Ensure backend is running on http://localhost:8000
- Check `frontend/.env` has correct `VITE_API_URL`

## Next Steps

- Read the full README.md for detailed documentation
- Customize the knowledge base in `backend/data/features.jsonl`
- Explore the code to understand the architecture
- Add more features!

## Alternative: Manual Start

If the setup script doesn't work, follow manual steps:

### Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
uvicorn app.main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## System Requirements

**Minimum:**
- 4 GB RAM
- 2 CPU cores
- 2 GB disk space (for models cache)
- Internet connection (for API calls)

**Recommended:**
- 8 GB RAM
- 4 CPU cores
- 5 GB disk space
- Fast internet connection

## Support

For issues:
1. Check the README.md troubleshooting section
2. Review logs in the terminal
3. Ensure all dependencies are installed
4. Verify API keys are valid

Happy coding! 🚀
