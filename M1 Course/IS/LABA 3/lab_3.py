# -*- coding: utf-8 -*-
"""
Лабораторная работа №4: Генеративно-состязательные сети (GAN)
Исправленная версия - все ошибки устранены
"""

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.datasets import mnist
import os

# Настройка GPU
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print("GPUs Available: ", gpus)
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except:
        pass

# Параметры
IMG_SIZE = 28
CHANNELS = 1
LATENT_DIM = 100
BATCH_SIZE = 64
EPOCHS = 80  # Уменьшим для теста


# =====================================================
# 1. DCGAN (Deep Convolutional GAN)
# =====================================================

def build_generator_dcgan():
    """Построение генератора DCGAN"""
    model = keras.Sequential([
        layers.Dense(7*7*256, use_bias=False, input_shape=(LATENT_DIM,)),
        layers.BatchNormalization(),
        layers.LeakyReLU(alpha=0.2),
        
        layers.Reshape((7, 7, 256)),
        
        layers.Conv2DTranspose(128, (5, 5), strides=(2, 2), padding='same', use_bias=False),
        layers.BatchNormalization(),
        layers.LeakyReLU(alpha=0.2),
        
        layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False),
        layers.BatchNormalization(),
        layers.LeakyReLU(alpha=0.2),
        
        layers.Conv2DTranspose(1, (5, 5), strides=(1, 1), padding='same', use_bias=False, activation='tanh')
    ])
    return model

def build_discriminator_dcgan():
    """Построение дискриминатора DCGAN"""
    model = keras.Sequential([
        layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same', input_shape=(IMG_SIZE, IMG_SIZE, CHANNELS)),
        layers.LeakyReLU(alpha=0.2),
        layers.Dropout(0.3),
        
        layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'),
        layers.LeakyReLU(alpha=0.2),
        layers.Dropout(0.3),
        
        layers.Conv2D(256, (5, 5), strides=(2, 2), padding='same'),
        layers.LeakyReLU(alpha=0.2),
        layers.Dropout(0.3),
        
        layers.Flatten(),
        layers.Dense(1, activation='sigmoid')
    ])
    return model

def train_dcgan(X_train, epochs=EPOCHS):
    """Обучение DCGAN"""
    print("\n" + "="*60)
    print("Обучение DCGAN")
    print("="*60)
    
    # Нормализация данных в диапазон [-1, 1]
    X_train = X_train.astype(np.float32)
    X_train = (X_train - 127.5) / 127.5
    X_train = np.expand_dims(X_train, axis=-1)
    
    generator = build_generator_dcgan()
    discriminator = build_discriminator_dcgan()
    
    # Компиляция дискриминатора
    discriminator.compile(loss='binary_crossentropy', 
                         optimizer=keras.optimizers.Adam(0.0002, 0.5), 
                         metrics=['accuracy'])
    
    # GAN модель
    discriminator.trainable = False
    gan_input = layers.Input(shape=(LATENT_DIM,))
    generated_image = generator(gan_input)
    gan_output = discriminator(generated_image)
    gan = keras.Model(gan_input, gan_output)
    gan.compile(loss='binary_crossentropy', 
               optimizer=keras.optimizers.Adam(0.0002, 0.5))
    
    # Обучение
    history = {'d_loss': [], 'g_loss': [], 'd_acc': []}
    
    for epoch in range(epochs):
        # Обучение дискриминатора
        idx = np.random.randint(0, X_train.shape[0], BATCH_SIZE)
        real_images = X_train[idx]
        
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        fake_images = generator.predict(noise, verbose=0)
        
        real_labels = np.ones((BATCH_SIZE, 1))
        fake_labels = np.zeros((BATCH_SIZE, 1))
        
        d_loss_real = discriminator.train_on_batch(real_images, real_labels)
        d_loss_fake = discriminator.train_on_batch(fake_images, fake_labels)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
        
        # Обучение генератора
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        misleading_labels = np.ones((BATCH_SIZE, 1))
        g_loss = gan.train_on_batch(noise, misleading_labels)
        
        history['d_loss'].append(d_loss[0])
        history['g_loss'].append(g_loss)
        history['d_acc'].append(d_loss[1] * 100)
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: D_loss={d_loss[0]:.4f}, G_loss={g_loss:.4f}, D_acc={d_loss[1]*100:.1f}%")
    
    return generator, discriminator, history


