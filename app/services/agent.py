from typing import List
from app.models.schemas import Message, ChatResponse, Recommendation
from app.retrieval.search import retriever
from app.prompts.system import AGENT_SYSTEM_PROMPT
from app.services.llm import generate_response

async def run_agent(messages: List[Message]) -> ChatResponse:
    # Get the latest message to figure out what they want right now
    if not messages:
        return ChatResponse(reply="How can I help you?", recommendations=[], end_of_conversation=False)
    
    latest_query = messages[-1].content
    
    # Put all messages together so the LLM remembers the context
    history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
    
    # We combine the last couple of messages for the search query 
    # so we don't lose context if they just say "add a personality test"
    search_query = latest_query
    if len(messages) > 2:
        user_messages = [m.content for m in messages if m.role == 'user']
        if len(user_messages) > 1:
            search_query = user_messages[-2] + " " + latest_query
            
    retrieved_items = retriever.search(search_query, top_k=10)
    
    # Format the results so the LLM can read them easily
    context_lines = []
    for i, item in enumerate(retrieved_items, 1):
        skills = ", ".join(item.get('skills', []))
        levels = ", ".join(item.get('job_levels', []))
        duration = item.get('duration', 'N/A')
        context_lines.append(f"{i}. Name: {item['name']} | Levels: {levels} | Duration: {duration} | Type: {item['test_type']} | URL: {item['url']} | Skills: {skills} | Desc: {item['description']}")
    
    context_str = "\n".join(context_lines) if context_lines else "No relevant assessments found in catalog."
    
    # Inject our search results into the prompt
    prompt = AGENT_SYSTEM_PROMPT.format(
        context=context_str,
        history=history_str
    )
    
    try:
        # Ask the LLM for a response
        llm_output = generate_response(prompt)
        
        # Sometimes the LLM might miss fields, so using .get() just in case
        reply = llm_output.get("reply", "I'm having trouble processing that.")
        recs_data = llm_output.get("recommendations", [])
        end_conv = llm_output.get("end_of_conversation", False)
        
        # Build the final list of recommendation objects
        recommendations = []
        for r in recs_data:
            recommendations.append(Recommendation(
                name=r.get("name", ""),
                url=r.get("url", ""),
                test_type=r.get("test_type", "")
            ))
            
        return ChatResponse(
            reply=reply,
            recommendations=recommendations,
            end_of_conversation=end_conv
        )
        
    except Exception as e:
        print(f"Error in agent loop: {e}")
        return ChatResponse(
            reply="An error occurred while generating the response. Please try again.",
            recommendations=[],
            end_of_conversation=False
        )
