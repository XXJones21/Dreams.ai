#!/usr/bin/env python3
"""
Test script to demonstrate enhanced Cenedril's structured prompt generation.
"""

import os
import sys
from core.agents import Cenedril
from core.imn_utils import read_imn, write_imn, get_imn_filelock
from langchain_openai import ChatOpenAI

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cenedril_enhancement():
    """Test the enhanced Cenedril with structured prompt generation."""
    
    # Test dream ID
    dream_id = "db1d5723-6c8b-4d43-8bc3-91a7a27a1da7"
    imn_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    
    print("🎬 Testing Enhanced Cenedril - Structured Prompt Generation")
    print("=" * 60)
    
    # Read the existing IMN file
    with get_imn_filelock(imn_path):
        imn_data = read_imn(imn_path)
    
    if not imn_data:
        print("❌ Could not read IMN file")
        return
    
    # Show original director's vision
    director_vision = imn_data["pre_production"].get("director_vision", {})
    original_prompt = director_vision.get("image_prompt", "")
    
    print("📋 Original Director's Prompt:")
    print(f"   {original_prompt}")
    print()
    
    # Create a test state for Cenedril
    test_state = {
        "id": dream_id,
        "messages": [{"role": "assistant", "content": "Test message"}],
        "user_id": "test-user-123"
    }
    
    # Run enhanced Cenedril
    print("🎨 Running Enhanced Cenedril...")
    enhanced_state = Cenedril(test_state)
    
    # Read the updated IMN file
    with get_imn_filelock(imn_path):
        updated_imn_data = read_imn(imn_path)
    
    # Show the enhanced prompt
    enhanced_prompt = updated_imn_data["pre_production"].get("enhanced_image_prompt", "")
    
    print("\n🎨 Enhanced Cenedril Output:")
    print("=" * 60)
    print(enhanced_prompt)
    print("=" * 60)
    
    # Compare the prompts
    print("\n📊 Comparison:")
    print(f"Original length: {len(original_prompt)} characters")
    print(f"Enhanced length: {len(enhanced_prompt)} characters")
    print(f"Improvement: {len(enhanced_prompt) - len(original_prompt)} characters")
    
    # Check for structured elements
    structured_indicators = [
        "Main prompt:", "Style modifiers:", "Negative prompt:", 
        "Technical notes:", "SDXL", "optimized", "structured"
    ]
    
    print("\n🔍 Structured Elements Found:")
    for indicator in structured_indicators:
        if indicator.lower() in enhanced_prompt.lower():
            print(f"   ✅ {indicator}")
        else:
            print(f"   ❌ {indicator}")
    
    print("\n✅ Enhanced Cenedril test completed!")

if __name__ == "__main__":
    test_cenedril_enhancement() 