"""
run_pipeline_cli.py - Command-line pipeline test for Dreams.ai

Usage:
    python run_pipeline_cli.py [--prompt "Your prompt"] [--user_id USER_ID]

Runs the full Dreams.ai pipeline using the same backend as the web test suite and prints results and timings to the terminal.
"""
import sys
import time
from test_gui import run_pipeline_test

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run Dreams.ai pipeline test from the command line.")
    parser.add_argument('--prompt', type=str, default="A magical forest with glowing mushrooms", help='Prompt for the dream')
    parser.add_argument('--user_id', type=str, default="cli-user", help='User ID for the dream')
    args = parser.parse_args()

    print(f"Running pipeline test with prompt: {args.prompt}")
    start_time = time.time()
    dream_card = run_pipeline_test(args.prompt, args.user_id)
    duration = time.time() - start_time
    print("\n=== Pipeline Test Result ===")
    print(f"Dream ID: {dream_card.dream_id}")
    print(f"Title: {dream_card.title}")
    print(f"Excerpt: {dream_card.excerpt}")
    print(f"Story: {dream_card.story}")
    print(f"Pitch: {dream_card.pitch}")
    print(f"Scene Count: {dream_card.scene_count}")
    print(f"Director Vision: {dream_card.director_vision}")
    print(f"Image Prompt: {dream_card.image_prompt}")
    print(f"Test Duration: {dream_card.test_duration:.2f} seconds")
    print(f"Wall Time: {duration:.2f} seconds")
    print("===========================\n")
    print("Pipeline CLI test complete.")
    sys.exit(0)

if __name__ == "__main__":
    main() 