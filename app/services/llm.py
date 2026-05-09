import os
import json
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

def generate_response(prompt: str) -> dict:
    if LLM_PROVIDER == "gemini":
        return _generate_with_gemini(prompt)
    else:
        return _generate_with_openai(prompt)

def _generate_with_openai(prompt: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    return json.loads(content)

def _generate_with_gemini(prompt: str) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel(
        'gemini-2.5-flash-lite',
        generation_config={"response_mime_type": "application/json"}
    )
    
    response = model.generate_content(prompt)
    return json.loads(response.text)
