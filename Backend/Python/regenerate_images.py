#!/usr/bin/env python3
"""
Utility script to regenerate images from IMN files using their stored seeds.
This allows for perfect reproducibility of dream images.
"""

import os
import sys
import glob
import base64
from PIL import Image
import io

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.image_generator import generate_dream_image
from core.imn_utils import read_imn, write_imn, get_imn_filelock

def regenerate_images_from_imn_files():
    """Regenerate images from all IMN files using their stored seeds"""
    
    print("🔄 Regenerating images from IMN files...")
    print("=" * 60)
    
    # Find all IMN files
    imn_directory = os.path.join("..", "Dreams")
    imn_files = glob.glob(os.path.join(imn_directory, "*.imn"))
    
    if not imn_files:
        print("❌ No IMN files found in Dreams directory")
        return
    
    print(f"📁 Found {len(imn_files)} IMN files")
    
    regenerated_count = 0
    skipped_count = 0
    error_count = 0
    
    for imn_file in imn_files:
        dream_id = os.path.basename(imn_file).replace('.imn', '')
        print(f"\n🎨 Processing dream: {dream_id}")
        
        try:
            # Read IMN file
            with get_imn_filelock(imn_file):
                imn_data = read_imn(imn_file)
            
            if not imn_data:
                print(f"   ❌ Failed to read IMN file")
                error_count += 1
                continue
            
            # Check for image generation metadata
            post_production = imn_data.get('post_production', {})
            image_generation = post_production.get('image_generation', {})
            
            if not image_generation:
                print(f"   ⚠️  No image generation metadata found, skipping")
                skipped_count += 1
                continue
            
            # Extract stored parameters
            seed = image_generation.get('seed')
            prompt = image_generation.get('prompt')
            service = image_generation.get('service', 'sdxl_turbo')
            width = image_generation.get('width', 512)
            height = image_generation.get('height', 512)
            num_inference_steps = image_generation.get('num_inference_steps', 1)
            guidance_scale = image_generation.get('guidance_scale', 0.0)
            
            if not seed or not prompt:
                print(f"   ⚠️  Missing seed or prompt, skipping")
                skipped_count += 1
                continue
            
            print(f"   📝 Prompt: {prompt[:50]}...")
            print(f"   🎲 Seed: {seed}")
            print(f"   🎨 Service: {service}")
            
            # Regenerate image
            print(f"   🔄 Regenerating image...")
            result = generate_dream_image(
                prompt=prompt,
                service=service,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                seed=seed
            )
            
            if result and result.get('service') == service:
                # Update the IMN file with new image data
                image_generation['image_data'] = result.get('image_data')
                image_generation['filename'] = result.get('filename')
                image_generation['generation_time'] = result.get('metadata', {}).get('generation_time', 0)
                image_generation['generated_at'] = result.get('metadata', {}).get('generated_at')
                
                # Write updated IMN file
                with get_imn_filelock(imn_file):
                    write_imn(imn_data, imn_directory)
                
                print(f"   ✅ Successfully regenerated and updated IMN file")
                print(f"   📁 File: {result.get('filename')}")
                print(f"   ⏱️  Time: {result.get('metadata', {}).get('generation_time', 0):.2f}s")
                
                regenerated_count += 1
                
            else:
                print(f"   ❌ Image generation failed: {result}")
                error_count += 1
                
        except Exception as e:
            print(f"   ❌ Error processing {dream_id}: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Regeneration Summary:")
    print(f"   ✅ Successfully regenerated: {regenerated_count}")
    print(f"   ⚠️  Skipped (no metadata): {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📁 Total IMN files: {len(imn_files)}")

def verify_image_reproducibility(dream_id):
    """Verify that a specific dream's image can be perfectly reproduced"""
    
    print(f"🔍 Verifying image reproducibility for dream: {dream_id}")
    print("=" * 60)
    
    imn_file = os.path.join("..", "Dreams", f"{dream_id}.imn")
    
    if not os.path.exists(imn_file):
        print(f"❌ IMN file not found: {imn_file}")
        return
    
    try:
        # Read IMN file
        with get_imn_filelock(imn_file):
            imn_data = read_imn(imn_file)
        
        if not imn_data:
            print(f"❌ Failed to read IMN file")
            return
        
        # Check for image generation metadata
        post_production = imn_data.get('post_production', {})
        image_generation = post_production.get('image_generation', {})
        
        if not image_generation:
            print(f"❌ No image generation metadata found")
            return
        
        # Extract stored parameters
        seed = image_generation.get('seed')
        prompt = image_generation.get('prompt')
        service = image_generation.get('service', 'sdxl_turbo')
        width = image_generation.get('width', 512)
        height = image_generation.get('height', 512)
        num_inference_steps = image_generation.get('num_inference_steps', 1)
        guidance_scale = image_generation.get('guidance_scale', 0.0)
        
        print(f"📝 Prompt: {prompt}")
        print(f"🎲 Seed: {seed}")
        print(f"🎨 Service: {service}")
        print(f"📐 Resolution: {width}x{height}")
        
        # Generate image multiple times to verify reproducibility
        print(f"\n🔄 Generating image 3 times to verify reproducibility...")
        
        images = []
        for i in range(3):
            print(f"   Generation {i+1}/3...")
            result = generate_dream_image(
                prompt=prompt,
                service=service,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                seed=seed
            )
            
            if result and result.get('service') == service:
                images.append(result.get('image_data'))
                print(f"   ✅ Generated successfully")
            else:
                print(f"   ❌ Generation failed")
                return
        
        # Compare all generated images
        print(f"\n🔍 Comparing generated images...")
        
        all_identical = True
        for i in range(len(images)):
            for j in range(i + 1, len(images)):
                if images[i] != images[j]:
                    all_identical = False
                    print(f"   ⚠️  Images {i+1} and {j+1} are different!")
                else:
                    print(f"   ✅ Images {i+1} and {j+1} are identical")
        
        if all_identical:
            print(f"\n🎯 Perfect reproducibility achieved!")
        else:
            print(f"\n⚠️  Reproducibility issues detected")
            
    except Exception as e:
        print(f"❌ Error verifying reproducibility: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Regenerate images from IMN files")
    parser.add_argument("--verify", type=str, help="Verify reproducibility for specific dream ID")
    parser.add_argument("--regenerate-all", action="store_true", help="Regenerate all images from IMN files")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_image_reproducibility(args.verify)
    elif args.regenerate_all:
        regenerate_images_from_imn_files()
    else:
        print("Usage:")
        print("  python regenerate_images.py --regenerate-all")
        print("  python regenerate_images.py --verify <dream_id>")
        print("\nExamples:")
        print("  python regenerate_images.py --regenerate-all")
        print("  python regenerate_images.py --verify f1c48beb-efbe-48e9-8a83-d0a863ccd9c3") 