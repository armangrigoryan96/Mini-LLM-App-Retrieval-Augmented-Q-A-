# Quick Start Guide

## 🚀 Fast Setup with Docker (2 minutes)

### 1. Prerequisites Check
```bash
docker --version
docker compose version  # or docker-compose --version
```

### 2. Configure API Key
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use any text editor
# Add: OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Start Application
```bash
docker compose up -d --build
```

This will:
- Build the application Docker image
- Start Milvus vector database
- Start all supporting services (etcd, MinIO)
- Launch the Streamlit app

Wait ~1 minute for all services to be ready.

### 4. Access Application
```bash
# Open in browser
http://localhost:8501
```

**First Launch**: The system will automatically:
1. Detect empty vector database
2. Fetch PostgreSQL documentation (2 docs by default for cost control)
3. Build vector database with embeddings
4. Be ready for questions!

---

## 🔧 Alternative: Local Development Setup

### 1. Prerequisites Check
```bash
python3 --version  # Should be 3.8+
docker --version
```

### 2. Start Milvus Services Only
```bash
docker compose up -d etcd minio standalone
```

### 3. Setup Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure API Key
```bash
cp .env.example .env
nano .env
# Add: OPENAI_API_KEY=sk-your-actual-key-here
```

### 5. Launch App Locally
```bash
streamlit run app.py
```

Open browser to: http://localhost:8501

---

## 🔧 Manual Setup (if needed)

### Start Milvus Only
```bash
docker-compose up -d
```

### Stop Milvus
```bash
docker-compose down
```

### Rebuild Vector Store
```bash
python -m src.vector_store
# Answer 'yes' when prompted to rebuild
```

### Run Unit Tests
```bash
python tests/run_tests.py
# or with pytest
pytest tests/ -v
```

### Run Evaluation
```bash
python -m src.evaluate
```

---

## 📝 Common Commands

### Docker Deployment
| Task | Command |
|------|---------|
| Start all services | `docker compose up -d` |
| Stop all services | `docker compose down` |
| View logs | `docker compose logs -f app` |
| Restart app | `docker compose restart app` |
| Rebuild app | `docker compose up -d --build app` |
| Check status | `docker compose ps` |

### Local Development
| Task | Command |
|------|---------|
| Start Milvus only | `docker compose up -d etcd minio standalone` |
| Stop Milvus | `docker compose down` |
| Activate env | `source venv/bin/activate` |
| Run app locally | `streamlit run app.py` |
| Scrape docs | `python -m src.scraper` |
| Build vectors | `python -m src.vector_store` |
| Run tests | `python tests/run_tests.py` |
| Evaluate | `python -m src.evaluate` |

---

## 🐛 Troubleshooting

### App won't start
```bash
# Check logs
docker compose logs -f app

# Restart services
docker compose restart app

# Rebuild from scratch
docker compose down
docker compose up -d --build
```

### Milvus won't start
```bash
docker compose down -v  # Remove volumes
docker compose up -d
```

### Import errors (local development)
```bash
pip install -r requirements.txt --upgrade
```

### Can't connect to Milvus
```bash
# Check if running
docker compose ps

# Check logs
docker compose logs milvus-standalone

# For Docker app, ensure MILVUS_HOST=milvus-standalone in .env
# For local app, ensure MILVUS_HOST=localhost (or comment out)
```

### Port already in use
```bash
# For port 8501 (Streamlit)
lsof -i :8501
docker compose stop app

# For port 19530 (Milvus)
lsof -i :19530
docker compose stop standalone
```

### Permission denied on volumes
```bash
# Clean up volumes and rebuild
docker compose down -v
sudo rm -rf volumes/
docker compose up -d --build
```

---

## 📊 Expected Results

### Docker Deployment
After successful setup:
- ✅ 4 Docker containers running (app, milvus, etcd, minio)
- ✅ Streamlit app accessible at localhost:8501
- ✅ Automatic vector database build on first launch (2 docs by default)
- ✅ Can ask questions and get answers with sources
- ✅ Chat history maintained across questions
- ✅ Source citations with relevance scores

### Full Setup (All 35 docs)
To build full knowledge base, update `.env`:
```bash
MAX_DOCS=0  # or remove this line
MAX_CHUNKS_PER_DOC=0  # or remove this line
```
Then restart: `docker compose restart app`

Expected results:
- ✅ 35 PostgreSQL docs scraped
- ✅ ~500-1000 text chunks created
- ✅ Embeddings stored in Milvus with HNSW indexing
- ✅ Higher quality answers with more context
- ✅ Better coverage of PostgreSQL topics

---

## ⏱️ Performance

### Docker Deployment
- **Initial setup**: 2-3 minutes
- **First launch (auto-build)**: 3-5 minutes (2 docs)
- **First launch (full)**: 10-15 minutes (35 docs)
- **Subsequent launches**: < 10 seconds
- **Query response**: 2-3 seconds

### Local Development
- **Initial setup**: 5-10 minutes
- **Document scraping**: 2-3 minutes
- **Vector build**: 3-5 minutes
- **Query response**: 2-3 seconds
- **Evaluation**: 5-10 minutes (20 questions)
