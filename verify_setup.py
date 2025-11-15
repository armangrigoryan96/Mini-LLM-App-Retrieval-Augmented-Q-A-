#!/usr/bin/env python3
"""
Verification script to check if the RAG project is properly configured
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version >= 3.8"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"  ✗ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_project_structure():
    """Check if all required folders exist"""
    print("\n✓ Checking project structure...")
    required_dirs = ['src', 'data', 'config', 'tests']
    required_files = [
        'app.py',
        'requirements.txt',
        'docker-compose.yml',
        '.env.example',
        'README.md',
        'src/__init__.py',
        'src/scraper.py',
        'src/vector_store.py',
        'src/rag_pipeline.py',
        'src/evaluate.py',
        'src/qa_dataset.py'
    ]
    
    all_good = True
    for dir_name in required_dirs:
        if not Path(dir_name).is_dir():
            print(f"  ✗ Missing directory: {dir_name}")
            all_good = False
        else:
            print(f"  ✓ {dir_name}/")
    
    for file_name in required_files:
        if not Path(file_name).is_file():
            print(f"  ✗ Missing file: {file_name}")
            all_good = False
        else:
            print(f"  ✓ {file_name}")
    
    return all_good

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n✓ Checking Python dependencies...")
    required_packages = [
        'streamlit',
        'pymilvus',
        'sentence_transformers',
        'langchain',
        'langchain_openai',
        'beautifulsoup4',
        'requests',
        'numpy',
        'sklearn',
        'dotenv'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                __import__('bs4')
            elif package == 'sklearn':
                __import__('sklearn')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} not installed")
            all_good = False
    
    return all_good

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n✓ Checking environment configuration...")
    
    if not Path('.env').is_file():
        print("  ⚠️  .env file not found (use .env.example as template)")
        return False
    
    print("  ✓ .env file exists")
    
    with open('.env', 'r') as f:
        content = f.read()
        
    required_vars = ['OPENAI_API_KEY']
    all_good = True
    
    for var in required_vars:
        if var in content:
            # Check if it's not the placeholder
            if 'your_openai_api_key_here' in content or 'your-key-here' in content:
                print(f"  ⚠️  {var} needs to be set (currently using placeholder)")
                all_good = False
            else:
                print(f"  ✓ {var} is set")
        else:
            print(f"  ✗ {var} not found in .env")
            all_good = False
    
    return all_good

def check_docker():
    """Check if Docker and Docker Compose are available"""
    print("\n✓ Checking Docker...")
    import subprocess
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✓ {result.stdout.strip()}")
        else:
            print("  ✗ Docker not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ✗ Docker not found")
        return False
    
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✓ {result.stdout.strip()}")
        else:
            print("  ✗ Docker Compose not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  ✗ Docker Compose not found")
        return False
    
    return True

def check_milvus():
    """Check if Milvus is running"""
    print("\n✓ Checking Milvus connection...")
    try:
        from pymilvus import connections, utility
        
        connections.connect(
            alias="default",
            host="localhost",
            port="19530",
            timeout=5
        )
        
        print("  ✓ Successfully connected to Milvus")
        
        # Check if collection exists
        if utility.has_collection("postgres_docs"):
            collection_info = utility.get_collection_stats("postgres_docs")
            print(f"  ✓ Collection 'postgres_docs' found")
        else:
            print("  ⚠️  Collection 'postgres_docs' not found (run: python -m src.vector_store)")
        
        connections.disconnect("default")
        return True
        
    except Exception as e:
        print(f"  ✗ Cannot connect to Milvus: {e}")
        print("  ℹ️  Run: docker-compose up -d")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("PostgreSQL RAG Q&A System - Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Python Dependencies", check_dependencies),
        ("Environment Configuration", check_env_file),
        ("Docker", check_docker),
        ("Milvus Vector Database", check_milvus),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All checks passed! System is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python -m src.scraper (if not done)")
        print("  2. Run: python -m src.vector_store (if not done)")
        print("  3. Run: streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
