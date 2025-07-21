"""
GUI Test Suite for Dreams.ai
Displays dream cards and allows testing the complete pipeline with visual feedback.
"""

import json
import os
import sys
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import time

# Add the current directory to the path so we can import from main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import graph
from core.imn_utils import validate_imn_structure, read_imn, create_imn_structure
from core.image_generator import generate_dream_image

app = Flask(__name__)
CORS(app)

# Global state for test results
test_results = []
current_test = None

class DreamCard:
    """Represents a dream card for display in the GUI"""
    
    def __init__(self, imn_data, dream_id):
        self.id = dream_id
        self.title = imn_data.get('pre_production', {}).get('dream_name', 'Untitled Dream')
        self.excerpt = imn_data.get('pre_production', {}).get('story_prompt', '')[:200] + '...'
        self.content = imn_data.get('pre_production', {}).get('pitch', '')
        self.creator = {
            'id': imn_data.get('pre_production', {}).get('user_id', 'unknown'),
            'name': 'Test User',
            'avatar': None,
            'verified': False
        }
        self.engagement = {
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'views': 0
        }
        self.tags = []
        self.category = ''
        self.emotion = ''
        self.theme = ''
        self.created_at = imn_data.get('pre_production', {}).get('created_at', datetime.now().isoformat())
        self.is_trending = False
        self.is_featured = False
        self.similarity_score = None
        
        # Additional test-specific data
        self.test_status = 'pending'
        self.test_duration = 0
        self.error_message = None
        self.scenes = imn_data.get('in_production', [])
        self.director_vision = imn_data.get('pre_production', {}).get('director_vision', {})
        self.image_prompt = imn_data.get('pre_production', {}).get('first_frame_prompt', '')
        self.generated_image = None

def dream_card_to_dict(card):
    """Convert DreamCard object to dictionary for JSON serialization"""
    return {
        'id': card.id,
        'title': card.title,
        'excerpt': card.excerpt,
        'content': card.content,
        'creator': card.creator,
        'engagement': card.engagement,
        'tags': card.tags,
        'category': card.category,
        'emotion': card.emotion,
        'theme': card.theme,
        'created_at': card.created_at,
        'is_trending': card.is_trending,
        'is_featured': card.is_featured,
        'similarity_score': card.similarity_score,
        'test_status': card.test_status,
        'test_duration': card.test_duration,
        'error_message': card.error_message,
        'scenes': card.scenes,
        'director_vision': card.director_vision,
        'image_prompt': card.image_prompt,
        'generated_image': card.generated_image
    }

def run_pipeline_test(prompt, user_id="test-user"):
    """Run the complete pipeline and return results"""
    global current_test
    
    start_time = time.time()
    
    try:
        # Initialize state
        state = {
            "messages": [{"role": "user", "content": prompt}],
            "user_id": user_id
        }
        
        current_test = {
            'prompt': prompt,
            'status': 'running',
            'start_time': start_time,
            'progress': 0
        }
        
        # Run the pipeline
        result = graph.invoke(state)
        
        # Get the dream ID and read the .imn file
        dream_id = result.get("id")
        if dream_id:
            imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
            imn_data = read_imn(imn_file_path)
            
            if imn_data:
                # Create dream card
                dream_card = DreamCard(imn_data, dream_id)
                dream_card.test_status = 'completed'
                dream_card.test_duration = time.time() - start_time
                
                # Generate image if prompt is available
                if dream_card.image_prompt:
                    try:
                        image_result = generate_dream_image(dream_card.image_prompt)
                        if image_result:
                            dream_card.generated_image = image_result
                    except Exception as e:
                        print(f"Image generation failed: {e}")
                
                current_test['status'] = 'completed'
                current_test['dream_card'] = dream_card
                current_test['duration'] = dream_card.test_duration
                
                return dream_card
            else:
                current_test['status'] = 'error'
                current_test['error'] = 'Failed to read .imn file'
                return None
        else:
            current_test['status'] = 'error'
            current_test['error'] = 'No dream ID generated'
            return None
            
    except Exception as e:
        current_test['status'] = 'error'
        current_test['error'] = str(e)
        return None

@app.route('/')
def index():
    """Main test interface"""
    return render_template('test_interface.html')

@app.route('/api/test', methods=['POST'])
def run_test():
    """API endpoint to run a pipeline test"""
    global test_results, current_test
    
    data = request.get_json()
    prompt = data.get('prompt', 'A magical forest adventure')
    user_id = data.get('user_id', f'test-user-{uuid.uuid4().hex[:8]}')
    
    # Run test in background thread
    def test_worker():
        global test_results
        dream_card = run_pipeline_test(prompt, user_id)
        if dream_card:
            test_results.append(dream_card)
    
    thread = threading.Thread(target=test_worker)
    thread.start()
    
    return jsonify({'status': 'started', 'message': 'Test started'})

@app.route('/api/status')
def get_status():
    """Get current test status"""
    global current_test, test_results
    
    return jsonify({
        'current_test': current_test,
        'test_count': len(test_results),
        'recent_tests': [dream_card_to_dict(card) for card in test_results[-5:]]  # Last 5 tests
    })

@app.route('/api/dreams')
def get_dreams():
    """Get all test dreams"""
    global test_results
    
    return jsonify([dream_card_to_dict(card) for card in test_results])

@app.route('/api/dream/<dream_id>')
def get_dream(dream_id):
    """Get specific dream details"""
    global test_results
    
    for card in test_results:
        if card.id == dream_id:
            return jsonify(dream_card_to_dict(card))
    
    return jsonify({'error': 'Dream not found'}), 404

@app.route('/api/clear')
def clear_tests():
    """Clear all test results"""
    global test_results, current_test
    
    test_results = []
    current_test = None
    
    return jsonify({'status': 'cleared'})

@app.route('/api/image/<dream_id>')
def get_dream_image(dream_id):
    """Get generated image for a dream"""
    global test_results
    
    for card in test_results:
        if card.id == dream_id and card.generated_image:
            return jsonify({
                'image_data': card.generated_image['image_data'],
                'filename': card.generated_image['filename'],
                'prompt': card.generated_image['prompt'],
                'service': card.generated_image['service']
            })
    
    return jsonify({'error': 'Image not found'}), 404

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """Generate a new image from a prompt"""
    data = request.get_json()
    prompt = data.get('prompt')
    service = data.get('service', 'placeholder')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        image_result = generate_dream_image(prompt, service)
        if image_result:
            return jsonify({
                'image_data': image_result['image_data'],
                'filename': image_result['filename'],
                'prompt': image_result['prompt'],
                'service': image_result['service']
            })
        else:
            return jsonify({'error': 'Image generation failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create static directory for CSS/JS
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    print("Starting Dreams.ai GUI Test Suite...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000) 