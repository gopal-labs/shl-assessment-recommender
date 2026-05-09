# SHL Assessment Recommender

Hi! This is my submission for the SHL AI Intern assignment. It's a chatbot API that helps users figure out which SHL assessment they should use for hiring.

I used FastAPI, a local FAISS index for searching the catalog, and an LLM (either OpenAI or Gemini) to generate the responses.

## How to run it locally

1. **Clone the repo** and go to the project folder.
2. **Make a virtual environment** (this is optional but keeps things clean):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or on Windows use: venv\Scripts\activate
   ```
3. **Install the packages**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up the environment variables**:
   Copy the example file and add your API key:
   ```bash
   cp .env.example .env
   ```
   In `.env`, you can set `LLM_PROVIDER=openai` (or `gemini`) and put your API key there.

5. **Load the data**:
   Run these scripts to load the catalog data and build the FAISS index so the bot has something to search through:
   ```bash
   python scripts/scrape_catalog.py
   python scripts/build_index.py
   ```

6. **Start the API**:
   ```bash
   uvicorn app.main:app --reload
   ```

## How to test the API

You can check if the server is running by hitting the health endpoint:
```bash
curl http://localhost:8000/health
```

To chat with the bot, send a POST request with your conversation history:
```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{
  "messages": [
    {"role": "user", "content": "I need a cognitive test for a senior technical hire."}
  ]
}'
```

The response will look something like this:
```json
{
  "reply": "For a senior technical hire, I recommend the SHL Verify Interactive G+. It covers inductive, numerical, and deductive reasoning in a single adaptive test.",
  "recommendations": [
    {
      "name": "SHL Verify Interactive G+",
      "url": "https://www.shl.com/products/product-catalog/view/shl-verify-interactive-g/",
      "test_type": "A"
    }
  ],
  "end_of_conversation": false
}
```

## Running the tests

I wrote some pytest tests to make sure the API returns the right JSON format and handles empty histories properly. Run them with:
```bash
python -m pytest tests/
```

## Deployment

I set this up to be easily deployed on Render's free tier. 
If you connect this repo to Render, it should pick up the `render.yaml` file automatically. Just don't forget to add your `OPENAI_API_KEY` or `GEMINI_API_KEY` in the Render dashboard!

If you want to read more about why I built it this way, check out `approach_document.md`.
