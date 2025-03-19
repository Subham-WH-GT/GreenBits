
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import os

# Load model
MODEL_PATH = "model/e_waste_classifier.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Load class labels dynamically
dataset_dir = "C:/Users/user/Desktop/GreenBits/modified-dataset"
train_dir = os.path.join(dataset_dir, "train")
categories = sorted(os.listdir(train_dir))  # Gets the folder names (class labels)

# Function to preprocess images before prediction
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Prediction function
def predict_e_waste(img_path):
    img_array = preprocess_image(img_path)
    pred = model.predict(img_array)
    
    # Print probability distribution for debugging
    print("Raw Predictions:", pred)

    predicted_class = categories[np.argmax(pred)]
    confidence = np.max(pred)  # Get the highest probability

    return predicted_class, confidence

# Test the function
# test_image = "static/uploads/tv.jpg"  # Change this to an actual image path
# predicted_label, confidence = predict_e_waste(test_image)

# print(f"Predicted Class: {predicted_label}, Confidence: {confidence:.2f}")