import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.datasets import fashion_mnist
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

tf.get_logger().setLevel('ERROR')
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ------------------------------
# 1. Класс VAE с регулируемым beta
# ------------------------------
class VAE(Model):
    def __init__(self, encoder, decoder, beta=1.0, **kwargs):
        super(VAE, self).__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.beta = beta
        self.total_loss_tracker = keras.metrics.Mean(name="total_loss")
        self.reconstruction_loss_tracker = keras.metrics.Mean(name="reconstruction_loss")
        self.kl_loss_tracker = keras.metrics.Mean(name="kl_loss")

    @property
    def metrics(self):
        return [self.total_loss_tracker, self.reconstruction_loss_tracker, self.kl_loss_tracker]

    def train_step(self, data):
        with tf.GradientTape() as tape:
            z_mean, z_log_var, z = self.encoder(data)
            reconstruction = self.decoder(z)
            
            # Приводим к одинаковой размерности
            if len(reconstruction.shape) == 4 and reconstruction.shape[1] != data.shape[1]:
                reconstruction = tf.image.resize(reconstruction, (data.shape[1], data.shape[2]))
            
            # Вычисляем потери
            reconstruction_loss = tf.reduce_mean(
                tf.reduce_sum(keras.losses.binary_crossentropy(data, reconstruction), axis=[1, 2])
            )
            kl_loss = -0.5 * tf.reduce_mean(
                1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
            )
            total_loss = reconstruction_loss + self.beta * kl_loss

        grads = tape.gradient(total_loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))

        self.total_loss_tracker.update_state(total_loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        
        # Возвращаем словарь с loss
        return {
            "loss": self.total_loss_tracker.result(),
            "reconstruction_loss": self.reconstruction_loss_tracker.result(),
            "kl_loss": self.kl_loss_tracker.result(),
        }

    def test_step(self, data):
        # Добавляем test_step для валидации
        z_mean, z_log_var, z = self.encoder(data)
        reconstruction = self.decoder(z)
        
        if len(reconstruction.shape) == 4 and reconstruction.shape[1] != data.shape[1]:
            reconstruction = tf.image.resize(reconstruction, (data.shape[1], data.shape[2]))
        
        reconstruction_loss = tf.reduce_mean(
            tf.reduce_sum(keras.losses.binary_crossentropy(data, reconstruction), axis=[1, 2])
        )
        kl_loss = -0.5 * tf.reduce_mean(
            1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
        )
        total_loss = reconstruction_loss + self.beta * kl_loss
        
        self.total_loss_tracker.update_state(total_loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)
        
        return {
            "loss": self.total_loss_tracker.result(),
            "reconstruction_loss": self.reconstruction_loss_tracker.result(),
            "kl_loss": self.kl_loss_tracker.result(),
        }

    def call(self, inputs):
        z_mean, z_log_var, z = self.encoder(inputs)
        reconstruction = self.decoder(z)
        if len(reconstruction.shape) == 4 and reconstruction.shape[1] != inputs.shape[1]:
            reconstruction = tf.image.resize(reconstruction, (inputs.shape[1], inputs.shape[2]))
        return reconstruction

# ------------------------------
# 2. Функция построения энкодера и декодера
# ------------------------------
def build_vae_models(input_shape=(28, 28, 1), latent_dim=2,
                     encoder_filters=[32, 64], encoder_activations=['relu', 'relu'],
                     decoder_filters=[64, 32], decoder_activations=['relu', 'relu'],
                     output_activation='sigmoid'):
    
    # Энкодер
    encoder_input = keras.Input(shape=input_shape, name="encoder_input")
    x = encoder_input
    
    # Проходим сверточные слои
    for i, (filters, activation) in enumerate(zip(encoder_filters, encoder_activations)):
        if activation == 'leaky_relu':
            x = layers.Conv2D(filters, kernel_size=3, strides=2, padding='same')(x)
            x = layers.LeakyReLU(negative_slope=0.3)(x)
        else:
            x = layers.Conv2D(filters, kernel_size=3, strides=2, padding='same', activation=activation)(x)
    
    # Сохраняем форму после энкодера
    conv_shape = x.shape[1:]
    height, width, channels = conv_shape[0], conv_shape[1], conv_shape[2]
    flatten_dim = height * width * channels
    
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation='relu')(x)
    z_mean = layers.Dense(latent_dim, name="z_mean")(x)
    z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)

    # Репараметризация
    def sampling(args):
        z_mean, z_log_var = args
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

    z = layers.Lambda(sampling, name="z")([z_mean, z_log_var])
    encoder = Model(encoder_input, [z_mean, z_log_var, z], name="encoder")

    # Декодер
    decoder_input = keras.Input(shape=(latent_dim,), name="decoder_input")
    
    # Dense слой
    x = layers.Dense(flatten_dim, activation='relu')(decoder_input)
    
    # Reshape
    x = layers.Reshape((height, width, channels))(x)
    
    # Транспонированные свертки
    for i, (filters, activation) in enumerate(zip(decoder_filters, decoder_activations)):
        if activation == 'leaky_relu':
            x = layers.Conv2DTranspose(filters, kernel_size=3, strides=2, padding='same')(x)
            x = layers.LeakyReLU(negative_slope=0.3)(x)
        elif activation == 'tanh':
            x = layers.Conv2DTranspose(filters, kernel_size=3, strides=2, padding='same', activation=activation)(x)
        else:
            x = layers.Conv2DTranspose(filters, kernel_size=3, strides=2, padding='same', activation=activation)(x)
    
    # Финальный слой для восстановления исходной размерности
    decoder_output = layers.Conv2DTranspose(1, kernel_size=3, strides=2, padding='same', activation=output_activation)(x)
    decoder = Model(decoder_input, decoder_output, name="decoder")

    return encoder, decoder

