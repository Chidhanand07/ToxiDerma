
#!/usr/bin/env python3
"""
ToxiDerma-XAI Training Script
Train the arsenic lesion detection model using transfer learning
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from toxiderma_model import ToxiDermaXAI

def create_sample_data_structure():
    """Create sample data directory structure"""
    directories = [
        'data/train/affected',
        'data/train/healthy',
        'data/validation/affected', 
        'data/validation/healthy',
        'data/test/affected',
        'data/test/healthy',
        'models',
        'results'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def plot_training_history(history, save_path='results/training_history.png'):
    """Plot training history"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    # Accuracy
    axes[0,0].plot(history['accuracy'], label='Training Accuracy')
    axes[0,0].plot(history['val_accuracy'], label='Validation Accuracy')
    axes[0,0].set_title('Model Accuracy')
    axes[0,0].set_xlabel('Epoch')
    axes[0,0].set_ylabel('Accuracy')
    axes[0,0].legend()
    axes[0,0].grid(True)

    # Loss
    axes[0,1].plot(history['loss'], label='Training Loss')
    axes[0,1].plot(history['val_loss'], label='Validation Loss')
    axes[0,1].set_title('Model Loss')
    axes[0,1].set_xlabel('Epoch')
    axes[0,1].set_ylabel('Loss')
    axes[0,1].legend()
    axes[0,1].grid(True)

    # Remove empty subplots
    axes[1,0].remove()
    axes[1,1].remove()

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"Training history saved to {save_path}")

def train_model(data_dir, model_type='resnet50', epochs=50, batch_size=32):
    """Main training function"""

    print("="*60)
    print("ToxiDerma-XAI Model Training")
    print("="*60)

    print(f"Initializing {model_type} model...")
    toxiderma = ToxiDermaXAI()

    model = toxiderma.build_model(transfer_model=model_type)
    print("Model architecture:")
    model.summary()

    print("\nPreparing data generators...")
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'validation')
    test_dir = os.path.join(data_dir, 'test')

    if not all(os.path.exists(d) for d in [train_dir, val_dir]):
        print("Error: Data directories not found!")
        print("Please ensure the following structure exists:")
        print("data/")
        print("├── train/")
        print("│   ├── affected/")
        print("│   └── healthy/")
        print("├── validation/")
        print("│   ├── affected/")
        print("│   └── healthy/")
        print("└── test/")
        print("    ├── affected/")
        print("    └── healthy/")
        return None

    try:
        train_generator, val_generator = toxiderma.prepare_data_generators(
            train_dir, val_dir, batch_size=batch_size
        )

        print(f"Training samples: {train_generator.samples}")
        print(f"Validation samples: {val_generator.samples}")
        print(f"Classes: {train_generator.class_indices}")

    except Exception as e:
        print(f"Error preparing data: {e}")
        print("Please ensure your data directories contain images.")
        return None

    print("\nStarting training...")
    try:
        history = toxiderma.train_model(
            train_generator, 
            val_generator, 
            epochs=epochs
        )

        plot_training_history(history)

        model_path = f'models/toxiderma_{model_type}_model.h5'
        toxiderma.save_model(model_path)

        if os.path.exists(test_dir) and len(os.listdir(test_dir)) > 0:
            print("\nEvaluating on test set...")
            try:
                from tensorflow.keras.preprocessing.image import ImageDataGenerator
                test_datagen = ImageDataGenerator(rescale=1./255)
                test_generator = test_datagen.flow_from_directory(
                    test_dir,
                    target_size=(224, 224),
                    batch_size=batch_size,
                    class_mode='categorical',
                    shuffle=False
                )

                test_results = toxiderma.evaluate_model(test_generator)
                print(f"Test Results: {test_results}")

            except Exception as e:
                print(f"Test evaluation failed: {e}")

        print("\n" + "="*60)
        print("Training completed successfully!")
        print(f"Model saved to: {model_path}")
        print("="*60)

        return toxiderma

    except Exception as e:
        print(f"Training failed: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Train ToxiDerma-XAI model')
    parser.add_argument('--data_dir', default='data', help='Path to data directory')
    parser.add_argument('--model', default='resnet50', choices=['resnet50', 'efficientnet'],
                      help='Base model architecture')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--setup_dirs', action='store_true', 
                      help='Create sample data directory structure')

    args = parser.parse_args()

    if args.setup_dirs:
        print("Setting up data directory structure...")
        create_sample_data_structure()
        print("\nDirectory structure created!")
        print("Please place your images in the appropriate directories before training.")
        return

    if not os.path.exists(args.data_dir):
        print(f"Data directory '{args.data_dir}' not found!")
        print("Use --setup_dirs to create the directory structure.")
        return

    model = train_model(
        data_dir=args.data_dir,
        model_type=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size
    )

    if model is None:
        print("Training failed!")
        sys.exit(1)
    else:
        print("Training completed successfully!")

if __name__ == "__main__":
    main()
