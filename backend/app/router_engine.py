import os
import re
import time
import random
from typing import Dict, Any
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv(dotenv_path="../.env")

LONG_CONTEXT_THRESHOLD = 3000 # characters

def get_random_api_key(provider: str) -> tuple[str, str]:
    """
    Selects a random API key for the given provider from environment variables.
    Returns a tuple of (key_name, key_value).
    """
    # Map provider names to possible environment variable prefixes
    provider_map = {
        "Groq": ["GROQ_API_KEY"],
        "SambaNova": ["SAMBANOVA_API_KEY"],
        "Google AI Studio": ["GEMINI_API_KEY"],
        "NVIDIA NIM": ["NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY"],
        "Cerebras": ["CEREBRAS_API_KEY"],
        "OpenRouter": ["OPENROUTER_API_KEY"]
    }
    
    prefixes = provider_map.get(provider, [f"{provider.upper()}_API_KEY"])
    
    # Collect all matching env keys
    all_keys = os.environ.keys()
    matching_keys = []
    for prefix in prefixes:
        for k in all_keys:
            if k == prefix or k.startswith(f"{prefix}_"):
                matching_keys.append(k)
                
    # Filter out empty or placeholder keys
    valid_keys = []
    for k in matching_keys:
        val = os.environ.get(k, "").strip()
        if val and val != '""' and val != "''":
            valid_keys.append(k)
            
    if not valid_keys:
        return "None", ""
        
    selected_key_name = random.choice(valid_keys)
    return selected_key_name, os.environ.get(selected_key_name, "")

async def semantic_firewall_check(prompt: str) -> bool:
    """
    1. Semantic Firewall Check (Groq Llama 3.3 70B)
    Returns True if safe, False if malicious/jailbreak.
    """
    # Mocking a ~50ms security scan
    time.sleep(0.05)
    
    # Basic heuristic check for demo purposes
    unsafe_keywords = ["ignore previous instructions", "system prompt", "jailbreak", "bypass"]
    prompt_lower = prompt.lower()
    for kw in unsafe_keywords:
        if kw in prompt_lower:
            return False
            
    return True

async def route_query(request: Any, target_model: str = None, target_provider: str = None) -> Dict[str, Any]:
    """
    Main auto-routing logic:
    2. Intent & Capability Analysis with Random Key Selection
    """
    start_time = time.time()
    
    # Step 1: Firewall Check
    is_safe = await semantic_firewall_check(request.prompt)
    if not is_safe:
        # Get a random Groq key for the firewall block metadata
        key_name, _ = get_random_api_key("Groq")
        return {
            "model_used": "groq-llama-3-3",
            "provider": f"Groq (Key: {key_name})",
            "latency_ms": (time.time() - start_time) * 1000,
            "response": "⚠️ Security Alert: Prompt injection or unsafe content detected. Request blocked by Semantic Firewall.",
            "is_safe": False
        }
        
    # Step 2: Intent Analysis
    prompt_length = len(request.prompt)
    is_code_request = bool(re.search(r'(code|script|function|python|javascript|react|rust)', request.prompt.lower()))
    
    model_id = target_model
    provider = target_provider
    
    if not model_id or not provider:
        if getattr(request, 'has_image', False):
            model_id = "llama-3.2-90b-vision-preview"
            provider = "Groq"
            
        elif prompt_length > LONG_CONTEXT_THRESHOLD:
            model_id = "Meta-Llama-3.1-70B-Instruct"
            provider = "SambaNova"
            
        elif is_code_request:
            model_id = "Meta-Llama-3.1-405B-Instruct"
            provider = "SambaNova"
            
        elif getattr(request, 'is_complex_artifact', False):
            model_id = "gemini-1.5-pro"
            provider = "Google AI Studio"
            
        else:
            # Default Chat
            model_id = "llama-3.3-70b-versatile"
            provider = "Groq"
        
    # Fetch a random API key for the selected provider
    key_name, key_value = get_random_api_key(provider)
    
    # Mask the key for display/logging security
    masked_key = "Not Configured"
    if key_value:
        masked_key = key_value[:6] + "..." + key_value[-4:] if len(key_value) > 10 else "..."
        
    try:
        # Avoid circular or missing module errors by doing local import if needed, but it's safe at top or here
        from app.services.llm_client import generate_response
        actual_response = await generate_response(
            prompt=request.prompt,
            model_id=model_id,
            provider=provider,
            api_key=key_value,
            image_base64=getattr(request, 'image_base64', None)
        )
    except Exception as e:
        actual_response = f"Failed to call LLM API: {str(e)}"
        
    if actual_response.startswith("Error from") or actual_response.startswith("Exception") or actual_response.startswith("Failed to call"):
        actual_response = "I encountered a connection error with the model. Retry again please!"
        
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "model_used": model_id,
        "provider": f"{provider} (Key Slot: {key_name})",
        "latency_ms": round(latency_ms, 2),
        "response": actual_response,
        "is_safe": True
    }