# ------------------------------
# 3. Функция обучения и оценки
# ------------------------------
def train_and_evaluate(config_name, encoder, decoder, beta, epochs=15, batch_size=128):
    print(f"\n{'='*60}\nЗапуск: {config_name} (beta={beta})\n{'='*60}")
    
    # Загружаем данные
    (x_train, _), (x_test, _) = fashion_mnist.load_data()
    x_train = x_train.astype('float32') / 255.
    x_test = x_test.astype('float32') / 255.
    x_train = np.expand_dims(x_train, -1)
    x_test = np.expand_dims(x_test, -1)
    
    # Берем подвыборку для ускорения
    x_train = x_train[:5000]
    x_test = x_test[:1000]

    vae = VAE(encoder, decoder, beta=beta)
    # Не указываем loss в compile(), так как он определен в train_step
    vae.compile(optimizer=keras.optimizers.Adam(learning_rate=1e-3))
    
    try:
        history = vae.fit(x_train, epochs=epochs, batch_size=batch_size, 
                         validation_data=(x_test, None), verbose=1)
    except Exception as e:
        print(f"Ошибка при обучении: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

    # Анализ скрытых векторов
    z_mean, z_log_var, _ = encoder.predict(x_test, verbose=0)
    mean_z = np.mean(z_mean, axis=0)
    var_z = np.var(z_mean, axis=0)
    print(f"Среднее скрытых векторов: {mean_z}")
    print(f"Дисперсия скрытых векторов: {var_z}")

    # Визуализация
    try:
        n = 8
        figure = np.zeros((28 * n, 28 * n))
        grid_x = norm.ppf(np.linspace(0.05, 0.95, n))
        grid_y = norm.ppf(np.linspace(0.05, 0.95, n))
        for i, yi in enumerate(grid_x):
            for j, xi in enumerate(grid_y):
                z_sample = np.array([[xi, yi]])
                x_decoded = decoder.predict(z_sample, verbose=0)
                if x_decoded.shape[1] > 28:
                    x_decoded = tf.image.resize(x_decoded, (28, 28)).numpy()
                digit = x_decoded[0].reshape(28, 28)
                figure[i * 28: (i + 1) * 28, j * 28: (j + 1) * 28] = digit
        
        plt.figure(figsize=(10, 10))
        plt.imshow(figure, cmap='Greys_r')
        plt.title(f"{config_name} | beta={beta}")
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"Ошибка при визуализации: {e}")

    return history, mean_z, var_z

