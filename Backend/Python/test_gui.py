"""
GUI Test Suite for Dreams.ai
Displays dream cards and allows testing the complete pipeline with visual feedback.
"""

import json
import os
import sys
import uuid
import time
import psutil
import threading
import base64
import pytz
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Add the current directory to the path so we can import from main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.pipeline_instance import PipelineInstance
from core.imn_utils import validate_imn_structure, read_imn, create_imn_structure, write_imn, get_imn_filelock
from core.image_generator import generate_dream_image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global state
current_test = None
test_results = []
debug_info = {
    'agent_execution': [],
    'memory_usage': [],
    'timing_breakdown': {},
    'pipeline_steps': [],
    'current_agent': None,
    'step_start_time': None,
    'total_start_time': None
}

class DreamCard:
    def __init__(self, dream_id, title, excerpt, story, pitch, user_id, test_duration=0):
        self.dream_id = dream_id
        self.title = title
        self.excerpt = excerpt
        self.story = story
        self.pitch = pitch
        self.user_id = user_id
        self.test_duration = test_duration
        # Create timezone-aware datetime string
        utc_now = datetime.now(pytz.UTC)
        self.created_at = utc_now.isoformat()
        self.scene_count = 0
        self.image_data = None
        self.image_prompt = None
        self.director_vision = None
        self.scenes = []

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    memory_info = process.memory_info()
    return {
        'rss_mb': memory_info.rss / 1024 / 1024,
        'vms_mb': memory_info.vms / 1024 / 1024,
        'percent': process.memory_percent()
    }

def update_debug_info(agent_name=None, step_name=None, data=None):
    """Update debug information during pipeline execution"""
    global debug_info
    
    current_time = time.time()
    
    # Update memory usage
    memory = get_memory_usage()
    debug_info['memory_usage'].append({
        'timestamp': current_time,
        'rss_mb': memory['rss_mb'],
        'vms_mb': memory['vms_mb'],
        'percent': memory['percent']
    })
    
    # Keep only last 100 memory readings
    if len(debug_info['memory_usage']) > 100:
        debug_info['memory_usage'] = debug_info['memory_usage'][-100:]
    
    # Update agent execution
    if agent_name:
        debug_info['current_agent'] = agent_name
        debug_info['agent_execution'].append({
            'timestamp': current_time,
            'agent': agent_name,
            'step': step_name,
            'data': data
        })
        
        # Keep only last 50 agent executions
        if len(debug_info['agent_execution']) > 50:
            debug_info['agent_execution'] = debug_info['agent_execution'][-50:]
    
    # Update timing breakdown
    if step_name and debug_info['step_start_time']:
        step_duration = current_time - debug_info['step_start_time']
        if step_name not in debug_info['timing_breakdown']:
            debug_info['timing_breakdown'][step_name] = []
        debug_info['timing_breakdown'][step_name].append(step_duration)
        
        # Keep only last 10 timings per step
        if len(debug_info['timing_breakdown'][step_name]) > 10:
            debug_info['timing_breakdown'][step_name] = debug_info['timing_breakdown'][step_name][-10:]
    
    # Update pipeline steps
    if step_name:
        debug_info['pipeline_steps'].append({
            'timestamp': current_time,
            'step': step_name,
            'agent': agent_name,
            'duration': step_duration if 'step_duration' in locals() else None
        })
        
        # Keep only last 20 pipeline steps
        if len(debug_info['pipeline_steps']) > 20:
            debug_info['pipeline_steps'] = debug_info['pipeline_steps'][-20:]
    
    debug_info['step_start_time'] = current_time

def reset_debug_info():
    """Reset debug information for a new test"""
    global debug_info
    debug_info = {
        'agent_execution': [],
        'memory_usage': [],
        'timing_breakdown': {},
        'pipeline_steps': [],
        'current_agent': None,
        'step_start_time': None,
        'total_start_time': time.time()
    }

