import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "catalog.json")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index")
INDEX_FILE = os.path.join(INDEX_DIR, "catalog.index")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.json")

def build_index():
    print("Loading catalog data...")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Error: Raw data file {RAW_DATA_PATH} not found. Run scrape_catalog.py first.")
        return

    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print(f"Loaded {len(catalog)} assessments.")

    print("Loading SentenceTransformer model...")
    # Use a lightweight, beginner-friendly model that runs on CPU
    model = SentenceTransformer('all-MiniLM-L6-v2')

    texts_to_embed = []
    metadata = []

    for item in catalog:
        # Create a rich text representation for semantic search
        skills_str = ", ".join(item.get("skills_measured", []))
        levels_str = ", ".join(item.get("job_levels", []))
        text = f"{item['name']}. {item['description']} Role Levels: {levels_str}. Skills: {skills_str}. Category: {item['category']}."
        texts_to_embed.append(text)
        
        # Save metadata to match back after search
        metadata.append({
            "name": item["name"],
            "url": item["url"],
            "test_type": item.get("test_type", ""),
            "description": item.get("description", ""),
            "category": item.get("category", ""),
            "skills": item.get("skills_measured", []),
            "job_levels": item.get("job_levels", []),
            "duration": item.get("duration", ""),
            "languages": item.get("languages", [])
        })

    print("Generating embeddings...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    
    # FAISS requires float32
    embeddings = np.array(embeddings).astype("float32")

    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    os.makedirs(INDEX_DIR, exist_ok=True)
    
    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)

    print(f"Index built with {index.ntotal} vectors and saved to {INDEX_DIR}")

if __name__ == "__main__":
    build_index()
