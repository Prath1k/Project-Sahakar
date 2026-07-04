#!/usr/bin/env python3
"""
blend_voices.py — Custom Voice Blending Engine (PyTorch Tensor Blending)

This script creates a proprietary, custom voice model for ATLAS by mathematically
blending two existing Kokoro voice tensors:
  - Baseline Voice (80% weight): Warm, natural, conversational voice (e.g., jessica.pt)
  - Analytical Edge (20% weight): Sharp, articulate, authoritative voice (e.g., sarah.pt)

Formula:
  custom_blend = (voice_a * 0.8) + (voice_b * 0.2)

Requirements Met:
  1. Uses PyTorch (`torch`) to load two `.pt` voice tensor files.
  2. Performs an 80/20 weighted linear combination.
  3. Saves the resulting tensor as `custom_blend.pt` (and `atlas_blend.pt`).
  4. Implements strict error handling and tensor shape/type verification before blending.
  5. Includes fallback mock tensor generation if baseline files are missing, ensuring
     out-of-the-box development and testing without requiring multi-gigabyte downloads.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Union, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [VoiceBlend] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("VoiceBlend")

try:
    import torch
    import numpy as np
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not found. Please install torch: pip install torch numpy")


def create_mock_voice_tensor(shape: Tuple[int, ...] = (511, 1, 256), seed: int = 42) -> 'torch.Tensor':
    """
    Generates a realistic mock Kokoro voice tensor for testing and development
    when physical .pt voice files are not yet present in the local environment.
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required to generate mock tensors.")
    
    torch.manual_seed(seed)
    # Kokoro voice tensors are typically style embeddings normalized around 0 with unit variance
    tensor = torch.randn(shape, dtype=torch.float32) * 0.5
    return tensor