def dream_card_to_dict(dream_card):
    """Convert DreamCard object or dictionary to dictionary for JSON serialization"""
    # Handle both dictionary and object formats
    if isinstance(dream_card, dict):
        # Already a dictionary - return as is with safe defaults
        return {
            'dream_id': dream_card.get('dream_id', ''),
            'title': dream_card.get('title', 'Untitled'),
            'excerpt': dream_card.get('excerpt', ''),
            'story': dream_card.get('story', ''),
            'pitch': dream_card.get('pitch', ''),
            'user_id': dream_card.get('user_id', ''),
            'test_duration': dream_card.get('test_duration', 0),
            'created_at': dream_card.get('created_at', dream_card.get('timestamp', '')),
            'scene_count': dream_card.get('scene_count', 0),
            'image_data': dream_card.get('image_data', None),
            'image_prompt': dream_card.get('image_prompt', ''),
            'director_vision': dream_card.get('director_vision', ''),
            'scenes': dream_card.get('scenes', [])
        }
    else:
        # Object format - use attributes
        return {
            'dream_id': dream_card.dream_id,
            'title': dream_card.title,
            'excerpt': dream_card.excerpt,
            'story': dream_card.story,
            'pitch': dream_card.pitch,
            'user_id': dream_card.user_id,
            'test_duration': dream_card.test_duration,
            'created_at': dream_card.created_at,
            'scene_count': dream_card.scene_count,
            'image_data': dream_card.image_data,  # This should now be the base64 string
            'image_prompt': dream_card.image_prompt,
            'director_vision': dream_card.director_vision,
            'scenes': dream_card.scenes
        }

