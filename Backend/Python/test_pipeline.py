"""
Test script for the Dreams.ai agent pipeline
"""
import json
import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import from main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import graph
from core.imn_utils import validate_imn_structure, read_imn


def test_agent_pipeline():
    """
    Test the complete agent pipeline with a sample prompt
    """
    print("Testing Dreams.ai Agent Pipeline")
    print("=" * 50)
    
    # Test prompt
    test_prompt = "A corgi taking a nap on a sunny beach"
    print(f"Test Prompt: {test_prompt}")
    print()
    
    # Initialize state
    state = {
        "messages": [{"role": "user", "content": test_prompt}],
        "user_id": "test-user-123"
    }
    
    try:
        # Run the pipeline
        print("Running agent pipeline...")
        result = graph.invoke(state)
        
        # Check if we got a dream ID
        dream_id = result.get("id")
        if not dream_id:
            print("❌ No dream ID generated")
            return False
        
        print(f"✅ Dream ID generated: {dream_id}")
        
        # Check if .imn file was created
        imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
        if not os.path.exists(imn_file_path):
            print(f"❌ .imn file not found at {imn_file_path}")
            return False
        
        print(f"✅ .imn file created: {imn_file_path}")
        
        # Validate .imn file structure
        imn_data = read_imn(imn_file_path)
        if imn_data is None:
            print("❌ Could not read .imn file")
            return False
        
        if not validate_imn_structure(imn_data):
            print("❌ .imn file structure is invalid")
            return False
        
        print("✅ .imn file structure is valid")
        
        # Display key information
        pre_prod = imn_data.get("pre_production", {})
        print(f"\n📋 Dream Details:")
        print(f"  Name: {pre_prod.get('dream_name', 'N/A')}")
        print(f"  Story: {pre_prod.get('story_prompt', 'N/A')[:100]}...")
        print(f"  Goal: {pre_prod.get('initial_goal', 'N/A')}")
        
        # Check if scenes were generated
        scenes = imn_data.get("in_production", [])
        print(f"  Scenes: {len(scenes)} generated")
        
        if scenes:
            latest_scene = scenes[-1]
            print(f"  Latest Scene: {latest_scene.get('scene_context', 'N/A')[:100]}...")
            print(f"  Available Actions: {len(latest_scene.get('actions', []))}")
        
        # Check if director's vision was generated
        if "director_vision" in pre_prod:
            print("✅ Director's vision generated")
        else:
            print("⚠️  No director's vision found")
        
        print("\n🎉 Pipeline test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_agents():
    """
    Test individual agent functions
    """
    print("\n🔍 Testing Individual Agents")
    print("=" * 30)
    
    # Import agent functions
    from main import Carthir, convert_prompt_to_imn, Narnion, CarthirReview, Cenedril
    
    # Test state
    test_state = {
        "messages": [{"role": "user", "content": "A magical forest adventure"}],
        "user_id": "test-user-456"
    }
    
    agents_to_test = [
        ("Carthir", Carthir),
        ("convert_prompt_to_imn", convert_prompt_to_imn),
        ("Narnion", Narnion),
        ("CarthirReview", CarthirReview),
        ("Cenedril", Cenedril)
    ]
    
    for agent_name, agent_func in agents_to_test:
        try:
            print(f"Testing {agent_name}...")
            result = agent_func(test_state.copy())
            print(f"✅ {agent_name} completed successfully")
        except Exception as e:
            print(f"❌ {agent_name} failed: {e}")


def test_imn_utilities():
    """
    Test .imn utility functions
    """
    print("\n📁 Testing .imn Utilities")
    print("=" * 30)
    
    from core.imn_utils import create_imn_structure, validate_imn_structure
    
    # Test creating IMN structure
    test_imn = create_imn_structure(
        dream_id="test-dream-123",
        user_id="test-user",
        dream_name="Test Dream",
        story_prompt="A test story",
        initial_goal="Test goal",
        pitch="Test pitch"
    )
    
    print("✅ IMN structure created")
    
    # Test validation
    if validate_imn_structure(test_imn):
        print("✅ IMN structure validation passed")
    else:
        print("❌ IMN structure validation failed")
    
    # Test with invalid structure
    invalid_imn = {"invalid": "structure"}
    if not validate_imn_structure(invalid_imn):
        print("✅ Invalid IMN structure correctly rejected")
    else:
        print("❌ Invalid IMN structure incorrectly accepted")


def main():
    """
    Run all tests
    """
    print("Dreams.ai Pipeline Test Suite")
    print("=" * 50)
    print(f"Started at: {datetime.now()}")
    print()
    
    # Test .imn utilities first
    test_imn_utilities()
    
    # Test individual agents
    test_individual_agents()
    
    # Test full pipeline
    success = test_agent_pipeline()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
    print(f"Completed at: {datetime.now()}")


if __name__ == "__main__":
    main() 