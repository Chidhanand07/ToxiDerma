import tensorflow as tf
from tensorflow.keras import layers, models, applications
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import cv2
from lime import lime_image
from skimage.segmentation import mark_boundaries
import matplotlib.pyplot as plt

class ToxiDermaXAI:
    def __init__(self, input_shape=(224, 224, 3), num_classes=2):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None

        self.class_indices = {'Affected': 0, 'Healthy': 1}
        
    def build_model(self, transfer_model='resnet50'):
        """Build transfer learning model"""

        if transfer_model == 'resnet50':
            base_model = applications.ResNet50(
                weights='imagenet',
                include_top=False,
                input_shape=self.input_shape
            )
        elif transfer_model == 'efficientnet':
            base_model = applications.EfficientNetB0(
                weights='imagenet',
                include_top=False,
                input_shape=self.input_shape
            )

        base_model.trainable = False

        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.BatchNormalization(),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        return model
    
    def prepare_data_generators(self, train_dir, val_dir, batch_size=32):

        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            brightness_range=[0.8, 1.2],
            fill_mode='nearest'
        )

        val_datagen = ImageDataGenerator(rescale=1./255)
        
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        return train_generator, val_generator
    
    def train_model(self, train_generator, val_generator, epochs=50):
        """Train the model with callbacks"""
        
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            ),
            tf.keras.callbacks.ModelCheckpoint(
                'models/best_model.h5',
                monitor='val_accuracy',
                save_best_only=True
            )
        ]
        

        print("Phase 1: Training with frozen base model...")
        history1 = self.model.fit(
            train_generator,
            epochs=10,
            validation_data=val_generator,
            callbacks=callbacks
        )
        

        print("Phase 2: Fine-tuning...")
        self.model.layers[0].trainable = True
        

        for layer in self.model.layers[0].layers[:-20]:
            layer.trainable = False
        

        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        history2 = self.model.fit(
            train_generator,
            epochs=epochs-10,
            validation_data=val_generator,
            callbacks=callbacks
        )

        self.history = {
            'loss': history1.history['loss'] + history2.history['loss'],
            'accuracy': history1.history['accuracy'] + history2.history['accuracy'],
            'val_loss': history1.history['val_loss'] + history2.history['val_loss'],
            'val_accuracy': history1.history['val_accuracy'] + history2.history['val_accuracy']
        }
        
        return self.history
    
    def predict_single_image(self, image_path):

        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, self.input_shape[:2])
        image = image / 255.0
        image = np.expand_dims(image, axis=0)
        
        # Make prediction
        prediction = self.model.predict(image)
        confidence = np.max(prediction)
        class_pred = np.argmax(prediction)
        

        label_map = {v: k for k, v in self.class_indices.items()}
        predicted_class = label_map.get(class_pred, 'Unknown')
        
        return {
            'class': predicted_class,
            'confidence': float(confidence),
            'probabilities': {
                label_map[0]: float(prediction[0][0]),
                label_map[1]: float(prediction[0][1])
            }
        }
    
    def generate_gradcam(self, image_path, layer_name=None):

        if layer_name is None:
            layer_name = 'conv5_block3_out'  # Last conv layer in ResNet50
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        original_image = image.copy()
        image = cv2.resize(image, self.input_shape[:2])
        image = image / 255.0
        image = np.expand_dims(image, axis=0)
        
        # Access the base model (ResNet50) inside the Sequential model
        base_model = self.model.layers[0]
        
        # Create a model for gradient computation
        with tf.GradientTape() as tape:
            # Get conv layer output and predictions
            conv_outputs = base_model.get_layer(layer_name).output
            grad_model = tf.keras.models.Model(
                [base_model.inputs], [conv_outputs, base_model.output]
            )
            
            with tf.GradientTape() as tape2:
                conv_outputs, base_predictions = grad_model(image)
                # Pass through remaining layers of the main model
                x = self.model.layers[1](base_predictions)  # GlobalAveragePooling2D
                x = self.model.layers[2](x)  # BatchNormalization
                x = self.model.layers[3](x)  # Dense 128
                x = self.model.layers[4](x)  # Dropout
                x = self.model.layers[5](x)  # Dense 64
                x = self.model.layers[6](x)  # Dropout
                predictions = self.model.layers[7](x)  # Final Dense
                
                class_idx = tf.argmax(predictions[0])
                loss = predictions[:, class_idx]
        
        # Calculate gradients
        grads = tape2.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Generate heatmap
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        heatmap = heatmap.numpy()
        
        # Resize heatmap to original image size
        heatmap = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        
        # Overlay heatmap on original image
        overlay = cv2.addWeighted(original_image, 0.6, heatmap, 0.4, 0)
        
        return overlay, heatmap
    
    def generate_lime_explanation(self, image_path, num_samples=1000):
        """Generate LIME explanation for image"""
        # Load and preprocess image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, self.input_shape[:2])
        image = image / 255.0
        
        # Create LIME explainer
        explainer = lime_image.LimeImageExplainer()
        
        def predict_proba(images):
            return self.model.predict(images)
        
        # Generate explanation
        explanation = explainer.explain_instance(
            image,
            predict_proba,
            top_labels=2,
            hide_color=0,
            num_samples=num_samples
        )
        
        # Get image and mask for top prediction
        temp, mask = explanation.get_image_and_mask(
            explanation.top_labels[0],
            positive_only=True,
            num_features=10,
            hide_rest=False
        )
        
        # Create boundary image
        boundary_image = mark_boundaries(temp, mask)
        
        return boundary_image, explanation
    
    def save_model(self, filepath):
        """Save trained model"""
        self.model.save(filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        self.model = tf.keras.models.load_model(filepath)
        print(f"Model loaded from {filepath}")
    
    def evaluate_model(self, test_generator):
        """Evaluate model performance"""
        results = self.model.evaluate(test_generator)
        
        # Get predictions for detailed metrics
        predictions = self.model.predict(test_generator)
        y_pred = np.argmax(predictions, axis=1)
        y_true = test_generator.classes
        
        from sklearn.metrics import classification_report, confusion_matrix
        
        print("Classification Report:")
        print(classification_report(y_true, y_pred, 
                                  target_names=['Affected', 'Healthy']))
        
        print("Confusion Matrix:")
        print(confusion_matrix(y_true, y_pred))
        
        return results


if __name__ == "__main__":
    toxiderma = ToxiDermaXAI()

    model = toxiderma.build_model('resnet50')
    print("Model built successfully!")

    model.summary()
