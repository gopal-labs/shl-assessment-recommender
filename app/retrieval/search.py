import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "faiss_index")
INDEX_FILE = os.path.join(INDEX_DIR, "catalog.index")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.json")

class RetrievalSystem:
    def __init__(self):
        self.index = None
        self.metadata = []
        self.model = None
        self._load_system()

    def _load_system(self):
        if not os.path.exists(INDEX_FILE) or not os.path.exists(METADATA_FILE):
            print("Warning: FAISS index or metadata not found. Run scripts/build_index.py first.")
            return

        print("Loading FAISS index...")
        self.index = faiss.read_index(INDEX_FILE)
        
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        print("Loading SentenceTransformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, query: str, top_k: int = 5):
        if self.index is None or self.model is None:
            return []

        # Convert query into vector
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype("float32")

        # Find the closest matches in FAISS
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                item = self.metadata[idx].copy()
                item['score'] = float(distances[0][i])
                results.append(item)
                
        # Simple hack: if the user types the exact name or description keyword, 
        # give it a big boost so it shows up first.
        query_lower = query.lower()
        boosted_results = []
        for item in results:
            boost = 0
            if query_lower in item['name'].lower() or query_lower in item['description'].lower():
                boost = 10
            # FAISS L2 distance: lower is better. So subtract to make the score "better"
            item['score'] -= boost 
            boosted_results.append(item)
            
        # Re-sort everything based on the new boosted scores
        boosted_results.sort(key=lambda x: x['score'])
        
        return boosted_results

# Singleton instance
retriever = RetrievalSystem()
