"""E2E milestone #1 runner: one prompt -> playable video through the linear pipeline.

Calls PipelineInstance directly with generate_video=True (bypasses test_gui's
redundant legacy in-process SDXL path). Run from Backend/Python so the agents'
relative `../Dreams` IMN paths resolve.
"""
import os
import sys
import json
import time

sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("COMFY_TRANSPORT", "direct")

from core.pipeline_instance import PipelineInstance
from core.imn_utils import read_imn, get_imn_filelock

PROMPT = (
    "I wake in a flooded cathedral lit only by my own trembling flashlight; "
    "black water rises around my legs as I wade toward a distant red glow."
)

def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else PROMPT
    print(f"[E2E] Prompt: {prompt}")
    state = {
        "messages": [{"role": "user", "content": prompt}],
        "user_id": "e2e-cli",
        "generate_video": True,
    }
    t0 = time.time()
    inst = PipelineInstance(state)
    result = inst.run()
    wall = time.time() - t0
    dream_id = result.get("id")
    print(f"\n[E2E] dream_id={dream_id}  wall={wall:.1f}s")

    imn_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    with get_imn_filelock(imn_path):
        imn = read_imn(imn_path)
    pp = (imn or {}).get("post_production", {})
    print("[E2E] image_generation:", json.dumps(pp.get("image_generation"), indent=2))
    print("[E2E] video_generation:", json.dumps(pp.get("video_generation"), indent=2))
    print(f"[E2E] IMN_PATH={os.path.abspath(imn_path)}")

if __name__ == "__main__":
    main()
