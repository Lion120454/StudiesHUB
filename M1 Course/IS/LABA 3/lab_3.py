# -*- coding: utf-8 -*-
"""
Лабораторная работа №4: GAN на датасете цветов (Flowers)
Обучает нейронную сеть генерировать изображения цветов
Поддерживает: DCGAN, CGAN, WGAN
"""

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os
from PIL import Image
import io
import tensorflow_datasets as tfds
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# Отключаем предупреждения
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Параметры по умолчанию для цветов
IMG_SIZE = 64  # 64×64 пикселя - оптимально для цветов
CHANNELS = 3   # RGB (цветные изображения)
LATENT_DIM = 100
BATCH_SIZE = 32
EPOCHS = 100

# Названия классов цветов из датасета
FLOWER_CLASSES = ["dandelion", "daisy", "tulips", "sunflowers", "roses"]
NUM_CLASSES = len(FLOWER_CLASSES)


class FlowersDataset:
    """Класс для загрузки и обработки датасета цветов"""
    
    def __init__(self, img_size=64):
        self.img_size = img_size
        self.images = None
        self.labels = None
        self.class_names = FLOWER_CLASSES
        
    def load_flowers_dataset(self, split='train'):
        """
        Загрузка датасета цветов из TensorFlow Datasets
        """
        print("\n" + "="*60)
        print("Загрузка датасета цветов (Flowers)")
        print("="*60)
        
        try:
            # Загрузка датасета
            dataset = tfds.load('tf_flowers', split=split, as_supervised=True, with_info=False)
            
            images_list = []
            labels_list = []
            
            print("Обработка изображений...")
            
            for image, label in tfds.as_numpy(dataset):
                # Изменение размера изображения
                img = tf.image.resize(image, (self.img_size, self.img_size))
                # Нормализация в диапазон [-1, 1]
                img = (img / 127.5) - 1
                images_list.append(img.numpy())
                labels_list.append(label)
            
            self.images = np.array(images_list)
            self.labels = np.array(labels_list)
            
            print(f"Успешно загружено {len(self.images)} изображений")
            print(f"Размер изображений: {self.img_size}×{self.img_size}")
            print(f"Классы: {self.class_names}")
            print(f"Распределение по классам:")
            for i, name in enumerate(self.class_names):
                count = np.sum(self.labels == i)
                print(f"  {name}: {count} изображений ({count/len(self.labels)*100:.1f}%)")
            
            return self.images, self.labels
            
        except Exception as e:
            print(f"Ошибка загрузки датасета: {e}")
            print("\nАльтернативная загрузка через URL...")
            return self._load_from_url()
    
    def _load_from_url(self):
        """
        Альтернативная загрузка датасета через URL (если tfds не работает)
        """
        import urllib.request
        import tarfile
        
        url = "http://download.tensorflow.org/example_images/flower_photos.tgz"
        print(f"Загрузка из {url}...")
        
        # Скачивание архива
        urllib.request.urlretrieve(url, "flower_photos.tgz")
        
        # Распаковка
        print("Распаковка архива...")
        with tarfile.open("flower_photos.tgz", "r:gz") as tar:
            tar.extractall()
        
        # Загрузка изображений из папок
        images_list = []
        labels_list = []
        
        for label_idx, class_name in enumerate(self.class_names):
            class_dir = f"flower_photos/{class_name}"
            if os.path.exists(class_dir):
                for img_file in os.listdir(class_dir):
                    if img_file.endswith('.jpg'):
                        img_path = os.path.join(class_dir, img_file)
                        try:
                            img = Image.open(img_path)
                            img = img.convert('RGB')
                            img = img.resize((self.img_size, self.img_size), Image.Resampling.LANCZOS)
                            img_array = np.array(img, dtype=np.float32)
                            img_array = (img_array / 127.5) - 1
                            images_list.append(img_array)
                            labels_list.append(label_idx)
                        except Exception as e:
                            print(f"Ошибка загрузки {img_path}: {e}")
        
        self.images = np.array(images_list)
        self.labels = np.array(labels_list)
        
        print(f"Загружено {len(self.images)} изображений из папок")
        return self.images, self.labels
    
    def preview_images(self, num_images=16):
        """
        Предпросмотр загруженных изображений
        """
        if self.images is None:
            print("Нет загруженных изображений")
            return
        
        num_images = min(num_images, len(self.images))
        fig, axes = plt.subplots(4, 4, figsize=(12, 12))
        axes = axes.flatten()
        
        for i in range(num_images):
            img = (self.images[i] + 1) / 2.0  # Денормализация
            axes[i].imshow(img)
            axes[i].set_title(f"{self.class_names[self.labels[i]]}", fontsize=8)
            axes[i].axis('off')
        
        plt.suptitle("Датасет цветов - примеры изображений")
        plt.tight_layout()
        plt.show()
    
    def get_class_images(self, class_name):
        """
        Получение изображений определенного класса
        """
        if class_name in self.class_names:
            class_idx = self.class_names.index(class_name)
            mask = self.labels == class_idx
            return self.images[mask], self.labels[mask]
        else:
            print(f"Класс {class_name} не найден. Доступны: {self.class_names}")
            return None, None


