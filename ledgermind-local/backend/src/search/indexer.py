import logging
import os
from typing import List, Dict, Any
from src.database.connection import db_manager
from src.search.vector_store import VectorStore
from src.search.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self, vector_store: VectorStore, embedding_client: EmbeddingClient):
        self.vector_store = vector_store
        self.embedding_client = embedding_client

    async def rebuild_index(self) -> Dict[str, int]:
        """Rebuilds the transaction-related index (merchants, categories, descriptions)."""
        # Delete only transaction-related documents
        self.vector_store.collection.delete(where={"type": {"$in": ["merchant", "category", "transaction_description"]}})
        
        counts = {
            "merchants": 0,
            "categories": 0,
            "descriptions": 0
        }
        
        conn = db_manager.get_connection()
        
        # 1. Index unique merchants
        merchants = conn.execute("SELECT DISTINCT merchant FROM transactions WHERE merchant IS NOT NULL").fetchall()
        merchant_docs = []
        merchant_metadatas = []
        merchant_ids = []
        for m in merchants:
            name = m[0]
            merchant_docs.append(name)
            merchant_metadatas.append({"type": "merchant", "merchant": name})
            merchant_ids.append(f"merchant_{name}")
        
        if merchant_docs:
            await self.vector_store.add_documents(merchant_ids, merchant_docs, merchant_metadatas, self.embedding_client)
            counts["merchants"] = len(merchant_docs)
            
        # 2. Index unique categories
        categories = conn.execute("SELECT DISTINCT category FROM transactions WHERE category IS NOT NULL").fetchall()
        category_docs = []
        category_metadatas = []
        category_ids = []
        for c in categories:
            name = c[0]
            category_docs.append(name)
            category_metadatas.append({"type": "category", "category": name})
            category_ids.append(f"category_{name}")
            
        if category_docs:
            await self.vector_store.add_documents(category_ids, category_docs, category_metadatas, self.embedding_client)
            counts["categories"] = len(category_docs)
            
        # 3. Index unique transaction descriptions
        descriptions = conn.execute("SELECT DISTINCT description, merchant, category FROM transactions").fetchall()
        desc_docs = []
        desc_metadatas = []
        desc_ids = []
        for i, (desc, merch, cat) in enumerate(descriptions):
            desc_docs.append(desc)
            desc_metadatas.append({
                "type": "transaction_description",
                "merchant": merch or "",
                "category": cat or ""
            })
            desc_ids.append(f"desc_{i}")
            
        if desc_docs:
            batch_size = 100
            for i in range(0, len(desc_docs), batch_size):
                await self.vector_store.add_documents(
                    desc_ids[i:i+batch_size], 
                    desc_docs[i:i+batch_size], 
                    desc_metadatas[i:i+batch_size], 
                    self.embedding_client
                )
            counts["descriptions"] = len(desc_docs)
            
        return counts

    async def rebuild_knowledge_index(self) -> Dict[str, int]:
        """Rebuilds the knowledge base index from markdown files."""
        # Try a few locations for docs/kb depending on where this is run from
        kb_dir = "docs/kb"
        if not os.path.exists(kb_dir):
            kb_dir = "../docs/kb"
            if not os.path.exists(kb_dir):
                # Another possibility if running from backend root
                kb_dir = "docs/kb" # already tried, but let's be explicit
                
        if not os.path.exists(kb_dir):
            logger.error(f"KB directory not found: {kb_dir}")
            return {"documents": 0}

        docs = []
        metadatas = []
        ids = []
        
        count = 0
        for filename in os.listdir(kb_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(kb_dir, filename)
                with open(file_path, "r") as f:
                    content = f.read()
                    # Split by ## headers to create chunks
                    sections = content.split("\n## ")
                    for i, section in enumerate(sections):
                        if i == 0:
                            # Title section (usually # Header)
                            text = section
                        else:
                            text = "## " + section
                        
                        docs.append(text)
                        metadatas.append({
                            "type": "knowledge_base",
                            "source": filename,
                            "section": i
                        })
                        ids.append(f"kb_{filename}_{i}")
                        count += 1
        
        if docs:
            # Delete old KB entries
            self.vector_store.collection.delete(where={"type": "knowledge_base"})
            
            await self.vector_store.add_documents(ids, docs, metadatas, self.embedding_client)
            
        return {"documents": count}
