import tensorflow as tf
from PIL import Image
import numpy as np
from io import BytesIO
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, BatchNormalization, MaxPooling2D, Dropout, Flatten, Dense
from tensorflow.keras.applications import DenseNet121




# Hàm để tải model
def load_model(model_path="model\ckpt_epoch_13.weights.h5"):
    conv_base = DenseNet121(
        weights='imagenet',
        include_top = False,
        input_shape=(256,256,3),
        pooling='avg'
    )
    conv_base.trainable = False
    model = Sequential()
    model.add(conv_base)
    model.add(BatchNormalization())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.35))
    model.add(BatchNormalization())
    model.add(Dense(120, activation='relu'))
    model.add(Dense(10, activation='softmax'))
    model.load_weights(model_path)
    return model

def preprocess_image(file: bytes, target_size):
    image = Image.open(BytesIO(file)).convert("RGB")  
    image = image.resize(target_size)  
    image_array = np.array(image) / 255.0  
    return np.expand_dims(image_array, axis=0) 

# Hàm để dự đoán
def predict(input_data, model):
   
    input_data = preprocess_image(input_data,(256,256))
    # Thực hiện dự đoán
    predictions = model.predict(input_data)
    class_names = ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']
    return class_names[np.argmax(predictions , axis=1)[0]]
