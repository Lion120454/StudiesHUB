#Реализовать нейронную сеть для наложения стиля на изображения (Задание д).
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications import vgg19
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Model
import matplotlib.pyplot as plt
import time
import os

class NeuralStyleTransfer:
    def __init__(self, content_image_path, style_image_path, 
                 img_height=400, img_width=400,
                 content_weight=1e-4, style_weight=1.0, 
                 total_variation_weight=1e-4):
        """
        Инициализация класса для переноса стиля
        
        Args:
            content_image_path: путь к изображению контента
            style_image_path: путь к изображению стиля
            img_height: высота изображения
            img_width: ширина изображения
            content_weight: вес контентной потери
            style_weight: вес стилевой потери
            total_variation_weight: вес потери гладкости
        """
        self.content_path = content_image_path
        self.style_path = style_image_path
        self.img_height = img_height
        self.img_width = img_width
        self.content_weight = content_weight
        self.style_weight = style_weight
        self.total_variation_weight = total_variation_weight
        
        # Загрузка и подготовка изображений
        self.content_image = self.load_and_preprocess(content_image_path)
        self.style_image = self.load_and_preprocess(style_image_path)
        
        # Инициализация сгенерированного изображения
        self.generated_image = tf.Variable(self.content_image, dtype=tf.float32)
        
        # Создание модели
        self.model = self.create_model()
        
        # Словари для хранения значений потерь
        self.loss_history = {
            'total': [],
            'content': [],
            'style': [],
            'tv': []
        }
        
    def load_and_preprocess(self, image_path):
        """
        Загрузка и предобработка изображения
        
        Args:
            image_path: путь к изображению
            
        Returns:
            предобработанное изображение
        """
        img = load_img(image_path, target_size=(self.img_height, self.img_width))
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = vgg19.preprocess_input(img)
        return tf.convert_to_tensor(img, dtype=tf.float32)
    
    def deprocess_image(self, img_tensor):
        """
        Обратное преобразование изображения для отображения
        
        Args:
            img_tensor: тензор изображения
            
        Returns:
            изображение для отображения
        """
        img = img_tensor.numpy().copy()
        img = img.reshape((self.img_height, self.img_width, 3))
        
        # Обратное преобразование предобработки VGG19
        img[:, :, 0] += 103.939
        img[:, :, 1] += 116.779
        img[:, :, 2] += 123.68
        img = img[:, :, ::-1]  # BGR -> RGB
        img = np.clip(img, 0, 255).astype('uint8')
        
        return img
    
    def create_model(self):
        """
        Создание модели для извлечения признаков
        
        Returns:
            модель Keras
        """
        # Загрузка предобученной модели VGG19
        vgg = vgg19.VGG19(weights='imagenet', include_top=False)
        vgg.trainable = False
        
        # Выбор слоев для контента и стиля
        content_layers = ['block5_conv2']
        style_layers = [
            'block1_conv1',
            'block2_conv1', 
            'block3_conv1',
            'block4_conv1',
            'block5_conv1'
        ]
        
        # Создание выходных слоев
        layer_outputs = [vgg.get_layer(layer).output for layer in content_layers + style_layers]
        
        model = Model(inputs=vgg.input, outputs=layer_outputs)
        model.trainable = False
        
        return model
    
    def gram_matrix(self, tensor):
        """
        Вычисление матрицы Грама для стилевых признаков
        
        Args:
            tensor: тензор признаков
            
        Returns:
            матрица Грама
        """
        channels = int(tensor.shape[-1])
        features = tf.reshape(tensor, [-1, channels])
        gram = tf.matmul(features, features, transpose_a=True)
        return gram / tf.cast(tf.shape(features)[0], tf.float32)
    
    def compute_loss(self, model, generated, content, style):
        """
        Вычисление общей потери
        
        Args:
            model: модель VGG
            generated: сгенерированное изображение
            content: контентное изображение
            style: стилевое изображение
            
        Returns:
            общая потеря
        """
        # Получение признаков
        gen_features = model(generated)
        content_features = model(content)
        style_features = model(style)
        
        # Контентная потеря
        content_loss = tf.reduce_mean(tf.square(
            gen_features[0] - content_features[0]
        ))
        
        # Стилевая потеря
        style_loss = 0
        for i in range(1, len(gen_features)):
            gen_gram = self.gram_matrix(gen_features[i])
            style_gram = self.gram_matrix(style_features[i])
            layer_style_loss = tf.reduce_mean(tf.square(gen_gram - style_gram))
            style_loss += layer_style_loss
        
        # Потеря гладкости (Total Variation Loss) - ИСПРАВЛЕННАЯ ВЕРСИЯ
        # Вычисляем разности между соседними пикселями
        diff_h = generated[:, 1:, :, :] - generated[:, :-1, :, :]  # [1, 399, 400, 3]
        diff_w = generated[:, :, 1:, :] - generated[:, :, :-1, :]  # [1, 400, 399, 3]
        
        # Вычисляем потерю как сумму квадратов разностей
        tv_loss = tf.reduce_mean(tf.square(diff_h)) + tf.reduce_mean(tf.square(diff_w))
        
        # Общая потеря
        total_loss = (self.content_weight * content_loss + 
                     self.style_weight * style_loss + 
                     self.total_variation_weight * tv_loss)
        
        return total_loss, content_loss, style_loss, tv_loss
    
    def train_step(self, model, optimizer):
        """
        Один шаг обучения
        
        Args:
            model: модель VGG
            optimizer: оптимизатор
            
        Returns:
            значения потерь
        """
        with tf.GradientTape() as tape:
            loss, content_loss, style_loss, tv_loss = self.compute_loss(
                model, 
                self.generated_image, 
                self.content_image, 
                self.style_image
            )
        
        grads = tape.gradient(loss, self.generated_image)
        optimizer.apply_gradients([(grads, self.generated_image)])
        
        # Клиппинг значений для стабильности
        self.generated_image.assign(tf.clip_by_value(self.generated_image, -128, 128))
        
        return loss, content_loss, style_loss, tv_loss
    
    def train(self, iterations=1000, learning_rate=2.0, display_interval=100):
        """
        Обучение модели переноса стиля
        
        Args:
            iterations: количество итераций
            learning_rate: скорость обучения
            display_interval: интервал отображения результатов
        """
        optimizer = tf.optimizers.Adam(learning_rate=learning_rate)
        
        start_time = time.time()
        
        for i in range(iterations):
            try:
                loss, content_loss, style_loss, tv_loss = self.train_step(self.model, optimizer)
                
                # Сохранение истории потерь
                self.loss_history['total'].append(loss.numpy())
                self.loss_history['content'].append(content_loss.numpy())
                self.loss_history['style'].append(style_loss.numpy())
                self.loss_history['tv'].append(tv_loss.numpy())
                
                # Отображение прогресса
                if i % display_interval == 0:
                    elapsed_time = time.time() - start_time
                    print(f"Итерация {i}/{iterations}")
                    print(f"  Total Loss: {loss.numpy():.4f}")
                    print(f"  Content Loss: {content_loss.numpy():.4f}")
                    print(f"  Style Loss: {style_loss.numpy():.4f}")
                    print(f"  TV Loss: {tv_loss.numpy():.4f}")
                    print(f"  Время: {elapsed_time:.2f} сек\n")
                    
                    # Сохранение промежуточного результата
                    self.save_result(f"result_iter_{i}.png")
                    
            except Exception as e:
                print(f"Ошибка на итерации {i}: {e}")
                continue
    
    def save_result(self, filename):
        """
        Сохранение текущего результата
        
        Args:
            filename: имя файла для сохранения
        """
        try:
            result_img = self.deprocess_image(self.generated_image)
            plt.figure(figsize=(10, 10))
            plt.imshow(result_img)
            plt.axis('off')
            plt.savefig(filename, bbox_inches='tight', pad_inches=0)
            plt.close()
        except Exception as e:
            print(f"Ошибка при сохранении {filename}: {e}")
    
    def plot_loss_history(self):
        """
        Визуализация истории потерь
        """
        if not self.loss_history['total']:
            print("Нет данных для визуализации")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        axes[0, 0].plot(self.loss_history['total'])
        axes[0, 0].set_title('Total Loss')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Loss')
        
        axes[0, 1].plot(self.loss_history['content'])
        axes[0, 1].set_title('Content Loss')
        axes[0, 1].set_xlabel('Iteration')
        axes[0, 1].set_ylabel('Loss')
        
        axes[1, 0].plot(self.loss_history['style'])
        axes[1, 0].set_title('Style Loss')
        axes[1, 0].set_xlabel('Iteration')
        axes[1, 0].set_ylabel('Loss')
        
        axes[1, 1].plot(self.loss_history['tv'])
        axes[1, 1].set_title('Total Variation Loss')
        axes[1, 1].set_xlabel('Iteration')
        axes[1, 1].set_ylabel('Loss')
        
        plt.tight_layout()
        plt.savefig('loss_history.png')
        plt.show()
    
    def display_results(self):
        """
        Отображение исходных и полученного изображений
        """
        try:
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Контентное изображение
            content_display = self.deprocess_image(self.content_image)
            axes[0].imshow(content_display)
            axes[0].set_title('Content Image')
            axes[0].axis('off')
            
            # Стилевое изображение
            style_display = self.deprocess_image(self.style_image)
            axes[1].imshow(style_display)
            axes[1].set_title('Style Image')
            axes[1].axis('off')
            
            # Сгенерированное изображение
            result_display = self.deprocess_image(self.generated_image)
            axes[2].imshow(result_display)
            axes[2].set_title('Generated Image')
            axes[2].axis('off')
            
            plt.tight_layout()
            plt.savefig('final_results.png')
            plt.show()
        except Exception as e:
            print(f"Ошибка при отображении результатов: {e}")