class DCGAN:
    """DCGAN модель для цветных изображений"""
    
    def __init__(self, img_size=64, channels=3, latent_dim=100):
        self.img_size = img_size
        self.channels = channels
        self.latent_dim = latent_dim
        self.generator = None
        self.discriminator = None
        self.gan = None
        self.history = {'d_loss': [], 'g_loss': [], 'd_acc': []}
        
    def build_generator(self):
        """Построение генератора для цветных изображений"""
        model = keras.Sequential([
            layers.Dense(8*8*256, use_bias=False, input_shape=(self.latent_dim,)),
            layers.BatchNormalization(),
            layers.LeakyReLU(alpha=0.2),
            layers.Reshape((8, 8, 256)),
            
            layers.Conv2DTranspose(128, (5, 5), strides=(2, 2), padding='same', use_bias=False),
            layers.BatchNormalization(),
            layers.LeakyReLU(alpha=0.2),
            
            layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False),
            layers.BatchNormalization(),
            layers.LeakyReLU(alpha=0.2),
            
            layers.Conv2DTranspose(32, (5, 5), strides=(2, 2), padding='same', use_bias=False),
            layers.BatchNormalization(),
            layers.LeakyReLU(alpha=0.2),
            
            layers.Conv2DTranspose(self.channels, (5, 5), strides=(1, 1), padding='same', 
                                  use_bias=False, activation='tanh')
        ])
        return model
    
    def build_discriminator(self):
        """Построение дискриминатора для цветных изображений"""
        model = keras.Sequential([
            layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same', 
                         input_shape=(self.img_size, self.img_size, self.channels)),
            layers.LeakyReLU(alpha=0.2),
            layers.Dropout(0.3),
            
            layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'),
            layers.LeakyReLU(alpha=0.2),
            layers.Dropout(0.3),
            
            layers.Conv2D(256, (5, 5), strides=(2, 2), padding='same'),
            layers.LeakyReLU(alpha=0.2),
            layers.Dropout(0.3),
            
            layers.Conv2D(512, (5, 5), strides=(2, 2), padding='same'),
            layers.LeakyReLU(alpha=0.2),
            layers.Dropout(0.3),
            
            layers.Flatten(),
            layers.Dense(1, activation='sigmoid')
        ])
        return model
    
    def compile(self):
        """Компиляция модели"""
        self.generator = self.build_generator()
        self.discriminator = self.build_discriminator()
        
        self.discriminator.compile(loss='binary_crossentropy',
                                   optimizer=keras.optimizers.Adam(0.0002, 0.5),
                                   metrics=['accuracy'])
        
        self.discriminator.trainable = False
        gan_input = layers.Input(shape=(self.latent_dim,))
        generated_image = self.generator(gan_input)
        gan_output = self.discriminator(generated_image)
        self.gan = keras.Model(gan_input, gan_output)
        self.gan.compile(loss='binary_crossentropy',
                        optimizer=keras.optimizers.Adam(0.0002, 0.5))
    
    def train(self, X_train, epochs, batch_size, callback=None):
        """Обучение модели"""
        print("\n" + "="*60)
        print("Обучение DCGAN на датасете цветов")
        print("="*60)
        print(f"Количество изображений: {X_train.shape[0]}")
        print(f"Размер изображений: {X_train.shape[1]}×{X_train.shape[2]}")
        
        for epoch in range(epochs):
            # Обучение дискриминатора
            idx = np.random.randint(0, X_train.shape[0], batch_size)
            real_images = X_train[idx]
            
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            fake_images = self.generator.predict(noise, verbose=0)
            
            real_labels = np.ones((batch_size, 1))
            fake_labels = np.zeros((batch_size, 1))
            
            d_loss_real = self.discriminator.train_on_batch(real_images, real_labels)
            d_loss_fake = self.discriminator.train_on_batch(fake_images, fake_labels)
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
            
            # Обучение генератора
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            misleading_labels = np.ones((batch_size, 1))
            g_loss = self.gan.train_on_batch(noise, misleading_labels)
            
            self.history['d_loss'].append(d_loss[0])
            self.history['g_loss'].append(g_loss)
            self.history['d_acc'].append(d_loss[1] * 100)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch:4d}: D_loss={d_loss[0]:.4f}, G_loss={g_loss:.4f}, D_acc={d_loss[1]*100:.1f}%")
                if callback:
                    callback(self, epoch)
        
        return self.history
    
    def generate_images(self, num_images=16):
        """Генерация изображений цветов"""
        noise = np.random.normal(0, 1, (num_images, self.latent_dim))
        predictions = self.generator.predict(noise, verbose=0)
        predictions = (predictions + 1) / 2.0
        return predictions
    
    def save_model(self, path):
        """Сохранение модели"""
        if not os.path.exists(path):
            os.makedirs(path)
        self.generator.save(os.path.join(path, 'dcgan_generator_flowers.h5'))
        self.discriminator.save(os.path.join(path, 'dcgan_discriminator_flowers.h5'))
        print(f"Модели сохранены в {path}")
    
    def load_model(self, path):
        """Загрузка модели"""
        self.generator = keras.models.load_model(os.path.join(path, 'dcgan_generator_flowers.h5'))
        self.discriminator = keras.models.load_model(os.path.join(path, 'dcgan_discriminator_flowers.h5'))
        self.compile()
        print(f"Модели загружены из {path}")