def run_pipeline_test(prompt, user_id):
    """Run the complete pipeline test with detailed debugging (using PipelineInstance)"""
    global current_test, test_results, debug_info
    
    logger.info(f"Starting pipeline test with prompt: {prompt}")
    reset_debug_info()
    
    # Performance tracking
    pipeline_start_time = time.time()
    llm_total_time = 0
    image_generation_time = 0
    
    try:
        # Initialize test state
        test_state = {
            "messages": [{"role": "user", "content": prompt}],
            "user_id": user_id
        }
        
        update_debug_info("Pipeline", "Initialization", {"prompt": prompt, "user_id": user_id})
        
        # Execute the pipeline using PipelineInstance
        logger.info("Executing pipeline instance...")
        update_debug_info("Graph", "Execution Start")
        llm_start_time = time.time()
        pipeline_instance = PipelineInstance(test_state)
        result = pipeline_instance.run()
        llm_total_time = time.time() - llm_start_time
        update_debug_info("Graph", "Execution Complete", {"result_keys": list(result.keys()), "llm_time": llm_total_time})
        
        # Extract dream ID
        dream_id = result.get('id', str(uuid.uuid4()))
        logger.info(f"Dream ID generated: {dream_id}")
        
        # Read IMN file
        update_debug_info("IMN", "File Reading")
        imn_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
        logger.info(f"Looking for IMN file at: {imn_path}")
        
        if os.path.exists(imn_path):
            logger.info("IMN file found, reading data...")
            imn_data = read_imn(imn_path)
            logger.info("IMN data read successfully")
            
            # Create dream card
            update_debug_info("DreamCard", "Creation")
            
            # Extract data from nested IMN structure
            pre_production = imn_data.get('pre_production', {})
            in_production = imn_data.get('in_production', [])
            post_production = imn_data.get('post_production', {})
            
            dream_card = DreamCard(
                dream_id=dream_id,
                title=pre_production.get('dream_name', 'Untitled Dream'),
                excerpt=pre_production.get('story_prompt', 'No excerpt available'),
                story=pre_production.get('initial_goal', 'No story available'),
                pitch=pre_production.get('pitch', 'No pitch available'),
                user_id=user_id
            )
            
            # Set scene count
            dream_card.scene_count = len(in_production)
            
            # Set director vision
            dream_card.director_vision = post_production.get('director_vision', 'No director vision available')
            
            logger.info(f"Dream card created. Title: {dream_card.title}")
            
            # Generate image
            update_debug_info("ImageGenerator", "Generation Start")
            # Look for image prompt in multiple locations - prioritize Cenedril's enhanced prompt
            director_vision = pre_production.get('director_vision', {})
            image_prompt = (
                pre_production.get('enhanced_image_prompt') or  # PRIORITY: Cenedril's structured prompt
                director_vision.get('image_prompt') or
                pre_production.get('first_frame_prompt') or 
                post_production.get('image_prompt') or
                'No image prompt available'
            )
            
            dream_card.image_prompt = image_prompt
            
            if image_prompt and image_prompt != 'No image prompt available':
                logger.info(f"Generating image with prompt: {image_prompt}")
                update_debug_info("ImageGenerator", "Processing", {"prompt_length": len(image_prompt)})
                
                # Use SDXL Turbo with 512x512 resolution
                logger.info("🎨 Starting SDXL Turbo image generation...")
                update_debug_info("SDXL Turbo", "Generation Start", {
                    "prompt": image_prompt,
                    "resolution": "512x512",
                    "service": "sdxl_turbo"
                })
                
                try:
                    # Generate image with SDXL Turbo
                    import random
                    
                    # Check if we already have a stored seed for this dream
                    stored_seed = post_production.get('image_generation', {}).get('seed')
                    
                    if stored_seed is not None:
                        # Use stored seed for consistency
                        seed = stored_seed
                        logger.info(f"🎲 Using stored seed: {seed} for consistent image regeneration")
                    else:
                        # Generate new random seed for initial creation
                        seed = random.randint(1, 1000000)
                        logger.info(f"🎲 Using new random seed: {seed} for initial image generation")
                    
                    image_data = generate_dream_image(
                        prompt=image_prompt,
                        service="sdxl_turbo",
                        width=512,
                        height=512,
                        num_inference_steps=1,
                        guidance_scale=0.0,
                        seed=seed,
                        director_vision=post_production.get('director_vision', {})
                    )
                    
                    if image_data and image_data.get('service') == 'sdxl_turbo':
                        # Extract just the base64 image data for frontend display
                        dream_card.image_data = image_data.get('image_data')
                        generation_time = image_data.get('metadata', {}).get('generation_time', 0)
                        
                        image_generation_time = generation_time
                        logger.info(f"✅ SDXL Turbo generation successful!")
                        logger.info(f"⏱️ Generation time: {generation_time:.2f}s")
                        logger.info(f"📁 File: {image_data.get('filename', 'N/A')}")
                        logger.info(f"📊 Resolution: {image_data.get('metadata', {}).get('width', 'N/A')}x{image_data.get('metadata', {}).get('height', 'N/A')}")
                        
                        # Store image generation metadata in IMN file
                        if imn_data:
                            imn_data["post_production"]["image_generation"] = {
                                "seed": seed,
                                "prompt": image_prompt,
                                "service": "sdxl_turbo",
                                "width": image_data.get('metadata', {}).get('width', 512),
                                "height": image_data.get('metadata', {}).get('height', 512),
                                "num_inference_steps": 1,
                                "guidance_scale": 0.0,
                                "generation_time": generation_time,
                                "filename": image_data.get('filename', ''),
                                "generated_at": datetime.now().isoformat(),
                                "model": "SDXL Turbo"
                            }
                            
                            # Write updated IMN data back to file
                            directory = os.path.join("..", "Dreams")
                            with get_imn_filelock(imn_path):
                                write_imn(imn_data, directory)
                            
                            logger.info(f"💾 Stored image generation metadata in IMN file (seed: {seed})")
                            
                except Exception as e:
                    error_msg = f"SDXL Turbo image generation failed: {str(e)}"
                    logger.error(error_msg)
                    update_debug_info("SDXL Turbo", "Generation Error", {"error": str(e)})
                    dream_card.image_data = None
            
            else:
                logger.info("No image prompt available")
            
            # Calculate test duration
            if debug_info['total_start_time']:
                dream_card.test_duration = time.time() - debug_info['total_start_time']
            
            # Performance summary
            total_time = time.time() - pipeline_start_time
            logger.info(f"🚀 PERFORMANCE SUMMARY:")
            logger.info(f"   Total Pipeline Time: {total_time:.2f}s")
            logger.info(f"   LLM Processing Time: {llm_total_time:.2f}s")
            logger.info(f"   Image Generation Time: {image_generation_time:.2f}s")
            logger.info(f"   LLM % of Total: {llm_total_time/total_time*100:.1f}%")
            logger.info(f"   Image % of Total: {image_generation_time/total_time*100:.1f}%")
            logger.info(f"Test completed successfully in {total_time:.2f} seconds")
            
            # Store successful result with complete dream information
            test_results.append({
                'dream_id': dream_id,
                'title': dream_card.title,
                'excerpt': dream_card.excerpt,
                'story': dream_card.story,
                'pitch': dream_card.pitch,
                'user_id': user_id,
                'test_duration': total_time,
                'llm_time': llm_total_time,
                'image_time': image_generation_time,
                'created_at': dream_card.created_at,
                'scene_count': dream_card.scene_count,
                'image_data': dream_card.image_data,
                'image_prompt': dream_card.image_prompt,
                'director_vision': dream_card.director_vision,
                'scenes': dream_card.scenes,
                'timestamp': time.time()
            })
            logger.info(f"Test completed and added to results. Total tests: {len(test_results)}")
            
            return dream_card
        else:
            error_msg = f"IMN file not found: {imn_path}"
            logger.error(error_msg)
            update_debug_info("Pipeline", "Error", {"error": error_msg})
            raise FileNotFoundError(error_msg)
            
    except Exception as e:
        error_msg = f"Pipeline test failed: {str(e)}"
        logger.error(error_msg)
        update_debug_info("Pipeline", "Error", {"error": str(e)})
        raise

