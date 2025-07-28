#!/usr/bin/env python3
"""
Fast Generators Test for Dreams.ai
Tests SDXL Turbo and SD 1.5 for speed optimization
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_sdxl_turbo():
    """Test SDXL Turbo generation"""
    print("🚀 Testing SDXL Turbo...")
    
    try:
        from core.image_generator import image_manager
        
        prompt = "A beautiful sunset over mountains, first-person perspective"
        print(f"📝 Prompt: {prompt}")
        
        start_time = time.time()
        result = image_manager.generate_image(
            prompt=prompt,
            service="sdxl_turbo",
            width=512,
            height=512,
            num_inference_steps=1
        )
        
        generation_time = time.time() - start_time
        
        if result and result.get('service') == 'sdxl_turbo':
            print("✅ SDXL Turbo successful!")
            print(f"⏱️ Generation time: {generation_time:.2f}s")
            print(f"📁 File: {result.get('filename')}")
            print(f"📊 Metadata: {result.get('metadata', {})}")
            return True, generation_time
        else:
            print(f"❌ SDXL Turbo failed")
            print(f"Result: {result}")
            return False, 0
            
    except Exception as e:
        print(f"❌ Error in SDXL Turbo test: {e}")
        return False, 0



def main():
    """Main test function"""
    print("🏁 Dreams.ai Fast Generators Test")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test SDXL Turbo
    success, time_sdxl = test_sdxl_turbo()
    if success:
        results['SDXL Turbo'] = time_sdxl
    

    
    # Results Summary
    print("\n" + "="*50)
    print("🏁 SPEED RESULTS")
    print("="*50)
    
    for model, gen_time in sorted(results.items(), key=lambda x: x[1]):
        status = "✅" if gen_time <= 10 else "⚠️" if gen_time <= 30 else "❌"
        print(f"{status} {model}: {gen_time:.2f}s")
    
    print("\n💡 RECOMMENDATIONS:")
    if results:
        fastest = min(results.items(), key=lambda x: x[1])
        print(f"   🏆 Fastest: {fastest[0]} ({fastest[1]:.2f}s)")
        
        if fastest[1] <= 10:
            print("   ✅ Target achieved! Ready for production")
            print("   🎯 Use this model for mobile-first experience")
        elif fastest[1] <= 30:
            print("   ⚠️ Close to target, consider optimizations")
        else:
            print("   ❌ Too slow, need different approach")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 