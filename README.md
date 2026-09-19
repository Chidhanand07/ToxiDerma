# ToxiDerma-XAI: AI-Powered Arsenic Lesion Detection

An advanced AI system for detecting arsenic-induced skin lesions using transfer learning and explainable AI techniques.

![ToxiDerma-XAI](https://img.shields.io/badge/AI-Medical%20Diagnosis-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-green) ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.8%2B-orange)

##  Project Overview

ToxiDerma-XAI is a comprehensive AI solution designed to assist healthcare professionals in detecting and analyzing arsenic-induced skin lesions. The system combines:

- **Transfer Learning**: Uses pre-trained ResNet50/EfficientNet models
- **Explainable AI**: Provides Grad-CAM and LIME explanations
- **Web Interface**: User-friendly interface for clinical use
- **Real-time Analysis**: Fast prediction and explanation generation

##  Project Structure

```
toxiderma-xai/
├── app.py                 # Flask web application
├── toxiderma_model.py     # Main AI model class
├── train.py              # Training script
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── style.css     # Custom styling
│   └── js/
│       └── app.js        # Frontend JavaScript
├── data/                 # Training data (create this)
│   ├── train/
│   ├── validation/
│   └── test/
├── models/               # Saved models
├── uploads/              # Uploaded images
└── results/              # Training results
```

##  Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd toxiderma-xai

# Create virtual environment
python -m venv toxiderma_env
source toxiderma_env/bin/activate  # On Windows: toxiderma_env\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Set Up Data Structure

```bash
# Create data directories
python train.py --setup_dirs

# Your data structure should look like:
# data/
# ├── train/
# │   ├── affected/    # Put affected skin images here
# │   └── healthy/     # Put healthy skin images here
# ├── validation/
# │   ├── affected/
# │   └── healthy/
# └── test/
#     ├── affected/
#     └── healthy/
```

### 3. Train the Model

```bash
# Train with default settings (ResNet50, 50 epochs)
python train.py

# Or customize training
python train.py --model efficientnet --epochs 30 --batch_size 16
```

### 4. Run the Web Application

```bash
# Start the Flask application
python app.py

# Access the application at http://localhost:5000
```

## 💻 Usage Guide

### Web Interface

1. **Upload Image**: Drag and drop or click to upload skin image
2. **Analyze**: Click "Analyze Image" to get AI prediction
3. **View Results**: See classification and confidence scores
4. **Explanations**: Generate Grad-CAM or LIME visualizations
5. **Clear**: Reset and upload new image

### API Endpoints

- `POST /upload` - Upload image file
- `POST /predict` - Get AI prediction
- `POST /explain` - Generate explanations
- `GET /health` - Check system health
- `GET /model-info` - Get model information

### Command Line Training

```bash
# Basic training
python train.py

# Advanced options
python train.py \
    --data_dir ./my_data \
    --model resnet50 \
    --epochs 100 \
    --batch_size 32
```

## 🧠 Model Architecture

The system uses transfer learning with the following architecture:

```
Input Image (224x224x3)
↓
Pre-trained Base Model (ResNet50/EfficientNet)
↓
Global Average Pooling
↓
Dense Layer (128 neurons, ReLU)
↓
Dropout (0.5)
↓
Dense Layer (64 neurons, ReLU)
↓
Dropout (0.3)
↓
Output Layer (2 classes, Softmax)
```

## 📊 Explainable AI Features

### Grad-CAM (Gradient-weighted Class Activation Mapping)
- Highlights important regions in the image
- Shows where the model "looks" when making decisions
- Provides intuitive visual explanations

### LIME (Local Interpretable Model-agnostic Explanations)
- Explains individual predictions
- Shows which image regions influence the decision
- Complements Grad-CAM with different perspective

## 🎯 Performance Metrics

The model is evaluated using:
- **Accuracy**: Overall classification accuracy
- **Precision**: Positive predictive value
- **Recall (Sensitivity)**: True positive rate
- **Specificity**: True negative rate
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under ROC curve

## 🛠️ Development

### Adding New Features

1. **Model Improvements**:
   - Add new architectures in `toxiderma_model.py`
   - Implement ensemble methods
   - Add severity grading

2. **UI Enhancements**:
   - Modify templates in `templates/`
   - Update styling in `static/css/`
   - Add functionality in `static/js/`

3. **API Extensions**:
   - Add new endpoints in `app.py`
   - Implement batch processing
   - Add model comparison features

### Code Structure

- `ToxiDermaXAI`: Main model class with all ML functionality
- `Flask App`: Web server handling HTTP requests
- `Frontend`: HTML/CSS/JS for user interface
- `Training Script`: Command-line training interface

## 🔒 Medical Disclaimer

⚠️ **Important**: This tool is designed for research and educational purposes only. It should not be used as a substitute for professional medical diagnosis or treatment. Always consult qualified healthcare professionals for medical advice.

## 📝 Requirements

- Python 3.8+
- TensorFlow 2.8+
- 8GB+ RAM (16GB recommended)
- GPU support (optional but recommended)
- Modern web browser

##  Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request



##  Acknowledgments

- **RNS Institute of Technology** - Department of AI & ML
- **Dr. Mamatha S K** - Project Guide
- **Research Team**: Sampreeth BM, Chamarthy Bhanu Sri Varsha, Chidanandh R, Raghu O

##  References

Based on research from:
- Transfer Learning for Medical Image Analysis
- Explainable AI in Healthcare Applications
- Arsenic-induced Skin Lesion Studies
- Deep Learning for Dermatological Applications

##  Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create new issue with detailed description
4. Contact the development team

---


