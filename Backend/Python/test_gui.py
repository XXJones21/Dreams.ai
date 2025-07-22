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
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Add the current directory to the path so we can import from main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.pipeline_instance import PipelineInstance
from core.imn_utils import validate_imn_structure, read_imn, create_imn_structure
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
        self.created_at = datetime.now().isoformat()
        self.scene_count = 0
        self.image_data = None
        self.image_prompt = None
        self.director_vision = None

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
    """Convert DreamCard object to dictionary for JSON serialization"""
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
        'image_data': dream_card.image_data,
        'image_prompt': dream_card.image_prompt,
        'director_vision': dream_card.director_vision
    }

def run_pipeline_test(prompt, user_id):
    """Run the complete pipeline test with detailed debugging (using PipelineInstance)"""
    global current_test, test_results, debug_info
    
    logger.info(f"Starting pipeline test with prompt: {prompt}")
    reset_debug_info()
    
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
        pipeline_instance = PipelineInstance(test_state)
        result = pipeline_instance.run()
        update_debug_info("Graph", "Execution Complete", {"result_keys": list(result.keys())})
        
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
            image_prompt = post_production.get('image_prompt', 'No image prompt available')
            dream_card.image_prompt = image_prompt
            
            if image_prompt and image_prompt != 'No image prompt available':
                logger.info(f"Generating image with prompt: {image_prompt}")
                update_debug_info("ImageGenerator", "Processing", {"prompt_length": len(image_prompt)})
                
                image_data = generate_dream_image(image_prompt, dream_id)
                dream_card.image_data = image_data
                
                update_debug_info("ImageGenerator", "Generation Complete")
                logger.info("Image generated successfully")
            else:
                logger.info("No image prompt available")
            
            # Calculate test duration
            if debug_info['total_start_time']:
                dream_card.test_duration = time.time() - debug_info['total_start_time']
            
            update_debug_info("Pipeline", "Test Complete", {"duration": dream_card.test_duration})
            logger.info(f"Test completed successfully in {dream_card.test_duration:.2f} seconds")
            
            # Add to results
            test_results.append(dream_card)
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
    """Get all test dreams"""
    global test_results
    return jsonify([dream_card_to_dict(dream) for dream in test_results])

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
    """Generate a new image for a dream"""
    try:
        data = request.get_json()
        dream_id = data.get('dream_id')
        prompt = data.get('prompt')
        
        if not dream_id or not prompt:
            return jsonify({'error': 'Missing dream_id or prompt'}), 400
        
        image_data = generate_dream_image(prompt, dream_id)
        return jsonify({'image_data': image_data})
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    app.run(debug=True, host='0.0.0.0', port=5000) 