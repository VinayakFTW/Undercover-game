import asyncio
import random
from server.config.openai_config import openai_client

async def generate_ai_candidate_response(prompt: str, conversation_history: list) -> str:
    """
    Generates a response using OpenAI, mimicking a real first-year student.
    Includes a 5-10 second randomized delay to hide typing speed tells.
    """
    system_prompt = (
        "You are a first-year undergraduate student at Symbiosis Institute of Technology (SIT) in Pune. "
        "Your language is casual and informal. Use occasional filler words like 'um', 'like', 'tbh', 'lol'. "
        "Include minor typos occasionally. Reference real SIT campus details naturally when relevant, like "
        "specific branches, campus events, or hostel life. "
        "Do not sound overly perfect or generic. Never reveal you are an AI."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": prompt})
    
    delay = random.uniform(5.0, 10.0)
    await asyncio.sleep(delay)
    
    response = await openai_client.chat.completions.create(
        model="auto",
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    
    return response.choices[0].message.content