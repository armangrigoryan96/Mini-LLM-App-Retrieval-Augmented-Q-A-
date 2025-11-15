# Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### 1. Prerequisites Check
```bash
python3 --version  # Should be 3.8+
docker --version
docker-compose --version
```

### 2. One-Command Setup
```bash
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Start Milvus vector database
- Create `.env` file

### 3. Configure API Key
```bash
nano .env
# Add: OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Verify Setup
```bash
python verify_setup.py
```

### 5. Build Knowledge Base
```bash
# Activate venv if not already
source venv/bin/activate

# Scrape PostgreSQL docs (~2 minutes)
python -m src.scraper

# Build vector database (~3 minutes)
python -m src.vector_store
```

### 6. Launch App
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

| Task | Command |
|------|---------|
| Start Milvus | `docker-compose up -d` |
| Stop Milvus | `docker-compose down` |
| Activate env | `source venv/bin/activate` |
| Run app | `streamlit run app.py` |
| Scrape docs | `python -m src.scraper` |
| Build vectors | `python -m src.vector_store` |
| Run tests | `python tests/run_tests.py` |
| Evaluate | `python -m src.evaluate` |
| Verify setup | `python verify_setup.py` |

---

## 🐛 Troubleshooting

### Milvus won't start
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
```

### Import errors
```bash
pip install -r requirements.txt --upgrade
```

### Can't connect to Milvus
```bash
# Check if running
docker-compose ps

# Check logs
docker-compose logs milvus-standalone
```

### Port already in use
```bash
# Find process using port 19530
lsof -i :19530

# Stop the process or change port in docker-compose.yml
```

---

## 📊 Expected Results

After successful setup:
- ✅ 35 PostgreSQL docs scraped
- ✅ ~500-1000 text chunks created
- ✅ Embeddings stored in Milvus with HNSW indexing
- ✅ Streamlit app running on localhost:8501
- ✅ Can ask questions and get answers with sources
- ✅ 22 unit tests passing
- ✅ Prompts configurable via `config/prompts.yaml`

---

## ⏱️ Performance

- **Initial setup**: 5-10 minutes
- **Document scraping**: 2-3 minutes
- **Vector build**: 3-5 minutes
- **Query response**: 2-3 seconds
- **Evaluation**: 5-10 minutes (20 questions)
