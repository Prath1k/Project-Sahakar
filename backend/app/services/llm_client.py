import httpx
import logging

logger = logging.getLogger("LLMClient")

PROVIDER_URLS = {
    "Groq": "https://api.groq.com/openai/v1/chat/completions",
    "SambaNova": "https://api.sambanova.ai/v1/chat/completions",
    "Cerebras": "https://api.cerebras.ai/v1/chat/completions",
    "Google AI Studio": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "NVIDIA NIM": "https://integrate.api.nvidia.com/v1/chat/completions"
}

from typing import Optional

async def generate_response(prompt: str, model_id: str, provider: str, api_key: str, image_base64: Optional[str] = None) -> str:
    """
    Sends the prompt to the selected LLM provider using their OpenAI-compatible endpoint.
    """
    if not api_key or api_key == "None":
        return f"Error: No valid API key found in your .env file for {provider}."
        
    url = PROVIDER_URLS.get(provider)
    if not url:
        return f"Error: Provider {provider} not supported yet."
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    content_payload = prompt
    if image_base64:
        content_payload = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_base64}}
        ]
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": content_payload}],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"LLM API Error: {response.text}")
                return f"Error from {provider} API (Status {response.status_code}): {response.text}"
                
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"LLM Client Exception: {str(e)}")
        return f"Exception connecting to {provider}: {str(e)}"
