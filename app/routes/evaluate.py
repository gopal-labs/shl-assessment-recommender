from fastapi import APIRouter
from app.services.evaluate import run_full_evaluation_suite # Import the function

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])

@router.post("/run")
async def run_eval():
    """
    Triggers the SHL Assessment Evaluation Suite.
    Reads from eval_dataset.json and returns overall metrics.
    """
    results = await run_full_evaluation_suite()
    return results