# =====================================================
# 2. CGAN (Conditional GAN)
# =====================================================

def build_generator_cgan():
    """Построение генератора CGAN с условными метками"""
    # Вход для шума
    noise_input = layers.Input(shape=(LATENT_DIM,), name='noise_input')
    # Вход для метки класса
    label_input = layers.Input(shape=(10,), name='label_input')
    
    # Объединение шума и метки
    merged = layers.Concatenate()([noise_input, label_input])
    
    x = layers.Dense(7*7*256, use_bias=False)(merged)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Reshape((7, 7, 256))(x)
    
    x = layers.Conv2DTranspose(128, (5, 5), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    
    x = layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    
    output = layers.Conv2DTranspose(1, (5, 5), strides=(1, 1), padding='same', use_bias=False, activation='tanh')(x)
    
    model = keras.Model([noise_input, label_input], output)
    return model

def build_discriminator_cgan():
    """Построение дискриминатора CGAN с условными метками"""
    img_input = layers.Input(shape=(IMG_SIZE, IMG_SIZE, CHANNELS), name='image_input')
    label_input = layers.Input(shape=(10,), name='label_input')
    
    # Преобразование метки в пространство изображения
    label_dense = layers.Dense(IMG_SIZE * IMG_SIZE)(label_input)
    label_reshaped = layers.Reshape((IMG_SIZE, IMG_SIZE, 1))(label_dense)
    
    # Объединение изображения и метки
    merged = layers.Concatenate()([img_input, label_reshaped])
    
    x = layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same')(merged)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same')(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Conv2D(256, (5, 5), strides=(2, 2), padding='same')(x)
    x = layers.LeakyReLU(alpha=0.2)(x)
    x = layers.Dropout(0.3)(x)
    
    x = layers.Flatten()(x)
    output = layers.Dense(1, activation='sigmoid')(x)
    
    model = keras.Model([img_input, label_input], output)
    return model

def train_cgan(X_train, y_train, epochs=EPOCHS):
    """Обучение CGAN"""
    print("\n" + "="*60)
    print("Обучение CGAN (Conditional GAN)")
    print("="*60)
    
    # Нормализация данных
    X_train = X_train.astype(np.float32)
    X_train = (X_train - 127.5) / 127.5
    X_train = np.expand_dims(X_train, axis=-1)
    
    # One-hot encoding меток
    y_train_onehot = keras.utils.to_categorical(y_train, 10)
    
    generator = build_generator_cgan()
    discriminator = build_discriminator_cgan()
    
    discriminator.compile(loss='binary_crossentropy', 
                         optimizer=keras.optimizers.Adam(0.0002, 0.5), 
                         metrics=['accuracy'])
    
    discriminator.trainable = False
    noise_input = layers.Input(shape=(LATENT_DIM,), name='gan_noise')
    label_input = layers.Input(shape=(10,), name='gan_label')
    generated_img = generator([noise_input, label_input])
    gan_output = discriminator([generated_img, label_input])
    gan = keras.Model([noise_input, label_input], gan_output)
    gan.compile(loss='binary_crossentropy', 
               optimizer=keras.optimizers.Adam(0.0002, 0.5))
    
    history = {'d_loss': [], 'g_loss': [], 'd_acc': []}
    
    for epoch in range(epochs):
        # Обучение дискриминатора
        idx = np.random.randint(0, X_train.shape[0], BATCH_SIZE)
        real_images = X_train[idx]
        real_labels = y_train_onehot[idx]
        
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        fake_labels = np.random.randint(0, 10, BATCH_SIZE)
        fake_labels_onehot = keras.utils.to_categorical(fake_labels, 10)
        fake_images = generator.predict([noise, fake_labels_onehot], verbose=0)
        
        real_labels_out = np.ones((BATCH_SIZE, 1))
        fake_labels_out = np.zeros((BATCH_SIZE, 1))
        
        d_loss_real = discriminator.train_on_batch([real_images, real_labels], real_labels_out)
        d_loss_fake = discriminator.train_on_batch([fake_images, fake_labels_onehot], fake_labels_out)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
        
        # Обучение генератора
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        random_labels = np.random.randint(0, 10, BATCH_SIZE)
        random_labels_onehot = keras.utils.to_categorical(random_labels, 10)
        misleading_labels = np.ones((BATCH_SIZE, 1))
        g_loss = gan.train_on_batch([noise, random_labels_onehot], misleading_labels)
        
        history['d_loss'].append(d_loss[0])
        history['g_loss'].append(g_loss)
        history['d_acc'].append(d_loss[1] * 100)
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: D_loss={d_loss[0]:.4f}, G_loss={g_loss:.4f}, D_acc={d_loss[1]*100:.1f}%")
            
            # Периодическая генерация изображений
            if epoch % 50 == 0:
                generate_conditional_images(generator, epoch)
    
    return generator, discriminator, history

def generate_conditional_images(generator, epoch):
    """Генерация изображений для всех 10 классов"""
    fig, axes = plt.subplots(2, 5, figsize=(12, 6))
    axes = axes.flatten()
    
    for digit in range(10):
        noise = np.random.normal(0, 1, (1, LATENT_DIM))
        label = keras.utils.to_categorical([digit], 10)
        img = generator.predict([noise, label], verbose=0)
        img = (img[0, :, :, 0] + 1) / 2.0
        axes[digit].imshow(img, cmap='gray')
        axes[digit].set_title(f'Digit: {digit}')
        axes[digit].axis('off')
    
    plt.suptitle(f'CGAN Generated Images - Epoch {epoch}')
    plt.tight_layout()
    plt.savefig(f'cgan_epoch_{epoch}.png', dpi=100)
    plt.close()


# =====================================================
# 3. WGAN (Wasserstein GAN)
# =====================================================

def build_generator_wgan():
    """Построение генератора WGAN"""
    model = keras.Sequential([
        layers.Dense(7*7*256, use_bias=False, input_shape=(LATENT_DIM,)),
        layers.BatchNormalization(),
        layers.LeakyReLU(alpha=0.2),
        layers.Reshape((7, 7, 256)),
        
        layers.Conv2DTranspose(128, (5, 5), strides=(2, 2), padding='same', use_bias=False),
        layers.BatchNormalization(),
        layers.LeakyReLU(alpha=0.2),
        
        layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False),
        layers.BatchNormalization(),
        layers.LeakyReLU(alpha=0.2),
        
        layers.Conv2DTranspose(1, (5, 5), strides=(1, 1), padding='same', use_bias=False, activation='tanh')
    ])
    return model