def main():
    """
    Основная функция для запуска переноса стиля
    """
    # Пути к изображениям
    content_path = "lab1_b.jpg"  # замените на путь к вашему изображению
    style_path = "lab1_f.jpg"      # замените на путь к вашему изображению стиля
    
    # Проверка существования файлов
    if not os.path.exists(content_path):
        print(f"Ошибка: файл {content_path} не найден")
        print("Создайте тестовые изображения или укажите правильные пути")
        return
    
    if not os.path.exists(style_path):
        print(f"Ошибка: файл {style_path} не найден")
        return
    
    try:
        # Создание и обучение модели
        nst = NeuralStyleTransfer(
            content_image_path=content_path,
            style_image_path=style_path,
            img_height=400,
            img_width=400,
            content_weight=1e-4,
            style_weight=1.0,
            total_variation_weight=1e-4
        )
        
        print("Начало обучения...")
        nst.train(iterations=500, learning_rate=2.0, display_interval=50)
        
        # Визуализация результатов
        print("\nВизуализация результатов...")
        nst.display_results()
        nst.plot_loss_history()
        
        # Сохранение финального результата
        nst.save_result("final_result.png")
        print("Обучение завершено! Результаты сохранены.")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print("Проверьте, что все необходимые библиотеки установлены:")
        print("pip install tensorflow keras numpy matplotlib pillow")

if __name__ == "__main__":
    main()