# Approach Document

Hey! Here is a quick breakdown of how I built the SHL Assessment Recommender and why I made certain choices. I wanted to keep things simple, readable, and easy to debug.

## Architecture

I used FastAPI for the backend because it's super easy to set up and works well for simple endpoints. The whole app is stateless. Since the API requires the whole conversation history in every POST request anyway, I decided not to add a database for memory. This keeps the code simple and avoids dealing with session IDs.

For the RAG setup, I used FAISS (with `faiss-cpu`) to store embeddings locally. I used `sentence-transformers/all-MiniLM-L6-v2` because it's small, runs fast on CPU, and means I didn't have to pay for OpenAI's embedding API.

## Retrieval Strategy

I went with a basic hybrid search. 
1. **Semantic Search:** First, FAISS finds the top results using embeddings. This is good for matching concepts (like "cognitive" matching "reasoning").
2. **Keyword Boost:** After getting the FAISS results, I added a simple script that bumps up the score if the user's exact words are in the assessment name or description. I tried just using vector search initially, but if a user asked for exactly "OPQ32r", sometimes the vector search would put it second or third. This quick keyword boost fixed that.

## Prompting

I kept the system prompt pretty strict. The biggest challenge was stopping the LLM from inventing fake SHL assessment URLs. To fix this, I told it to *only* use the provided context and gave it the exact JSON schema it needs to return. 

I also added rules so it asks clarifying questions if the user is too vague (like just saying "I need a test"), and refuses nicely if someone asks for salary advice or something random.

## What I Simplified

- **Scraping:** The real SHL catalog is heavily loaded with JavaScript. Using just `requests` and `BeautifulSoup` wasn't getting all the data reliably. Because of time constraints, I built the scraper to make a request, but it falls back to a verified JSON dataset of the catalog. This ensures the app actually works when you test it, instead of breaking if the website layout changes.
- **Agent Framework:** I didn't use LangChain or LangGraph. For a simple "retrieve and answer" loop, those felt like overkill. I just wrote a basic python function to handle the logic flow. It's much easier to debug this way.

## Future Improvements

If I had more time, I would:
- Try a proper cross-encoder for reranking the search results. My keyword boost works okay for now, but a cross-encoder would be smarter.
- Use Playwright for the scraper to properly render the SHL catalog site.
- Add some logging so we can see what users are asking the most.
