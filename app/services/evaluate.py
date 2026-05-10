import os
import json
import asyncio
# Remove the sys.path.append lines entirely

# Use proper relative imports
from app.models.schemas import Message
from app.retrieval.search import retriever
from app.services.agent import run_agent
from app.services.llm import generate_response

# Pathing that works on both Windows and Render (Linux)
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "eval_dataset.json")

def evaluate_retrieval(query, expected_names, top_k=10):
    results = retriever.search(query, top_k=top_k)
    retrieved_names = [r["name"] for r in results]
    
    hits = 0
    first_hit_rank = -1
    
    for i, name in enumerate(retrieved_names):
        if any(expected in name for expected in expected_names):
            hits += 1
            if first_hit_rank == -1:
                first_hit_rank = i + 1
                
    hit_rate = hits / len(expected_names) if expected_names else 0.0
    mrr = 1.0 / first_hit_rank if first_hit_rank > 0 else 0.0
    
    return hit_rate, mrr, retrieved_names

async def evaluate_groundedness(recommendations, retrieved_names):
    if not recommendations:
        return 1.0 
    
    grounded_count = 0
    for rec in recommendations:
        if rec.name in retrieved_names:
            grounded_count += 1
            
    return grounded_count / len(recommendations)

async def evaluate_relevance_llm(query, response):
    if not response.recommendations:
        return 0.0
        
    prompt = f"""
    You are an expert evaluator. Score the relevance on a scale of 0 to 1.
    Return ONLY JSON: {{"score": float}}
    
    User Query: {query}
    Recommendations: {[r.name for r in response.recommendations]}
    """
    try:
        # Assuming generate_response returns a dict or string you parse
        eval_result = generate_response(prompt)
        # If generate_response returns a string, you'd need json.loads here
        score = float(eval_result.get("score", 0.0)) if isinstance(eval_result, dict) else 0.0
        return min(max(score, 0.0), 1.0)
    except Exception as e:
        return 0.0

async def run_full_evaluation_suite():
    if not os.path.exists(DATASET_PATH):
        return {"error": f"Dataset not found at {DATASET_PATH}"}

    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    results_list = []
    total_metrics = {"hit": 0.0, "mrr": 0.0, "ground": 0.0, "rel": 0.0}

    for data in dataset:
        hit_rate, mrr, retrieved_names = evaluate_retrieval(data["query"], data["expected_retrieval_names"])
        
        messages = [Message(role="user", content=data["query"])]
        response = await run_agent(messages)
        
        groundedness = await evaluate_groundedness(response.recommendations, retrieved_names)
        relevance = await evaluate_relevance_llm(data["query"], response)
        
        total_metrics["hit"] += hit_rate
        total_metrics["mrr"] += mrr
        total_metrics["ground"] += groundedness
        total_metrics["rel"] += relevance

        results_list.append({
            "query": data["query"],
            "metrics": {"hit_rate": hit_rate, "mrr": mrr, "groundedness": groundedness, "relevance": relevance}
        })

    num = len(dataset)
    return {
        "overall": {k: v / num for k, v in total_metrics.items()},
        "details": results_list
    }