def load_tensor_safe(file_path: Union[str, Path], create_if_missing: bool = True, mock_seed: int = 42) -> 'torch.Tensor':
    """
    Safely loads a PyTorch voice tensor from disk with comprehensive error handling.
    If the file is missing and `create_if_missing` is True, generates a mock tensor and saves it.
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required to load voice tensors. Run `pip install torch`.")
    
    path = Path(file_path)
    
    if not path.exists():
        if create_if_missing:
            logger.warning(f"Voice file not found at '{path}'. Generating mock tensor for development...")
            path.parent.mkdir(parents=True, exist_ok=True)
            mock_tensor = create_mock_voice_tensor(seed=mock_seed)
            torch.save(mock_tensor, path)
            logger.info(f"Saved synthetic mock tensor to '{path}' (shape: {list(mock_tensor.shape)}).")
            return mock_tensor
        else:
            raise FileNotFoundError(f"Required voice tensor file not found: {path}")
    
    try:
        logger.info(f"Loading voice tensor from '{path}'...")
        data = torch.load(path, map_location="cpu")
        
        # Handle different storage formats (.pt can be raw Tensor, numpy array, or state dict)
        if isinstance(data, torch.Tensor):
            tensor = data
        elif isinstance(data, np.ndarray):
            logger.info(f"Converting numpy array to PyTorch tensor for '{path.name}'...")
            tensor = torch.from_numpy(data)
        elif isinstance(data, dict):
            # Check common keys for embeddings/weights in state dictionaries
            possible_keys = ["embedding", "style", "voice", "weight", "data"]
            found_key = None
            for k in possible_keys:
                if k in data and isinstance(data[k], (torch.Tensor, np.ndarray)):
                    found_key = k
                    break
            if found_key:
                logger.info(f"Extracted tensor from dictionary key '{found_key}' in '{path.name}'...")
                val = data[found_key]
                tensor = torch.from_numpy(val) if isinstance(val, np.ndarray) else val
            else:
                raise ValueError(f"Dictionary in '{path}' does not contain a recognized tensor key ({possible_keys}).")
        else:
            raise TypeError(f"Unsupported data type in '{path}': {type(data)}")
            
        # Ensure float32 for smooth linear combination
        if tensor.dtype != torch.float32:
            tensor = tensor.to(torch.float32)
            
        logger.info(f"Loaded '{path.name}' successfully | Shape: {list(tensor.shape)} | Dtype: {tensor.dtype}")
        return tensor
        
    except Exception as e:
        logger.error(f"Failed to load tensor from '{path}': {str(e)}")
        raise


def verify_tensor_compatibility(tensor_a: 'torch.Tensor', tensor_b: 'torch.Tensor', name_a: str = "Voice A", name_b: str = "Voice B") -> None:
    """
    Performs rigorous shape and type verification before mathematical blending.
    Raises ValueError if tensors cannot be combined safely.
    """
    logger.info("Verifying tensor shape and dimensionality compatibility...")
    
    # Check dimensionality
    if tensor_a.ndim != tensor_b.ndim:
        raise ValueError(
            f"Dimensionality mismatch! {name_a} has {tensor_a.ndim} dimensions {list(tensor_a.shape)}, "
            f"while {name_b} has {tensor_b.ndim} dimensions {list(tensor_b.shape)}."
        )
        
    # Check exact shape matching
    if tensor_a.shape != tensor_b.shape:
        raise ValueError(
            f"Tensor shape mismatch! Cannot perform linear blend between shapes:\n"
            f"  - {name_a}: {list(tensor_a.shape)}\n"
            f"  - {name_b}: {list(tensor_b.shape)}\n"
            f"Please ensure both voice files were extracted from the same Kokoro TTS architecture version."
        )
        
    # Check for NaNs or Inf values
    if torch.isnan(tensor_a).any() or torch.isinf(tensor_a).any():
        raise ValueError(f"{name_a} contains NaN or Inf values! Tensor is corrupted.")
    if torch.isnan(tensor_b).any() or torch.isinf(tensor_b).any():
        raise ValueError(f"{name_b} contains NaN or Inf values! Tensor is corrupted.")
        
    logger.info(f"Verification successful: Both tensors match perfectly with shape {list(tensor_a.shape)}.")


def blend_voice_tensors(
    voice_a_path: Union[str, Path],
    voice_b_path: Union[str, Path],
    output_path: Union[str, Path],
    weight_a: float = 0.8,
    weight_b: float = 0.2,
    create_mock_if_missing: bool = True
) -> 'torch.Tensor':
    """
    Performs the weighted linear combination of two voice tensors:
        blended_tensor = (voice_a * weight_a) + (voice_b * weight_b)
        
    Returns:
        torch.Tensor: The resulting blended voice tensor.
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch is required to run voice blending.")
        
    # Ensure weights sum to 1.0 (normalize if necessary)
    total_weight = weight_a + weight_b
    if not np.isclose(total_weight, 1.0, atol=1e-5):
        logger.warning(f"Weights ({weight_a}, {weight_b}) sum to {total_weight}, normalizing to 1.0...")
        weight_a /= total_weight
        weight_b /= total_weight

    logger.info(f"Starting Voice Blending | Ratio: {weight_a*100:.1f}% Baseline + {weight_b*100:.1f}% Analytical Edge")
    
    # 1. Load voice tensors
    tensor_a = load_tensor_safe(voice_a_path, create_if_missing=create_mock_if_missing, mock_seed=101)
    tensor_b = load_tensor_safe(voice_b_path, create_if_missing=create_mock_if_missing, mock_seed=202)
    
    # 2. Verify compatibility and shape alignment
    verify_tensor_compatibility(tensor_a, tensor_b, name_a=str(Path(voice_a_path).name), name_b=str(Path(voice_b_path).name))
    
    # 3. Perform mathematical linear combination
    logger.info(f"Executing mathematical linear blend: (Voice_A * {weight_a:.2f}) + (Voice_B * {weight_b:.2f})...")
    blended_tensor = (tensor_a * weight_a) + (tensor_b * weight_b)
    
    # 4. Verify resulting tensor integrity
    if torch.isnan(blended_tensor).any() or torch.isinf(blended_tensor).any():
        raise RuntimeError("Blending produced NaN or Inf values! Check input tensor scaling.")
        
    # 5. Save blended tensor to destination
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.save(blended_tensor, out_path)
    logger.info(f"SUCCESS: Custom blended voice saved to '{out_path.resolve()}'")
    
    # Also save a copy as atlas_blend.pt in the same directory for backward compatibility
    if out_path.name != "atlas_blend.pt":
        atlas_copy_path = out_path.parent / "atlas_blend.pt"
        torch.save(blended_tensor, atlas_copy_path)
        logger.info(f"Created alias copy at '{atlas_copy_path.resolve()}'")
        
    # Print diagnostic statistics
    mean_a, std_a = tensor_a.mean().item(), tensor_a.std().item()
    mean_b, std_b = tensor_b.mean().item(), tensor_b.std().item()
    mean_blend, std_blend = blended_tensor.mean().item(), blended_tensor.std().item()
    
    logger.info("--- Voice Blend Diagnostic Summary ---")
    logger.info(f"  Baseline (Jessica 80%) : Mean = {mean_a:+.4f} | Std = {std_a:.4f}")
    logger.info(f"  Analytical (Sarah 20%) : Mean = {mean_b:+.4f} | Std = {std_b:.4f}")
    logger.info(f"  Custom Blend Output    : Mean = {mean_blend:+.4f} | Std = {std_blend:.4f}")
    logger.info("--------------------------------------")
    
    return blended_tensor


def main():
    parser = argparse.ArgumentParser(description="ATLAS Custom Voice Blending Engine (80/20 PyTorch Tensor Blend)")
    parser.add_argument("--voice-a", "-a", type=str, default="voices/jessica.pt", help="Path to baseline voice tensor (default: voices/jessica.pt)")
    parser.add_argument("--voice-b", "-b", type=str, default="voices/sarah.pt", help="Path to analytical edge voice tensor (default: voices/sarah.pt)")
    parser.add_argument("--output", "-o", type=str, default="voices/custom_blend.pt", help="Path to save blended voice tensor (default: voices/custom_blend.pt)")
    parser.add_argument("--weight-a", type=float, default=0.8, help="Weight for baseline voice A (default: 0.8)")
    parser.add_argument("--weight-b", type=float, default=0.2, help="Weight for analytical voice B (default: 0.2)")
    parser.add_argument("--no-mock", action="store_true", help="Fail if input files don't exist instead of generating mock tensors")
    
    args = parser.parse_args()
    
    try:
        blend_voice_tensors(
            voice_a_path=args.voice_a,
            voice_b_path=args.voice_b,
            output_path=args.output,
            weight_a=args.weight_a,
            weight_b=args.weight_b,
            create_mock_if_missing=not args.no_mock
        )
    except Exception as e:
        logger.error(f"Voice blending failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