@app.route('/')
def index():
    """Main test interface"""
    return render_template('test_interface.html')

@app.route('/api/test', methods=['POST'])
def run_test():
    """Run a pipeline test"""
    global current_test
    
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'A magical forest with glowing mushrooms')
        user_id = data.get('user_id', 'test-user')
        
        # Initialize current test
        current_test = {
            'prompt': prompt,
            'user_id': user_id,
            'status': 'running',
            'start_time': time.time(),
            'progress': 0
        }
        
        # Run test in background thread
        def run_test_thread():
            global current_test
            try:
                dream_card = run_pipeline_test(prompt, user_id)
                current_test['status'] = 'completed'
                current_test['dream_card'] = dream_card_to_dict(dream_card)
                current_test['duration'] = dream_card.test_duration
                
                logger.info(f"Test completed successfully in {dream_card.test_duration:.2f} seconds")
                return dream_card
            except Exception as e:
                current_test['status'] = 'error'
                current_test['error'] = str(e)
                logger.error(f"Test failed: {str(e)}")
                return None
        
        thread = threading.Thread(target=run_test_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'started', 'message': 'Test started successfully'})
        
    except Exception as e:
        logger.error(f"Error starting test: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get current test status and debug information"""
    global current_test, test_results, debug_info
    
    # Ensure current_test is serializable
    safe_current_test = None
    if current_test:
        safe_current_test = {
            'prompt': current_test.get('prompt'),
            'status': current_test.get('status'),
            'start_time': current_test.get('start_time'),
            'progress': current_test.get('progress'),
            'duration': current_test.get('duration'),
            'error': current_test.get('error')
        }
        # If there's a dream_card, ensure it's a dict
        if 'dream_card' in current_test:
            if isinstance(current_test['dream_card'], DreamCard):
                safe_current_test['dream_card'] = dream_card_to_dict(current_test['dream_card'])
            else:
                safe_current_test['dream_card'] = current_test['dream_card']
    
    # Prepare debug information
    safe_debug_info = {
        'current_agent': debug_info['current_agent'],
        'total_duration': time.time() - debug_info['total_start_time'] if debug_info['total_start_time'] else 0,
        'memory_usage': debug_info['memory_usage'][-1] if debug_info['memory_usage'] else None,
        'recent_agent_execution': debug_info['agent_execution'][-5:] if debug_info['agent_execution'] else [],
        'timing_breakdown': debug_info['timing_breakdown'],
        'pipeline_steps': debug_info['pipeline_steps'][-10:] if debug_info['pipeline_steps'] else []
    }
    
    return jsonify({
        'test_count': len(test_results),
        'current_test': safe_current_test,
        'debug_info': safe_debug_info
    })

@app.route('/api/dreams')
def get_dreams():
    """Get all test dreams from both test_results and IMN files"""
    global test_results
    
    # Get dreams from test_results (GUI-generated)
    gui_dreams = [dream_card_to_dict(dream) for dream in test_results]
    
    # Get dreams from IMN files (CLI-generated)
    imn_dreams = []
    dreams_dir = os.path.join("..", "Dreams")
    if os.path.exists(dreams_dir):
        for filename in os.listdir(dreams_dir):
            if filename.endswith('.imn'):
                dream_id = filename[:-4]  # Remove .imn extension
                imn_path = os.path.join(dreams_dir, filename)
                try:
                    imn_data = read_imn(imn_path)
                    pre_production = imn_data.get('pre_production', {})
                    in_production = imn_data.get('in_production', [])
                    
                    # Create dream card from IMN data
                    dream_card = DreamCard(
                        dream_id=dream_id,
                        title=pre_production.get('dream_name', 'Untitled Dream'),
                        excerpt=pre_production.get('story_prompt', 'No excerpt available'),
                        story=pre_production.get('initial_goal', 'No story available'),
                        pitch=pre_production.get('pitch', 'No pitch available'),
                        user_id=pre_production.get('user_id', 'cli-user')
                    )
                    
                    dream_card.scene_count = len(in_production)
                    # Store scene data for modal display
                    dream_card.scenes = in_production
                    # Ensure timezone-aware datetime for IMN dreams
                    imn_created_at = pre_production.get('created_at', '2025-07-28T00:00:00Z')
                    if not imn_created_at.endswith('Z') and '+' not in imn_created_at:
                        # If no timezone info, assume UTC
                        imn_created_at = imn_created_at + 'Z'
                    dream_card.created_at = imn_created_at
                    dream_card.test_duration = 0  # We don't have this for CLI dreams
                    
                    # Load director vision and image prompt from IMN data
                    director_vision_data = pre_production.get('director_vision', {})
                    dream_card.director_vision = director_vision_data.get('director_vision', 'No director vision available')
                    dream_card.image_prompt = director_vision_data.get('image_prompt', 'No image prompt available')
                    
                    # Try to find associated image from post_production data
                    post_production = imn_data.get('post_production', {})
                    image_generation = post_production.get('image_generation', {})
                    image_filename = image_generation.get('filename')
                    
                    if image_filename:
                        generated_images_dir = "generated_images"
                        image_path = os.path.join(generated_images_dir, image_filename)
                        if os.path.exists(image_path):
                            with open(image_path, 'rb') as f:
                                image_bytes = f.read()
                                dream_card.image_data = base64.b64encode(image_bytes).decode('utf-8')
                    
                    imn_dreams.append(dream_card_to_dict(dream_card))
                except Exception as e:
                    logger.error(f"Error reading IMN file {filename}: {e}")
    
    # Combine all dreams and deduplicate by dream ID
    # Merge data: prefer IMN data for completeness, but preserve GUI duration
    dreams_dict = {}
    
    # First add GUI dreams (with duration data)
    for dream in gui_dreams:
        dreams_dict[dream['id']] = dream
    
    # Then add/merge IMN dreams (with complete scene data)
    for dream in imn_dreams:
        dream_id = dream['id']
        if dream_id in dreams_dict:
            # Merge: keep GUI duration, use IMN scene data
            existing_dream = dreams_dict[dream_id]
            # Preserve duration from GUI version
            duration = existing_dream.get('test_duration', 0)
            # Use IMN data (more complete) but preserve duration
            dreams_dict[dream_id] = dream
            dreams_dict[dream_id]['test_duration'] = duration
            print(f"[get_dreams] Merged duplicate dream {dream_id}: duration={duration}s, scenes={dream.get('scene_count', 0)}")
        else:
            # New dream from IMN only
            dreams_dict[dream_id] = dream
    
    all_dreams = list(dreams_dict.values())
    print(f"[get_dreams] Returned {len(all_dreams)} deduplicated dreams (GUI: {len(gui_dreams)}, IMN: {len(imn_dreams)})")
    
    # Sort dreams by creation date (newest first)
    def get_created_at(dream):
        created_at = dream.get('created_at', '2025-07-28T00:00:00Z')
        try:
            # Parse ISO format datetime and ensure timezone awareness
            from datetime import datetime
            import pytz
            
            # Handle different datetime formats
            if created_at.endswith('Z'):
                # UTC timezone
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            elif '+' in created_at or created_at.endswith('UTC'):
                # Already timezone-aware
                dt = datetime.fromisoformat(created_at.replace('UTC', '+00:00'))
            else:
                # Assume local timezone if no timezone info
                dt = datetime.fromisoformat(created_at)
                # Make it timezone-aware by assuming local timezone
                import time
                local_offset = time.timezone if time.daylight == 0 else time.altzone
                local_tz = pytz.FixedOffset(-local_offset // 60)
                dt = local_tz.localize(dt)
            
            return dt
        except Exception as e:
            logger.warning(f"Failed to parse datetime '{created_at}': {e}")
            # Fallback to string comparison if parsing fails
            return created_at
    
    # Sort by creation date, newest first
    all_dreams.sort(key=get_created_at, reverse=True)
    
    logger.info(f"📋 Returning {len(all_dreams)} dreams sorted by creation date (newest first)")
    return jsonify(all_dreams)

@app.route('/api/dream/<dream_id>')
def get_dream(dream_id):
    """Get a specific dream by ID"""
    global test_results
    for dream in test_results:
        if dream.dream_id == dream_id:
            return jsonify(dream_card_to_dict(dream))
    return jsonify({'error': 'Dream not found'}), 404

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate a new image for a dream using SDXL Turbo"""
    try:
        data = request.get_json()
        dream_id = data.get('dream_id')
        prompt = data.get('prompt')
        
        if not dream_id or not prompt:
            return jsonify({'error': 'Missing dream_id or prompt'}), 400
        
        logger.info(f"🎨 Generating image with SDXL Turbo, prompt: {prompt}")
        update_debug_info("SDXL Turbo", "API Generation Start", {"prompt": prompt, "dream_id": dream_id})
        
        # Use SDXL Turbo with 1024x1024 resolution
        # Use a random seed to ensure unique images
        import random
        random_seed = random.randint(1, 1000000)
        logger.info(f"🎲 API using random seed: {random_seed} for unique image generation")
        image_data = generate_dream_image(
            prompt=prompt,
            service="sdxl_turbo",
            width=1024,
            height=1024,
            num_inference_steps=1,
            guidance_scale=0.0,
            seed=random_seed
        )
        
        if image_data and image_data.get('service') == 'sdxl_turbo':
            generation_time = image_data.get('metadata', {}).get('generation_time', 0)
            logger.info(f"✅ SDXL Turbo API generation successful! Time: {generation_time:.2f}s")
            update_debug_info("SDXL Turbo", "API Generation Complete", {
                "generation_time": generation_time,
                "filename": image_data.get('filename')
            })
            
            return jsonify({
                'image_data': image_data,
                'service': 'sdxl_turbo',
                'generation_time': generation_time
            })
        else:
            error_msg = f"SDXL Turbo API generation failed: {image_data}"
            logger.error(error_msg)
            update_debug_info("SDXL Turbo", "API Generation Failed", {"error": error_msg})
            return jsonify({'error': error_msg}), 500
        
    except Exception as e:
        error_msg = f"SDXL Turbo API image generation failed: {str(e)}"
        logger.error(error_msg)
        update_debug_info("SDXL Turbo", "API Generation Error", {"error": str(e)})
        return jsonify({'error': error_msg}), 500

@app.route('/api/image/<dream_id>')
def get_dream_image(dream_id):
    """Get image for a specific dream"""
    global test_results
    for dream in test_results:
        if dream.dream_id == dream_id and dream.image_data:
            return jsonify({'image_data': dream.image_data})
    return jsonify({'error': 'Image not found'}), 404

@app.route('/api/clear', methods=['POST'])
def clear_tests():
    """Clear all test results"""
    global test_results, current_test, debug_info
    test_results = []
    current_test = None
    reset_debug_info()
    logger.info("All test results cleared")
    return jsonify({'status': 'success', 'message': 'All tests cleared'})

@app.route('/api/debug')
def get_debug_info():
    """Get detailed debug information"""
    global debug_info
    return jsonify(debug_info)

if __name__ == '__main__':
    logger.info("Starting Dreams.ai GUI Test Suite...")
    logger.info("Server will be available at: http://localhost:5000")
    
    # Disable Flask's default logging to avoid Windows console issues
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Run Flask with Windows-compatible settings
    try:
        # Use localhost binding to avoid Windows handle errors
        app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.info("If you see 'Windows error 6', try running as Administrator or check Windows Defender/Firewall settings") 