def build_critic_wgan():
    """Построение критика (дискриминатора) WGAN без сигмоида"""
    model = keras.Sequential([
        layers.Conv2D(64, (5, 5), strides=(2, 2), padding='same', input_shape=(IMG_SIZE, IMG_SIZE, CHANNELS)),
        layers.LeakyReLU(alpha=0.2),
        layers.Dropout(0.3),
        
        layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'),
        layers.LeakyReLU(alpha=0.2),
        layers.Dropout(0.3),
        
        layers.Conv2D(256, (5, 5), strides=(2, 2), padding='same'),
        layers.LeakyReLU(alpha=0.2),
        layers.Dropout(0.3),
        
        layers.Flatten(),
        layers.Dense(1)  # Нет сигмоида - линейный выход
    ])
    return model

def wasserstein_loss(y_true, y_pred):
    """Wasserstein loss function"""
    return tf.reduce_mean(y_true * y_pred)

def train_wgan(X_train, epochs=EPOCHS, n_critic=3, clip_value=0.01):
    """Обучение WGAN с отсечением весов"""
    print("\n" + "="*60)
    print("Обучение WGAN (Wasserstein GAN)")
    print("="*60)
    
    # Нормализация данных
    X_train = X_train.astype(np.float32)
    X_train = (X_train - 127.5) / 127.5
    X_train = np.expand_dims(X_train, axis=-1)
    
    generator = build_generator_wgan()
    critic = build_critic_wgan()
    
    # Компиляция критика с Wasserstein loss
    critic.compile(loss=wasserstein_loss, 
                  optimizer=keras.optimizers.RMSprop(learning_rate=0.00005))
    
    # GAN модель
    critic.trainable = False
    gan_input = layers.Input(shape=(LATENT_DIM,))
    generated_image = generator(gan_input)
    gan_output = critic(generated_image)
    wgan = keras.Model(gan_input, gan_output)
    wgan.compile(loss=wasserstein_loss, 
                optimizer=keras.optimizers.RMSprop(learning_rate=0.00005))
    
    history = {'c_loss': [], 'g_loss': []}
    
    for epoch in range(epochs):
        # Обучение критика (несколько итераций на эпоху)
        for _ in range(n_critic):
            idx = np.random.randint(0, X_train.shape[0], BATCH_SIZE)
            real_images = X_train[idx]
            
            noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
            fake_images = generator.predict(noise, verbose=0)
            
            # Критик: максимизирует разницу между реальными и фейковыми
            c_loss_real = critic.train_on_batch(real_images, -np.ones((BATCH_SIZE, 1)))
            c_loss_fake = critic.train_on_batch(fake_images, np.ones((BATCH_SIZE, 1)))
            c_loss = 0.5 * np.add(c_loss_real, c_loss_fake)
            
            # Отсечение весов для условия Липшица
            for layer in critic.layers:
                weights = layer.get_weights()
                if weights:
                    weights = [np.clip(w, -clip_value, clip_value) for w in weights]
                    layer.set_weights(weights)
        
        # Обучение генератора
        noise = np.random.normal(0, 1, (BATCH_SIZE, LATENT_DIM))
        g_loss = wgan.train_on_batch(noise, -np.ones((BATCH_SIZE, 1)))
        
        c_loss_val = c_loss[0] if isinstance(c_loss, (list, tuple)) else c_loss
        history['c_loss'].append(c_loss_val)
        history['g_loss'].append(g_loss)
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: Critic_loss={c_loss_val:.4f}, Generator_loss={g_loss:.4f}")
    
    return generator, critic, history


