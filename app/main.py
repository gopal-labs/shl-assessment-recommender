from app.routes.chat import router as chat_router
from app.routes.evaluate import router as evaluate_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router


app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational AI Agent for recommending SHL assessments.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the SHL Assessment Recommender API! Navigate to /docs for the API documentation.",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /chat",
            "evaluate": "POST /evaluate"
        }
    }

# Include routers
app.include_router(chat_router)
app.include_router(evaluate_router)