# ------------------------------
# 4. Исследование с разными параметрами
# ------------------------------
configs = [
    {
        "name": "Simple network, relu, beta=1.0",
        "encoder_filters": [16, 32],
        "encoder_activations": ['relu', 'relu'],
        "decoder_filters": [32, 16],
        "decoder_activations": ['relu', 'relu'],
        "beta": 1.0
    },
    {
        "name": "Deeper network, leaky_relu, beta=1.0", 
        "encoder_filters": [32, 64],
        "encoder_activations": ['leaky_relu', 'leaky_relu'],
        "decoder_filters": [64, 32],
        "decoder_activations": ['leaky_relu', 'leaky_relu'],
        "beta": 1.0
    },
    {
        "name": "Wide network, beta=0.5",
        "encoder_filters": [32, 64],
        "encoder_activations": ['relu', 'relu'],
        "decoder_filters": [64, 32],
        "decoder_activations": ['relu', 'relu'],
        "beta": 0.5
    }
]

results = []
for cfg in configs:
    try:
        print(f"\nПостроение модели: {cfg['name']}")
        enc, dec = build_vae_models(
            input_shape=(28, 28, 1),
            latent_dim=2,
            encoder_filters=cfg["encoder_filters"],
            encoder_activations=cfg["encoder_activations"],
            decoder_filters=cfg["decoder_filters"],
            decoder_activations=cfg["decoder_activations"],
            output_activation='sigmoid'
        )
        
        hist, mean_z, var_z = train_and_evaluate(
            config_name=cfg["name"],
            encoder=enc,
            decoder=dec,
            beta=cfg["beta"],
            epochs=8
        )
        
        if hist:
            results.append({
                "config": cfg["name"],
                "beta": cfg["beta"],
                "mean_z_0": mean_z[0],
                "mean_z_1": mean_z[1],
                "var_z_0": var_z[0],
                "var_z_1": var_z[1],
                "final_reconstruction_loss": hist.history['reconstruction_loss'][-1],
                "final_kl_loss": hist.history['kl_loss'][-1]
            })
            print(f"✓ {cfg['name']} завершена успешно")
        else:
            print(f"✗ {cfg['name']} не удалась")
    except Exception as e:
        print(f"Ошибка в конфигурации {cfg['name']}: {e}")

# ------------------------------
# 5. Влияние beta (только если есть успешные результаты)
# ------------------------------
if results:
    print("\n" + "="*60)
    print("Исследование влияния коэффициента beta")
    print("="*60)

    betas = [0.3, 0.5, 1.0, 2.0, 3.0]
    beta_results = []

    # Создаем простую базовую модель
    try:
        enc_base, dec_base = build_vae_models(
            input_shape=(28, 28, 1),
            encoder_filters=[16, 32],
            encoder_activations=['relu', 'relu'],
            decoder_filters=[32, 16],
            decoder_activations=['relu', 'relu']
        )
        
        for beta in betas:
            print(f"\n--- beta = {beta} ---")
            hist, mean_z, var_z = train_and_evaluate(
                config_name=f"Base model, beta={beta}",
                encoder=enc_base,
                decoder=dec_base,
                beta=beta,
                epochs=6
            )
            if hist and mean_z is not None:
                beta_results.append({
                    "beta": beta,
                    "mean_z_norm": np.linalg.norm(mean_z),
                    "var_z_mean": np.mean(var_z),
                    "kl_loss": hist.history['kl_loss'][-1],
                    "reconstruction_loss": hist.history['reconstruction_loss'][-1]
                })
                print(f"✓ Beta={beta} завершена")
            else:
                print(f"✗ Beta={beta} не удалась")
    except Exception as e:
        print(f"Ошибка при исследовании beta: {e}")

