"""
image_gen_router.py — ATLAS Image Generation Router
Uses Pollinations.ai (free, no API key required) for image generation.
Also supports FAL.ai if FAL_KEY is set in environment.
"""

import os
import httpx
import urllib.parse
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ImageGenRequest(BaseModel):
    prompt: str
    style: Optional[str] = "vivid"       # vivid, natural, anime, photorealistic
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    model: Optional[str] = "flux"         # flux, turbo, flux-realism, flux-anime
    user_id: Optional[str] = "user_sricharan_default"


@router.post("/generate", summary="Generate an image from a text prompt")
async def generate_image_endpoint(request: ImageGenRequest):
    """
    Generates an image using Pollinations.ai (free, no API key).
    Returns a direct image URL + base64-encoded image data.
    
    Model options: flux, turbo, flux-realism, flux-anime, flux-3d
    Style options: vivid, natural, anime, photorealistic, cinematic
    """
    try:
        # Build Pollinations.ai URL (completely free, no API key needed)
        # Format: https://image.pollinations.ai/prompt/{encoded_prompt}?model={model}&width={w}&height={h}&nologo=true
        
        # Enrich the prompt with style if specified
        enriched_prompt = request.prompt
        style_map = {
            "vivid": "vivid, high contrast, dramatic lighting, ultra-detailed",
            "natural": "natural lighting, photorealistic, realistic colors",
            "anime": "anime style, studio ghibli, cel shaded, vibrant",
            "photorealistic": "photorealistic, DSLR photo, 8K, hyperdetailed",
            "cinematic": "cinematic, film grain, anamorphic lens, epic composition"
        }
        if request.style and request.style in style_map:
            enriched_prompt = f"{request.prompt}, {style_map[request.style]}"
        
        encoded_prompt = urllib.parse.quote(enriched_prompt)
        model = request.model or "flux"
        width = min(max(request.width or 1024, 256), 1920)
        height = min(max(request.height or 1024, 256), 1920)
        
        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?model={model}&width={width}&height={height}&nologo=true&enhance=true"
        )
        
        # Fetch the image to verify it works and return base64
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(image_url)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f"Image generation failed: HTTP {response.status_code}")
            
            image_bytes = response.content
            import base64
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            content_type = response.headers.get("content-type", "image/jpeg")
            
        return {
            "success": True,
            "prompt": request.prompt,
            "enriched_prompt": enriched_prompt,
            "model": model,
            "style": request.style,
            "width": width,
            "height": height,
            "image_url": image_url,
            "image_base64": f"data:{content_type};base64,{image_b64}",
            "provider": "Pollinations.ai (FLUX)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")


@router.get("/models", summary="List available image generation models")
async def list_image_models():
    """Returns all available image generation models on Pollinations.ai"""
    return {
        "provider": "Pollinations.ai",
        "models": [
            {"id": "flux", "name": "FLUX", "description": "Best quality, detailed outputs"},
            {"id": "flux-realism", "name": "FLUX Realism", "description": "Photorealistic images"},
            {"id": "flux-anime", "name": "FLUX Anime", "description": "Anime & illustration style"},
            {"id": "flux-3d", "name": "FLUX 3D", "description": "3D rendered style"},
            {"id": "turbo", "name": "FLUX Turbo", "description": "Fast generation, lower quality"},
        ],
        "styles": ["vivid", "natural", "anime", "photorealistic", "cinematic"]
    }
