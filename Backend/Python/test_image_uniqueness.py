#!/usr/bin/env python3
"""
Test script to verify that different dreams generate unique images.
This script tests the image generation with different prompts and seeds.
"""

import os
import sys
import hashlib
import base64
import random
from PIL import Image
import io

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.image_generator import generate_dream_image
from core.imn_utils import read_imn, write_imn, get_imn_filelock

def test_image_uniqueness():
    """Test that different prompts generate different images"""
    
    # Test prompts from different dreams
    test_prompts = [
        "A majestic corgi, dressed in tattered pirate attire, stands proudly at the edge of a serene and tranquil lake. The corgi's fur is a warm sandy color, with subtle hints of dark brown and golden tones. The pirate gear includes a faded bandana, worn leather boots, and a battered wooden sword. In the background, lush greenery and vibrant tropical flowers surround the lake, creating a sense of serenity and tranquility.",
        "Create an AI-generated image featuring a corgi pirate standing proudly on the bow of a pirate ship, with Polly perched on his shoulder. The background should feature a misty, moonlit night sky, with the silhouette of a rival pirate ship lurking in the shadows. The overall atmosphere should be dreamlike and full of wonder.",
        "A misty forest at dawn, with a faint path winding through the trees. In the distance, luminescent mushrooms glow softly, casting an ethereal light across the scene. A small, delicate creature emerges from the underbrush, adding a sense of movement and life to the image."
    ]
    
    # Test dream IDs
    test_dream_ids = [
        "f1c48beb-efbe-48e9-8a83-d0a863ccd9c3",
        "a9d8f02e-864a-44bf-8a89-0fba64574b8d", 
        "c2613c70-313f-43e8-8a2b-8147ec3de3dd"
    ]
    
    print("🧪 Testing image uniqueness with stored seeds...")
    print("=" * 60)
    
    generated_images = []
    
    for i, (prompt, dream_id) in enumerate(zip(test_prompts, test_dream_ids)):
        print(f"\n🎨 Generating image {i+1}/3")
        print(f"Dream ID: {dream_id}")
        print(f"Prompt: {prompt[:100]}...")
        
        # Generate random seed for initial generation
        seed = random.randint(1, 1000000)
        print(f"Initial Seed: {seed}")
        
        try:
            # Generate image
            result = generate_dream_image(
                prompt=prompt,
                service="sdxl_turbo",
                width=512,
                height=512,
                num_inference_steps=1,
                guidance_scale=0.0,
                seed=seed
            )
            
            if result and result.get('service') == 'sdxl_turbo':
                image_data = result.get('image_data')
                filename = result.get('filename', 'unknown')
                generation_time = result.get('metadata', {}).get('generation_time', 0)
                
                print(f"✅ Generated successfully!")
                print(f"   File: {filename}")
                print(f"   Time: {generation_time:.2f}s")
                print(f"   Image data length: {len(image_data)} chars")
                
                # Store for comparison
                generated_images.append({
                    'dream_id': dream_id,
                    'prompt': prompt,
                    'image_data': image_data,
                    'filename': filename,
                    'seed': seed
                })
                
            else:
                print(f"❌ Generation failed: {result}")
                
        except Exception as e:
            print(f"❌ Error generating image: {e}")
    
    # Test reproducibility with stored seeds
    print("\n" + "=" * 60)
    print("🔄 Testing reproducibility with stored seeds...")
    
    for i, img in enumerate(generated_images):
        print(f"\n🔄 Regenerating image {i+1} with stored seed: {img['seed']}")
        
        try:
            # Regenerate with stored seed
            result = generate_dream_image(
                prompt=img['prompt'],
                service="sdxl_turbo",
                width=512,
                height=512,
                num_inference_steps=1,
                guidance_scale=0.0,
                seed=img['seed']
            )
            
            if result and result.get('service') == 'sdxl_turbo':
                regenerated_data = result.get('image_data')
                
                # Compare with original
                if regenerated_data == img['image_data']:
                    print(f"✅ Perfect reproducibility! Images are identical")
                else:
                    print(f"⚠️  Images are different despite same seed")
                
            else:
                print(f"❌ Regeneration failed: {result}")
                
        except Exception as e:
            print(f"❌ Error regenerating image: {e}")
    
    # Compare generated images
    print("\n" + "=" * 60)
    print("🔍 Comparing generated images...")
    
    if len(generated_images) >= 2:
        for i in range(len(generated_images)):
            for j in range(i + 1, len(generated_images)):
                img1 = generated_images[i]
                img2 = generated_images[j]
                
                # Compare image data
                similarity = "DIFFERENT" if img1['image_data'] != img2['image_data'] else "IDENTICAL"
                print(f"   {img1['dream_id'][:8]} vs {img2['dream_id'][:8]}: {similarity}")
                print(f"   Seeds: {img1['seed']} vs {img2['seed']}")
                
                if similarity == "IDENTICAL":
                    print(f"   ⚠️  WARNING: Images are identical despite different prompts!")
                else:
                    print(f"   ✅ Images are unique as expected")
    
    print("\n" + "=" * 60)
    print("🎯 Test completed!")
    
    # Save images for visual inspection
    print("\n💾 Saving test images for visual inspection...")
    os.makedirs("test_images", exist_ok=True)
    
    for i, img in enumerate(generated_images):
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(img['image_data'])
            image = Image.open(io.BytesIO(image_bytes))
            
            # Save with descriptive name
            filename = f"test_images/dream_{img['dream_id'][:8]}_seed_{img['seed']}_{i+1}.png"
            image.save(filename)
            print(f"   Saved: {filename}")
            
        except Exception as e:
            print(f"   ❌ Error saving image {i+1}: {e}")
    
    print("\n✅ Test images saved to 'test_images/' directory")

def test_imn_seed_storage():
    """Test storing and retrieving seeds from IMN files"""
    
    print("\n" + "=" * 60)
    print("📁 Testing IMN seed storage functionality...")
    
    # Test with existing IMN files
    test_imn_files = [
        "f1c48beb-efbe-48e9-8a83-d0a863ccd9c3.imn",
        "a9d8f02e-864a-44bf-8a89-0fba64574b8d.imn"
    ]
    
    for imn_file in test_imn_files:
        imn_path = os.path.join("..", "Dreams", imn_file)
        
        if os.path.exists(imn_path):
            print(f"\n📖 Reading {imn_file}...")
            
            try:
                with get_imn_filelock(imn_path):
                    imn_data = read_imn(imn_path)
                
                if imn_data:
                    post_production = imn_data.get('post_production', {})
                    image_generation = post_production.get('image_generation', {})
                    
                    if image_generation:
                        seed = image_generation.get('seed')
                        prompt = image_generation.get('prompt', 'No prompt')
                        model = image_generation.get('model', 'Unknown')
                        
                        print(f"   ✅ Found image generation metadata:")
                        print(f"      Seed: {seed}")
                        print(f"      Model: {model}")
                        print(f"      Prompt: {prompt[:50]}...")
                    else:
                        print(f"   ⚠️  No image generation metadata found")
                else:
                    print(f"   ❌ Failed to read IMN file")
                    
            except Exception as e:
                print(f"   ❌ Error reading IMN file: {e}")
        else:
            print(f"   ⚠️  IMN file not found: {imn_path}")

if __name__ == "__main__":
    test_image_uniqueness()
    test_imn_seed_storage() 