# ------------------------------
# 6. Вывод результатов
# ------------------------------
print("\n" + "="*60)
print("Сводные результаты по трём архитектурам")
print("="*60)
if results:
    df_results = pd.DataFrame(results)
    print(df_results[['config', 'beta', 'final_reconstruction_loss', 'final_kl_loss']])
    print("\nСредние и дисперсии скрытых векторов:")
    for r in results:
        print(f"{r['config']}: mean=({r['mean_z_0']:.3f}, {r['mean_z_1']:.3f}), var=({r['var_z_0']:.3f}, {r['var_z_1']:.3f})")
        
    # Визуализация сравнения
    plt.figure(figsize=(14, 5))
    plt.subplot(1, 2, 1)
    x_pos = np.arange(len(results))
    bars1 = plt.bar(x_pos, [r['final_reconstruction_loss'] for r in results])
    plt.xticks(x_pos, [r['config'][:15] for r in results], rotation=45)
    plt.title('Reconstruction Loss (меньше = лучше)')
    plt.ylabel('Loss')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    bars2 = plt.bar(x_pos, [r['final_kl_loss'] for r in results], color='orange')
    plt.xticks(x_pos, [r['config'][:15] for r in results], rotation=45)
    plt.title('KL Loss (регуляризация)')
    plt.ylabel('Loss')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
else:
    print("Нет успешных результатов для отображения")

if beta_results:
    print("\n" + "="*60)
    print("Влияние beta на скрытое пространство")
    print("="*60)
    df_beta = pd.DataFrame(beta_results)
    print(df_beta.round(4))
    
    # Графики
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # График 1: Норма среднего
    axes[0, 0].plot(df_beta['beta'], df_beta['mean_z_norm'], marker='o', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('beta')
    axes[0, 0].set_ylabel('||mean_z||')
    axes[0, 0].set_title('Норма среднего скрытых векторов vs beta')
    axes[0, 0].grid(True, alpha=0.3)
    
    # График 2: Дисперсия
    axes[0, 1].plot(df_beta['beta'], df_beta['var_z_mean'], marker='s', color='orange', linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('beta')
    axes[0, 1].set_ylabel('Средняя дисперсия')
    axes[0, 1].set_title('Дисперсия скрытых векторов vs beta')
    axes[0, 1].grid(True, alpha=0.3)
    
    # График 3: KL Loss
    axes[1, 0].plot(df_beta['beta'], df_beta['kl_loss'], marker='^', color='green', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('beta')
    axes[1, 0].set_ylabel('KL Loss')
    axes[1, 0].set_title('KL Loss vs beta')
    axes[1, 0].grid(True, alpha=0.3)
    
    # График 4: Reconstruction Loss
    axes[1, 1].plot(df_beta['beta'], df_beta['reconstruction_loss'], marker='D', color='red', linewidth=2, markersize=8)
    axes[1, 1].set_xlabel('beta')
    axes[1, 1].set_ylabel('Reconstruction Loss')
    axes[1, 1].set_title('Reconstruction Loss vs beta')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Анализ результатов
    print("\n" + "="*60)
    print("АНАЛИЗ РЕЗУЛЬТАТОВ")
    print("="*60)
    print("\n1. Влияние beta на скрытое пространство:")
    print(f"   - При beta={beta_results[0]['beta']}: норма среднего = {beta_results[0]['mean_z_norm']:.3f}, дисперсия = {beta_results[0]['var_z_mean']:.3f}")
    print(f"   - При beta={beta_results[-1]['beta']}: норма среднего = {beta_results[-1]['mean_z_norm']:.3f}, дисперсия = {beta_results[-1]['var_z_mean']:.3f}")
    print(f"   → С ростом beta среднее стремится к 0, дисперсия уменьшается")
    
    print("\n2. Компромисс реконструкция vs регуляризация:")
    print(f"   - Малая beta ({beta_results[0]['beta']}): KL Loss={beta_results[0]['kl_loss']:.3f}, Rec Loss={beta_results[0]['reconstruction_loss']:.3f}")
    print(f"   - Большая beta ({beta_results[-1]['beta']}): KL Loss={beta_results[-1]['kl_loss']:.3f}, Rec Loss={beta_results[-1]['reconstruction_loss']:.3f}")
    print(f"   → Увеличение beta усиливает регуляризацию, но ухудшает реконструкцию")
    
    # Находим оптимальный beta по комбинированной метрике
    optimal_beta = min(beta_results, key=lambda x: x['reconstruction_loss'] + 0.5*x['kl_loss'])
    print(f"\n3. Оптимальный beta (баланс Rec Loss + 0.5*KL Loss): {optimal_beta['beta']}")
    

else:
    print("Нет результатов по исследованию beta")

print("\n" + "="*60)
print("Исследование завершено!")
print("="*60)