class CGAN:
    """Conditional GAN для генерации цветов определенного класса"""
    
    def __init__(self, img_size=64, channels=3, latent_dim=100, num_classes=5):
        self.img_size = img_size
        self.channels = channels
        self.latent_dim = latent_dim
        self.num_classes = num_classes
        self.generator = None
        self.discriminator = None
        self.gan = None
        self.history = {'d_loss': [], 'g_loss': [], 'd_acc': []}
    
    def build_generator(self):
        """Построение генератора CGAN"""
        noise_input = layers.Input(shape=(self.latent_dim,), name='noise')
        label_input = layers.Input(shape=(self.num_classes,), name='label')
        
        merged = layers.Concatenate()([noise_input, label_input])
        
        x = layers.Dense(8*8*256, use_bias=False)(merged)
        x = layers.BatchNormalization()(x)
        x = layers.LeakyReLU(alpha=0.2)(x)
        x = layers.Reshape((8, 8, 256))(x)
        
        x = layers.Conv2DTranspose(128, (5, 5), strides=(2, 2), padding='same', use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.LeakyReLU(alpha=0.2)(x)
        
        x = layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.LeakyReLU(alpha=0.2)(x)
        
        x = layers.Conv2DTranspose(32, (5, 5), strides=(2, 2), padding='same', use_bias=False)(x)
        x = layers.BatchNormalization()(x)
        x = layers.LeakyReLU(alpha=0.2)(x)
        
        output = layers.Conv2DTranspose(self.channels, (5, 5), strides=(1, 1), 
                                       padding='same', activation='tanh')(x)
        
        return keras.Model([noise_input, label_input], output)
    
    def build_discriminator(self):
        """Построение дискриминатора CGAN"""
        img_input = layers.Input(shape=(self.img_size, self.img_size, self.channels), name='image')
        label_input = layers.Input(shape=(self.num_classes,), name='label')
        
        # Преобразуем метку в карту признаков
        label_dense = layers.Dense(self.img_size * self.img_size)(label_input)
        label_reshaped = layers.Reshape((self.img_size, self.img_size, 1))(label_dense)
        label_tiled = layers.Concatenate()([label_reshaped] * self.channels)
        
        merged = layers.Concatenate()([img_input, label_tiled])
        
        x = layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same')(merged)
        x = layers.LeakyReLU(alpha=0.2)(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same')(x)
        x = layers.LeakyReLU(alpha=0.2)(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Conv2D(256, (5, 5), strides=(2, 2), padding='same')(x)
        x = layers.LeakyReLU(alpha=0.2)(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Conv2D(512, (5, 5), strides=(2, 2), padding='same')(x)
        x = layers.LeakyReLU(alpha=0.2)(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Flatten()(x)
        output = layers.Dense(1, activation='sigmoid')(x)
        
        return keras.Model([img_input, label_input], output)
    
    def compile(self):
        """Компиляция модели"""
        self.generator = self.build_generator()
        self.discriminator = self.build_discriminator()
        
        self.discriminator.compile(loss='binary_crossentropy',
                                   optimizer=keras.optimizers.Adam(0.0002, 0.5),
                                   metrics=['accuracy'])
        
        self.discriminator.trainable = False
        noise_input = layers.Input(shape=(self.latent_dim,))
        label_input = layers.Input(shape=(self.num_classes,))
        generated_img = self.generator([noise_input, label_input])
        gan_output = self.discriminator([generated_img, label_input])
        self.gan = keras.Model([noise_input, label_input], gan_output)
        self.gan.compile(loss='binary_crossentropy',
                        optimizer=keras.optimizers.Adam(0.0002, 0.5))
    
    def train(self, X_train, y_train, epochs, batch_size, callback=None):
        """Обучение модели с метками классов"""
        print("\n" + "="*60)
        print("Обучение CGAN на датасете цветов")
        print("=" * 60)        
        # One-hot encoding меток
        y_onehot = keras.utils.to_categorical(y_train, self.num_classes)
        
        for epoch in range(epochs):
            idx = np.random.randint(0, X_train.shape[0], batch_size)
            real_images = X_train[idx]
            real_labels = y_onehot[idx]
            
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            fake_labels = keras.utils.to_categorical(
                np.random.randint(0, self.num_classes, batch_size), 
                self.num_classes
            )
            fake_images = self.generator.predict([noise, fake_labels], verbose=0)
            
            d_loss_real = self.discriminator.train_on_batch([real_images, real_labels], 
                                                            np.ones((batch_size, 1)))
            d_loss_fake = self.discriminator.train_on_batch([fake_images, fake_labels], 
                                                            np.zeros((batch_size, 1)))
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
            
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            random_labels = keras.utils.to_categorical(
                np.random.randint(0, self.num_classes, batch_size), 
                self.num_classes
            )
            g_loss = self.gan.train_on_batch([noise, random_labels], np.ones((batch_size, 1)))
            
            self.history['d_loss'].append(d_loss[0])
            self.history['g_loss'].append(g_loss)
            self.history['d_acc'].append(d_loss[1] * 100)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch:4d}: D_loss={d_loss[0]:.4f}, G_loss={g_loss:.4f}, D_acc={d_loss[1]*100:.1f}%")
                if callback:
                    callback(self, epoch)
        
        return self.history
    
    def generate_images(self, class_id=None, num_images=16):
        """Генерация изображений цветов определенного класса"""
        if class_id is None:
            class_id = np.random.randint(0, self.num_classes)
        
        noise = np.random.normal(0, 1, (num_images, self.latent_dim))
        labels = keras.utils.to_categorical([class_id] * num_images, self.num_classes)
        predictions = self.generator.predict([noise, labels], verbose=0)
        predictions = (predictions + 1) / 2.0
        return predictions, class_id
    
    def save_model(self, path):
        """Сохранение модели"""
        if not os.path.exists(path):
            os.makedirs(path)
        self.generator.save(os.path.join(path, 'cgan_generator_flowers.h5'))
        self.discriminator.save(os.path.join(path, 'cgan_discriminator_flowers.h5'))
        print(f"Модели сохранены в {path}")


class FlowersGANApp:
    """Приложение для обучения GAN на датасете цветов"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GAN Trainer - Генерация цветов (Flowers Dataset)")
        self.root.geometry("900x700")
        
        self.dataset = None
        self.current_model = None
        self.model_type = None
        self.training_thread = None
        self.is_training = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title = ttk.Label(main_frame, text="GAN - Генерация изображений цветов", 
                         font=('Arial', 18, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(main_frame, text="Датасет: Flower Photos (5 классов: ромашки, тюльпаны, розы, подсолнухи, одуванчики)",
                 font=('Arial', 10)).grid(row=1, column=0, columnspan=2, pady=5)
        
        # Раздел загрузки датасета
        load_frame = ttk.LabelFrame(main_frame, text="1. Загрузка датасета цветов", padding="10")
        load_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(load_frame, text="Загрузить датасет Flowers", 
                  command=self.load_dataset).grid(row=0, column=0, padx=5)
        ttk.Button(load_frame, text="Предпросмотр изображений", 
                  command=self.preview_dataset).grid(row=0, column=1, padx=5)
        
        self.dataset_label = ttk.Label(load_frame, text="Датасет не загружен")
        self.dataset_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Раздел выбора модели
        model_frame = ttk.LabelFrame(main_frame, text="2. Выбор модели GAN", padding="10")
        model_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.model_var = tk.StringVar(value="DCGAN")
        ttk.Radiobutton(model_frame, text="DCGAN (стандартная)", 
                       variable=self.model_var, value="DCGAN").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(model_frame, text="CGAN (условная - выбор класса цветка)", 
                       variable=self.model_var, value="CGAN").grid(row=0, column=1, padx=10)
        
        # Раздел параметров
        params_frame = ttk.LabelFrame(main_frame, text="3. Параметры обучения", padding="10")
        params_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(params_frame, text="Размер изображения:").grid(row=0, column=0, padx=5)
        self.img_size_var = tk.StringVar(value="64")
        ttk.Combobox(params_frame, textvariable=self.img_size_var, 
                    values=["64", "128"], width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(params_frame, text="Эпохи:").grid(row=0, column=2, padx=5)
        self.epochs_var = tk.StringVar(value="100")
        ttk.Entry(params_frame, textvariable=self.epochs_var, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(params_frame, text="Размер батча:").grid(row=0, column=4, padx=5)
        self.batch_var = tk.StringVar(value="32")
        ttk.Entry(params_frame, textvariable=self.batch_var, width=10).grid(row=0, column=5, padx=5)
        
        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        self.train_btn = ttk.Button(control_frame, text="Начать обучение", 
                                    command=self.start_training)
        self.train_btn.grid(row=0, column=0, padx=10)
        
        self.generate_btn = ttk.Button(control_frame, text="Генерировать цветы", 
                                       command=self.generate_flowers, state='disabled')
        self.generate_btn.grid(row=0, column=1, padx=10)
        
        self.save_btn = ttk.Button(control_frame, text="Сохранить модель", 
                                   command=self.save_model, state='disabled')
        self.save_btn.grid(row=0, column=2, padx=10)
        
        # Прогресс
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог обучения", padding="10")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def load_dataset(self):
        """Загрузка датасета цветов"""
        try:
            img_size = int(self.img_size_var.get())
            self.dataset = FlowersDataset(img_size)
            
            self.log_message("Загрузка датасета цветов...")
            images, labels = self.dataset.load_flowers_dataset()
            
            self.dataset_label.config(text=f"Загружено {len(images)} изображений цветов | "
                                          f"Классы: {', '.join(self.dataset.class_names)}")
            self.log_message(f"Датасет загружен: {len(images)} изображений")
            self.log_message(f"Размер изображений: {img_size}×{img_size}")
            
        except Exception as e:
            self.log_message(f"Ошибка загрузки: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
    
    def preview_dataset(self):
        """Предпросмотр датасета"""
        if self.dataset and self.dataset.images is not None:
            self.dataset.preview_images()
        else:
            messagebox.showwarning("Предупреждение", "Сначала загрузите датасет")
    
    def update_progress(self, model, epoch):
        """Обновление прогресса обучения"""
        self.log_message(f"Эпоха {epoch}: D_loss={model.history['d_loss'][-1]:.4f}, "
                        f"G_loss={model.history['g_loss'][-1]:.4f}")
        
        # Показываем промежуточные результаты
        if epoch % 25 == 0 and epoch > 0:
            self.show_generated_preview(model, epoch)
    
    def show_generated_preview(self, model, epoch):
        """Показ сгенерированных цветов в процессе обучения"""
        if self.model_type == "CGAN":
            images, class_id = model.generate_images(class_id=0, num_images=16)
            title = f"CGAN - Сгенерированные цветы (класс: {FLOWER_CLASSES[class_id]}) - Эпоха {epoch}"
        else:
            images = model.generate_images(16)
            title = f"DCGAN - Сгенерированные цветы - Эпоха {epoch}"
        
        fig, axes = plt.subplots(4, 4, figsize=(10, 10))
        axes = axes.flatten()
        for i in range(16):
            axes[i].imshow(images[i])
            axes[i].axis('off')
        plt.suptitle(title)
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(1)
        plt.close()
    
    def start_training(self):
        """Запуск обучения"""
        if self.dataset is None or self.dataset.images is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите датасет цветов")
            return
        
        if self.is_training:
            messagebox.showwarning("Предупреждение", "Обучение уже выполняется")
            return
        
        self.train_btn.config(state='disabled')
        self.generate_btn.config(state='disabled')
        self.progress.start()
        self.is_training = True
        
        self.training_thread = threading.Thread(target=self.train_model)
        self.training_thread.start()
    
    def train_model(self):
        """Обучение модели"""
        try:
            X_train = self.dataset.images
            epochs = int(self.epochs_var.get())
            batch_size = int(self.batch_var.get())
            model_type = self.model_var.get()
            
            self.log_message(f"\n{'='*50}")
            self.log_message(f"Начало обучения {model_type}")
            self.log_message(f"Параметры: эпохи={epochs}, батч={batch_size}")
            self.log_message(f"Изображений в датасете: {X_train.shape[0]}")
            self.log_message(f"{'='*50}")
            
            if model_type == "DCGAN":
                self.current_model = DCGAN(IMG_SIZE, CHANNELS, LATENT_DIM)
                self.current_model.compile()
                self.current_model.train(X_train, epochs, batch_size, self.update_progress)
                self.model_type = "DCGAN"
                
            elif model_type == "CGAN":
                self.current_model = CGAN(IMG_SIZE, CHANNELS, LATENT_DIM, NUM_CLASSES)
                self.current_model.compile()
                self.current_model.train(X_train, self.dataset.labels, epochs, batch_size, self.update_progress)
                self.model_type = "CGAN"
            
            self.log_message("\n✅ Обучение завершено успешно!")
            self.progress.stop()
            self.generate_btn.config(state='normal')
            self.save_btn.config(state='normal')
            self.train_btn.config(state='normal')
            self.is_training = False
            
            # Показываем финальные результаты
            self.show_final_results()
            
        except Exception as e:
            self.log_message(f"❌ Ошибка: {str(e)}")
            self.progress.stop()
            self.train_btn.config(state='normal')
            self.is_training = False
            messagebox.showerror("Ошибка обучения", str(e))
    
    def show_final_results(self):
        """Показ финальных результатов"""
        if self.model_type == "CGAN":
            # Генерируем цветы для каждого класса
            fig, axes = plt.subplots(2, 5, figsize=(15, 6))
            for class_id in range(NUM_CLASSES):
                images, _ = self.current_model.generate_images(class_id=class_id, num_images=5)
                for i in range(min(5, len(images))):
                    axes[i, class_id].imshow(images[i])
                    axes[i, class_id].axis('off')
                    if i == 0:
                        axes[i, class_id].set_title(FLOWER_CLASSES[class_id], fontsize=10)
            plt.suptitle("CGAN - Сгенерированные цветы по классам")
            plt.tight_layout()
            plt.show()
        else:
            images = self.current_model.generate_images(25)
            fig, axes = plt.subplots(5, 5, figsize=(12, 12))
            axes = axes.flatten()
            for i in range(25):
                axes[i].imshow(images[i])
                axes[i].axis('off')
            plt.suptitle("DCGAN - Сгенерированные изображения цветов")
            plt.tight_layout()
            plt.show()
    
    def generate_flowers(self):
        """Генерация цветов обученной моделью"""
        if self.current_model is None:
            messagebox.showwarning("Предупреждение", "Сначала обучите модель")
            return
        
        gen_window = tk.Toplevel(self.root)
        gen_window.title("Генерация цветов")
        gen_window.geometry("400x300")
        
        ttk.Label(gen_window, text="Количество цветов:").pack(pady=10)
        num_var = tk.StringVar(value="16")
        ttk.Entry(gen_window, textvariable=num_var, width=10).pack()
        
        if self.model_type == "CGAN":
            ttk.Label(gen_window, text="Тип цветка:").pack(pady=10)
            class_var = tk.StringVar(value="roses")
            class_combo = ttk.Combobox(gen_window, textvariable=class_var, 
                                       values=FLOWER_CLASSES, width=15)
            class_combo.pack()
        
        def generate():
            num = int(num_var.get())
            if self.model_type == "CGAN":
                class_name = class_var.get()
                class_id = FLOWER_CLASSES.index(class_name)
                images, _ = self.current_model.generate_images(class_id=class_id, num_images=num)
                title = f"CGAN - {class_name}"
            else:
                images = self.current_model.generate_images(num)
                title = "DCGAN - Сгенерированные цветы"
            
            cols = min(5, num)
            rows = (num + cols - 1) // cols
            fig, axes = plt.subplots(rows, cols, figsize=(cols*3, rows*3))
            if rows == 1 and cols == 1:
                axes = [axes]
            else:
                axes = axes.flatten()
            
            for i in range(num):
                axes[i].imshow(images[i])
                axes[i].axis('off')
            for i in range(num, len(axes)):
                axes[i].axis('off')
            
            plt.suptitle(title)
            plt.tight_layout()
            plt.show()
            gen_window.destroy()
        
        ttk.Button(gen_window, text="Сгенерировать", command=generate).pack(pady=20)
    
    def save_model(self):
        """Сохранение модели"""
        if self.current_model is None:
            return
        
        save_dir = filedialog.askdirectory(title="Выберите папку для сохранения модели")
        if save_dir:
            self.current_model.save_model(save_dir)
            self.log_message(f"Модель сохранена в {save_dir}")
    
    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    """Основная функция"""
    print("="*60)
    print("GAN для генерации цветов (Flowers Dataset)")
    print("="*60)
    print("\nДатасет содержит 5 классов цветов:")
    for i, name in enumerate(FLOWER_CLASSES, 1):
        print(f"  {i}. {name}")
    print("\nЗапуск графического интерфейса...")
    
    app = FlowersGANApp()
    app.run()


if __name__ == "__main__":
    main()