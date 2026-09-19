from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import base64
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from toxiderma_model import ToxiDermaXAI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/results', exist_ok=True)

# Initialize model (load pre-trained model)
toxiderma_model = ToxiDermaXAI()

# Global variable to store model
model_loaded = False

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model_if_needed():
    """Load model if not already loaded"""
    global model_loaded, toxiderma_model
    if not model_loaded:
        try:
            toxiderma_model.load_model('models/best_model.h5')
            model_loaded = True
            print("✅ Model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    return True

def image_to_base64(image_array):
    """Convert numpy array image to base64 string"""
    try:
        if image_array is None:
            return None
        
        # Handle different image formats
        if isinstance(image_array, np.ndarray):
            # Ensure image is in correct format
            if image_array.dtype != np.uint8:
                if image_array.max() <= 1.0:
                    image_array = (image_array * 255).astype(np.uint8)
                else:
                    image_array = image_array.astype(np.uint8)
            
            # Convert to PIL Image
            if len(image_array.shape) == 3:
                image = Image.fromarray(image_array)
            else:
                image = Image.fromarray(image_array, mode='L')
        else:
            image = image_array
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode()
        return image_b64
        
    except Exception as e:
        print(f"Image conversion error: {e}")
        return None

@app.route('/')
def home():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'File uploaded successfully'
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """Make prediction on uploaded image"""
    try:
        print("=== PREDICT ENDPOINT CALLED ===")
        
        # Load model if not loaded
        if not load_model_if_needed():
            return jsonify({'success': False, 'error': 'Model failed to load'}), 500
        
        # Check if file was uploaded
        if 'file' not in request.files:
            print("ERROR: No file in request")
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({'success': False, 'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Use JPG, JPEG, or PNG'}), 400
            
        print(f"File received: {file.filename}")
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        print(f"File saved to: {temp_path}")
        
        # Make prediction using your model
        result = toxiderma_model.predict_single_image(temp_path)
        print(f"Prediction result: {result}")
        
        # Generate explanations
        gradcam_b64 = None
        lime_b64 = None
        
        try:
            print("Generating Grad-CAM...")
            gradcam_overlay, gradcam_heatmap = toxiderma_model.generate_gradcam(temp_path)
            gradcam_b64 = image_to_base64(gradcam_overlay)
            print("✅ Grad-CAM generated")
        except Exception as gradcam_error:
            print(f"❌ Grad-CAM error: {gradcam_error}")
            
        try:
            print("Generating LIME...")
            lime_explanation, _ = toxiderma_model.generate_lime_explanation(temp_path)
            lime_b64 = image_to_base64(lime_explanation)
            print("✅ LIME generated")
        except Exception as lime_error:
            print(f"❌ LIME error: {lime_error}")
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Return successful response
        response = {
            'success': True,
            'prediction': result['class'],
            'confidence': result['confidence'],
            'probabilities': result['probabilities'],
            'explanation': f"The AI detected {result['class'].lower()} tissue with {result['confidence']*100:.1f}% confidence.",
            'gradcam_image': gradcam_b64,
            'lime_image': lime_b64
        }
        
        print("SUCCESS: Returning prediction response")
        return jsonify(response)
        
    except Exception as e:
        print(f"CRITICAL ERROR in /predict: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/explain', methods=['POST'])
def explain():
    """Generate explanations for prediction"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        explanation_type = data.get('type', 'gradcam')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        # Load model if needed
        if not load_model_if_needed():
            return jsonify({'error': 'Model not available'}), 500
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        if explanation_type == 'gradcam':
            # Generate Grad-CAM
            overlay, heatmap = toxiderma_model.generate_gradcam(filepath)
            # Save explanation image
            explanation_filename = f"gradcam_{filename}"
            explanation_path = os.path.join('static/results', explanation_filename)
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1)
            plt.imshow(overlay)
            plt.title('Grad-CAM Overlay')
            plt.axis('off')
            plt.subplot(1, 2, 2)
            plt.imshow(heatmap)
            plt.title('Attention Heatmap')
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(explanation_path, bbox_inches='tight', dpi=150)
            plt.close()
            return jsonify({
                'success': True,
                'explanation_image': f'/static/results/{explanation_filename}',
                'type': 'gradcam'
            })
        elif explanation_type == 'lime':
            # Generate LIME explanation
            boundary_image, explanation = toxiderma_model.generate_lime_explanation(filepath)
            # Save explanation image
            explanation_filename = f"lime_{filename}"
            explanation_path = os.path.join('static/results', explanation_filename)
            plt.figure(figsize=(8, 6))
            plt.imshow(boundary_image)
            plt.title('LIME Explanation')
            plt.axis('off')
            plt.savefig(explanation_path, bbox_inches='tight', dpi=150)
            plt.close()
            return jsonify({
                'success': True,
                'explanation_image': f'/static/results/{explanation_filename}',
                'type': 'lime'
            })
        else:
            return jsonify({'error': 'Invalid explanation type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    model_status = 'loaded' if model_loaded else 'not loaded'
    return jsonify({
        'status': 'healthy',
        'model_status': model_status,
        'version': '1.0.0'
    })

@app.route('/model-info')
def model_info():
    """Get model information"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        # Get model architecture info
        total_params = toxiderma_model.model.count_params()
        return jsonify({
            'model_name': 'ToxiDerma-XAI',
            'architecture': 'ResNet50 + Transfer Learning',
            'total_parameters': int(total_params),
            'input_shape': toxiderma_model.input_shape,
            'num_classes': toxiderma_model.num_classes,
            'classes': ['Affected', 'Healthy']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Try to load model on startup
    print("Starting ToxiDerma-XAI application...")
    load_model_if_needed()
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=8000)
