"""
PostgreSQL Documentation Scraper and Processor

This module fetches PostgreSQL documentation pages, parses them,
chunks the text, and prepares them for embedding generation.
"""

import os
import json
import time
from typing import List, Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import html2text
from langchain_text_splitters import RecursiveCharacterTextSplitter


class PostgresDocScraper:
    """Scraper for PostgreSQL documentation pages."""
    
    URLS = [
        "https://www.postgresql.org/docs/16/sql-select.html",
        "https://www.postgresql.org/docs/16/sql-insert.html",
        "https://www.postgresql.org/docs/16/sql-update.html",
        "https://www.postgresql.org/docs/16/sql-delete.html",
        "https://www.postgresql.org/docs/16/sql-merge.html",
        "https://www.postgresql.org/docs/16/sql-create-table.html",
        "https://www.postgresql.org/docs/16/sql-alter-table.html",
        "https://www.postgresql.org/docs/16/sql-drop-table.html",
        "https://www.postgresql.org/docs/16/sql-create-index.html",
        "https://www.postgresql.org/docs/16/sql-drop-index.html",
        "https://www.postgresql.org/docs/16/sql-explain.html",
        "https://www.postgresql.org/docs/16/sql-analyze.html",
        "https://www.postgresql.org/docs/16/sql-vacuum.html",
        "https://www.postgresql.org/docs/16/sql-begin.html",
        "https://www.postgresql.org/docs/16/sql-commit.html",
        "https://www.postgresql.org/docs/16/sql-rollback.html",
        "https://www.postgresql.org/docs/16/sql-savepoint.html",
        "https://www.postgresql.org/docs/16/sql-set-transaction.html",
        "https://www.postgresql.org/docs/16/sql-create-view.html",
        "https://www.postgresql.org/docs/16/sql-refresh-materialized-view.html",
        "https://www.postgresql.org/docs/16/sql-grant.html",
        "https://www.postgresql.org/docs/16/sql-revoke.html",
        "https://www.postgresql.org/docs/16/sql-copy.html",
        "https://www.postgresql.org/docs/16/sql-truncate.html",
        "https://www.postgresql.org/docs/16/sql-set.html",
        "https://www.postgresql.org/docs/16/sql-show.html",
        "https://www.postgresql.org/docs/16/sql-create-role.html",
        "https://www.postgresql.org/docs/16/sql-alter-role.html",
        "https://www.postgresql.org/docs/16/sql-create-database.html",
        "https://www.postgresql.org/docs/16/sql-drop-database.html",
        "https://www.postgresql.org/docs/16/indexes.html",
        "https://www.postgresql.org/docs/16/indexes-partial.html",
        "https://www.postgresql.org/docs/16/ddl-constraints.html",
        "https://www.postgresql.org/docs/16/mvcc.html",
        "https://www.postgresql.org/docs/16/runtime-config.html"
    ]
    
    def __init__(self, output_dir: str = "data/raw_docs"):
        """Initialize the scraper.
        
        Args:
            output_dir: Directory to store scraped documents
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
    
    def fetch_page(self, url: str) -> Dict[str, str]:
        """Fetch and parse a single documentation page.
        
        Args:
            url: URL of the page to fetch
            
        Returns:
            Dictionary with url, title, and content
        """
        print(f"Fetching: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title = title.get_text().strip() if title else url.split('/')[-1]
            
            # Extract main content (PostgreSQL docs use div with class="sect1" or "chapter")
            content_div = soup.find('div', {'id': 'docContent'}) or soup.find('body')
            
            if content_div:
                # Remove navigation, footer, and other non-content elements
                for tag in content_div.find_all(['nav', 'footer', 'script', 'style']):
                    tag.decompose()
                
                # Convert to markdown-like text
                text_content = self.html_converter.handle(str(content_div))
            else:
                text_content = soup.get_text()
            
            # Clean up the text
            text_content = '\n'.join(line.strip() for line in text_content.split('\n') if line.strip())
            
            return {
                'url': url,
                'title': title,
                'content': text_content
            }
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return {
                'url': url,
                'title': url.split('/')[-1],
                'content': ''
            }
    
    def fetch_all(self, delay: float = 1.0, max_docs: int = None) -> List[Dict[str, str]]:
        """Fetch all documentation pages.
        
        Args:
            delay: Delay between requests in seconds
            max_docs: Maximum number of documents to fetch (None = all)
            
        Returns:
            List of document dictionaries
        """
        documents = []
        urls_to_fetch = self.URLS[:max_docs] if max_docs else self.URLS
        
        for url in urls_to_fetch:
            doc = self.fetch_page(url)
            if doc['content']:
                documents.append(doc)
                
                # Save individual document
                filename = url.split('/')[-1].replace('.html', '.json')
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(doc, f, indent=2, ensure_ascii=False)
            
            time.sleep(delay)  # Be nice to the server
        
        # Save all documents
        all_docs_path = os.path.join(self.output_dir, 'all_documents.json')
        with open(all_docs_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print(f"\nFetched {len(documents)} documents")
        return documents


class DocumentChunker:
    """Chunks documents into smaller pieces for embedding."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_documents(self, documents: List[Dict[str, str]], max_chunks_per_doc: int = None) -> List[Dict[str, str]]:
        """Chunk all documents into smaller pieces.
        
        Args:
            documents: List of document dictionaries
            max_chunks_per_doc: Maximum chunks to keep per document (None = all)
            
        Returns:
            List of chunk dictionaries with metadata
        """
        all_chunks = []
        
        for doc in documents:
            text_chunks = self.text_splitter.split_text(doc['content'])
            
            # Limit chunks per document if specified
            if max_chunks_per_doc:
                text_chunks = text_chunks[:max_chunks_per_doc]
            
            for i, chunk in enumerate(text_chunks):
                all_chunks.append({
                    'text': chunk,
                    'metadata': {
                        'source': doc['url'],
                        'title': doc['title'],
                        'chunk_id': i,
                        'total_chunks': len(text_chunks)
                    }
                })
        
        print(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks


def main():
    """Main function to scrape and process documents."""
    print("Starting PostgreSQL documentation scraper...")
    
    # Scrape documents
    scraper = PostgresDocScraper()
    documents = scraper.fetch_all(delay=0.5)
    
    if not documents:
        print("No documents fetched!")
        return
    
    # Chunk documents
    chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.chunk_documents(documents)
    
    # Save chunks
    chunks_path = os.path.join(scraper.output_dir, 'document_chunks.json')
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessing complete!")
    print(f"Documents saved to: {scraper.output_dir}")
    print(f"Total chunks: {len(chunks)}")


if __name__ == "__main__":
    main()
