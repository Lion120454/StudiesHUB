#Использовать предобученную сеть библиотеки keras для задачи классификации изображений. Задание б.

import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt


model = MobileNetV2(weights='imagenet')

def classify_image(img_path):
    # Загрузка и подготовка изображения
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
    # Получение предсказаний
    predictions = model.predict(img_array)
    
    # Декодирование предсказаний
    decoded_predictions = decode_predictions(predictions, top=3)[0]
    
    # Визуализация
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title('Исходное изображение')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    y_pos = np.arange(len(decoded_predictions))
    scores = [pred[2] for pred in decoded_predictions]
    labels = [f"{pred[1]}: {pred[2]:.2f}" for pred in decoded_predictions]
    
    plt.barh(y_pos, scores)
    plt.yticks(y_pos, labels)
    plt.xlabel('Вероятность')
    plt.title('Топ-3 предсказания')
    
    plt.tight_layout()
    plt.show()
    
    return decoded_predictions

# Использование
result = classify_image('lab1_b.jpg')
for i, pred in enumerate(result):
    print(f"{i+1}. {pred[1]}: {pred[2]:.2%}")