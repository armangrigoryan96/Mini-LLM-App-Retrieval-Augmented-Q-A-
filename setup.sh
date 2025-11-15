#!/bin/bash

# Setup script for PostgreSQL RAG Q&A System with Milvus

set -e

echo "=================================================="
echo "PostgreSQL RAG Q&A System - Setup Script"
echo "=================================================="

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check Docker
echo ""
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Docker Compose not found. Please install Docker Compose."
    exit 1
fi
echo "✓ Docker Compose is installed"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   Example: OPENAI_API_KEY=sk-your-key-here"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create data directory
echo ""
echo "Creating data directories..."
mkdir -p data/raw_docs

# Start Milvus
echo ""
echo "Starting Milvus vector database..."
docker-compose up -d

echo ""
echo "Waiting for Milvus to be ready (30 seconds)..."
sleep 30

echo ""
echo "=================================================="
echo "Setup complete!"
echo "=================================================="
echo ""
echo "Milvus is running:"
echo "  - Vector DB: localhost:19530"
echo "  - MinIO Console: http://localhost:9001"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and add your OpenAI API key:"
echo "   nano .env"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Scrape PostgreSQL documentation:"
echo "   python -m src.scraper"
echo ""
echo "4. Build vector database:"
echo "   python -m src.vector_store"
echo ""
echo "5. Run the application:"
echo "   streamlit run app.py"
echo ""
echo "6. (Optional) Run evaluation:"
echo "   python -m src.evaluate"
echo ""
echo "To stop Milvus:"
echo "   docker-compose down"
echo ""
echo "=================================================="