# =====================================================
# Вспомогательные функции
# =====================================================

def generate_and_save_images(generator, epoch, noise=None, prefix='dcgan'):
    """Генерация и сохранение изображений для DCGAN и WGAN"""
    if noise is None:
        noise = np.random.normal(0, 1, (16, LATENT_DIM))
    
    predictions = generator.predict(noise, verbose=0)
    
    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    axes = axes.flatten()
    
    for i in range(16):
        img = (predictions[i, :, :, 0] + 1) / 2.0
        axes[i].imshow(img, cmap='gray')
        axes[i].axis('off')
    
    plt.suptitle(f'{prefix.upper()} - Epoch {epoch}')
    plt.tight_layout()
    plt.savefig(f'{prefix}_epoch_{epoch}.png', dpi=100)
    plt.close()

def visualize_final_results_dcgan(generator, title, num_images=25, prefix='gan'):
    """Визуализация финальных результатов для DCGAN и WGAN"""
    noise = np.random.normal(0, 1, (num_images, LATENT_DIM))
    predictions = generator.predict(noise, verbose=0)
    
    cols = 5
    rows = num_images // cols
    fig, axes = plt.subplots(rows, cols, figsize=(10, 10))
    axes = axes.flatten()
    
    for i in range(num_images):
        img = (predictions[i, :, :, 0] + 1) / 2.0
        axes[i].imshow(img, cmap='gray')
        axes[i].axis('off')
    
    plt.suptitle(f'{title} - Final Generated Images')
    plt.tight_layout()
    plt.savefig(f'{prefix}_final_results.png', dpi=100)
    plt.show()

def visualize_final_results_cgan(generator, title, num_images=25, prefix='cgan'):
    """Визуализация финальных результатов для CGAN (с метками)"""
    cols = 5
    rows = num_images // cols
    fig, axes = plt.subplots(rows, cols, figsize=(10, 10))
    axes = axes.flatten()
    
    for i in range(num_images):
        noise = np.random.normal(0, 1, (1, LATENT_DIM))
        digit = i % 10  # Равномерное распределение по классам
        label = keras.utils.to_categorical([digit], 10)
        img = generator.predict([noise, label], verbose=0)
        img = (img[0, :, :, 0] + 1) / 2.0
        axes[i].imshow(img, cmap='gray')
        axes[i].set_title(f'Digit: {digit}', fontsize=8)
        axes[i].axis('off')
    
    plt.suptitle(f'{title} - Final Generated Images (Conditional)')
    plt.tight_layout()
    plt.savefig(f'{prefix}_final_results.png', dpi=100)
    plt.show()

