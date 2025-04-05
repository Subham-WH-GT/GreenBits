
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model


dataset_dir = "C:/Users/user/Desktop/GreenBit/modified-dataset"  # Update this with the actual dataset path

train_dir = os.path.join(dataset_dir, "train")
val_dir = os.path.join(dataset_dir, "val")


IMG_SIZE = (224, 224)
BATCH_SIZE = 32


train_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode="nearest"
)


val_datagen = ImageDataGenerator(rescale=1.0 / 255.0)


train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)

val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical"
)


base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))


for layer in base_model.layers:
    layer.trainable = False


x = base_model.output
x = GlobalAveragePooling2D()(x)  
x = Dense(256, activation="relu")(x)
x = Dropout(0.5)(x) 
output_layer = Dense(len(train_generator.class_indices), activation="softmax")(x)  


model = Model(inputs=base_model.input, outputs=output_layer)


model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)


EPOCHS = 20  
history = model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=val_generator
)

# Save the model
model_save_path = "model/e_waste_classifier.h5"
os.makedirs("model", exist_ok=True)  
model.save(model_save_path)

print(f"Model training complete and saved at {model_save_path}!")