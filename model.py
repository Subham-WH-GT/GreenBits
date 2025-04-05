
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import os

# Load model
MODEL_PATH = "model/e_waste_classifier.h5"
model = tf.keras.models.load_model(MODEL_PATH)


dataset_dir = "C:/Users/user/Desktop/GreenBit/modified-dataset"
train_dir = os.path.join(dataset_dir, "train")
categories = sorted(os.listdir(train_dir))  


def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0 
    img_array = np.expand_dims(img_array, axis=0) 
    return img_array


def predict_e_waste(img_path):
    img_array = preprocess_image(img_path)
    pred = model.predict(img_array)
    
   
    print("Raw Predictions:", pred)

    predicted_class = categories[np.argmax(pred)]
    confidence = np.max(pred)  # Get the highest probability

    return predicted_class, confidence

# Test the function
# test_image = "static/uploads/tv.jpg"  # Change this to an actual image path
# predicted_label, confidence = predict_e_waste(test_image)

# print(f"Predicted Class: {predicted_label}, Confidence: {confidence:.2f}")