def plot_training_history(history, title):
    """Построение графиков обучения"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    if 'd_loss' in history:
        axes[0].plot(history['d_loss'], label='Discriminator Loss')
        axes[0].plot(history['g_loss'], label='Generator Loss')
        axes[0].set_title(f'{title} - Losses')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        
        axes[1].plot(history['d_acc'], label='Discriminator Accuracy', color='green')
        axes[1].set_title(f'{title} - Accuracy')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Accuracy (%)')
        axes[1].legend()
    elif 'c_loss' in history:
        axes[0].plot(history['c_loss'], label='Critic Loss')
        axes[0].plot(history['g_loss'], label='Generator Loss')
        axes[0].set_title(f'{title} - Wasserstein Losses')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].legend()
        axes[1].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(f'{title.lower()}_history.png', dpi=100)
    plt.show()


# =====================================================
# Основной запуск
# =====================================================

def main():
    print("="*60)
    print("Лабораторная работа №4: Генеративно-состязательные сети (GAN)")
    print("="*60)
    
    # Загрузка данных MNIST
    (X_train, y_train), (X_test, y_test) = mnist.load_data()
    print(f"\nЗагружен датасет MNIST: {X_train.shape[0]} обучающих изображений")
    
    # Создание директории для результатов
    os.makedirs('results', exist_ok=True)
    os.chdir('results')
    
    # 1. DCGAN
    print("\n" + "="*40)
    print("Запуск 1. DCGAN (Deep Convolutional GAN)")
    print("="*40)
    gen_dcgan, disc_dcgan, hist_dcgan = train_dcgan(X_train, epochs=EPOCHS)
    plot_training_history(hist_dcgan, "DCGAN")
    visualize_final_results_dcgan(gen_dcgan, "DCGAN", prefix='dcgan')
    
    # 2. CGAN
    print("\n" + "="*40)
    print("Запуск 2. CGAN (Conditional GAN)")
    print("="*40)
    gen_cgan, disc_cgan, hist_cgan = train_cgan(X_train, y_train, epochs=EPOCHS)
    plot_training_history(hist_cgan, "CGAN")
    visualize_final_results_cgan(gen_cgan, "CGAN", prefix='cgan')
    
    # 3. WGAN
    print("\n" + "="*40)
    print("Запуск 3. WGAN (Wasserstein GAN)")
    print("="*40)
    gen_wgan, critic_wgan, hist_wgan = train_wgan(X_train, epochs=EPOCHS, n_critic=3)
    plot_training_history(hist_wgan, "WGAN")
    visualize_final_results_dcgan(gen_wgan, "WGAN", prefix='wgan')
    
    print("\n" + "="*60)
    print("Обучение всех моделей завершено!")
    print("Результаты сохранены в директории 'results'")
    print("="*60)
    
    # Сравнительная визуализация
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Генерация изображений для сравнения
    noise = np.random.normal(0, 1, (4, LATENT_DIM))
    
    # DCGAN
    imgs_dcgan = gen_dcgan.predict(noise, verbose=0)
    
    # CGAN
    labels_cgan = keras.utils.to_categorical(np.random.randint(0, 10, 4), 10)
    imgs_cgan = gen_cgan.predict([noise, labels_cgan], verbose=0)
    
    # WGAN
    imgs_wgan = gen_wgan.predict(noise, verbose=0)
    
    titles = ['DCGAN', 'CGAN', 'WGAN']
    imgs_list = [imgs_dcgan, imgs_cgan, imgs_wgan]
    
    for idx, (img_list, title) in enumerate(zip(imgs_list, titles)):
        ax = axes[idx]
        for i in range(4):
            img = (img_list[i, :, :, 0] + 1) / 2.0
            ax.imshow(img, cmap='gray')
            ax.set_title(title)
    
    plt.suptitle("Сравнение результатов разных GAN архитектур")
    plt.tight_layout()
    plt.savefig('comparison_all_gan.png', dpi=100)
    plt.show()

if __name__ == "__main__":
    main()