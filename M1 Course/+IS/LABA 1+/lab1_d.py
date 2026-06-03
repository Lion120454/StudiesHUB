#Реализовать с использованием библиотеки keras нейронную сеть для решения задачи регрессии (Задание г)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, confusion_matrix, classification_report
from tensorflow import keras
from tensorflow.keras import layers, models, regularizers, callbacks
import warnings
warnings.filterwarnings('ignore')

# Установка seed для воспроизводимости результатов
np.random.seed(42)
keras.utils.set_random_seed(42)

print("="*70)
print("НЕЙРОННАЯ СЕТЬ ДЛЯ ПРЕДСКАЗАНИЯ ВЕРОЯТНОСТИ СНЕГА")
print("="*70)

# ============================================
# 1. ГЕНЕРАЦИЯ МЕТЕОРОЛОГИЧЕСКИХ ДАННЫХ
# ============================================
print("\n1. ГЕНЕРАЦИЯ МЕТЕОРОЛОГИЧЕСКИХ ДАННЫХ")
print("-"*50)

# Количество образцов
n_samples = 5000

# Генерация метеорологических параметров
np.random.seed(42)

# Температура воздуха (°C) - от -20 до +15
temperature = np.random.uniform(-20, 15, n_samples)

# Влажность воздуха (%) - от 30 до 100
humidity = np.random.uniform(30, 100, n_samples)

# Атмосферное давление (гПа) - от 980 до 1040
pressure = np.random.uniform(980, 1040, n_samples)

# Скорость ветра (м/с) - от 0 до 25
wind_speed = np.random.uniform(0, 25, n_samples)

# Высота облачности (м) - от 0 до 3000
cloud_ceiling = np.random.uniform(0, 3000, n_samples)

# Месяц (1-12) - сезонность
month = np.random.randint(1, 13, n_samples)

# Время суток (0-23) - температура может меняться
hour = np.random.randint(0, 24, n_samples)

# Создаем DataFrame
data = pd.DataFrame({
    'temperature': temperature,
    'humidity': humidity,
    'pressure': pressure,
    'wind_speed': wind_speed,
    'cloud_ceiling': cloud_ceiling,
    'month': month,
    'hour': hour
})

# Добавляем дополнительные признаки
data['is_winter'] = data['month'].isin([12, 1, 2]).astype(int)
data['is_night'] = ((data['hour'] < 6) | (data['hour'] > 20)).astype(int)
data['temp_below_zero'] = (data['temperature'] < 0).astype(int)

# ============================================
# 2. РАСЧЕТ ВЕРОЯТНОСТИ СНЕГА (ЦЕЛЕВАЯ ПЕРЕМЕННАЯ)
# ============================================
print("\n2. РАСЧЕТ ВЕРОЯТНОСТИ СНЕГА")
print("-"*50)

# Сложная нелинейная зависимость для вероятности снега
def calculate_snow_probability(temp, humidity, pressure, wind, cloud, month, hour):
    """
    Расчет вероятности снега на основе метеорологических параметров
    """
    # Базовые условия для снега
    temp_factor = np.exp(-((temp + 5) ** 2) / 100)  # Оптимум около -5°C
    temp_factor[temp > 2] = 0  # Выше 2°C снег маловероятен
    temp_factor[temp < -15] = temp_factor[temp < -15] * 0.5  # Слишком холодно - мало снега
    
    # Влажность должна быть высокой
    humidity_factor = np.where(humidity > 80, (humidity - 80) / 20, 0)
    humidity_factor = np.clip(humidity_factor, 0, 1)
    
    # Давление обычно низкое перед осадками
    pressure_factor = np.exp(-((pressure - 1000) ** 2) / 400)
    pressure_factor = 1 - pressure_factor * 0.5
    
    # Сезонный фактор (зимой выше)
    seasonal_factor = np.zeros_like(month)
    seasonal_factor[(month >= 11) | (month <= 3)] = 0.8
    seasonal_factor[(month >= 4) & (month <= 10)] = 0.2
    
    # Время суток (ночью чаще)
    time_factor = np.where((hour < 6) | (hour > 20), 0.7, 0.3)
    
    # Облачность
    cloud_factor = np.clip(cloud / 2000, 0, 1)
    
    # Скорость ветра (умеренный ветер способствует осадкам)
    wind_factor = np.exp(-((wind - 5) ** 2) / 50)
    
    # Комбинируем все факторы
    probability = (temp_factor * 0.35 + 
                  humidity_factor * 0.25 + 
                  pressure_factor * 0.10 + 
                  seasonal_factor * 0.15 +
                  time_factor * 0.05 +
                  cloud_factor * 0.05 +
                  wind_factor * 0.05)
    
    # Добавляем случайный шум
    noise = np.random.normal(0, 0.05, len(probability))
    probability = np.clip(probability + noise, 0, 1)
    
    return probability

# Рассчитываем вероятность снега
snow_probability = calculate_snow_probability(
    data['temperature'].values,
    data['humidity'].values,
    data['pressure'].values,
    data['wind_speed'].values,
    data['cloud_ceiling'].values,
    data['month'].values,
    data['hour'].values
)

data['snow_probability'] = snow_probability

# Добавляем бинарную метку (снег есть/нет) для дополнительного анализа
data['snow_label'] = (data['snow_probability'] > 0.5).astype(int)

print(f"Сгенерировано {n_samples} метеорологических наблюдений")
print(f"\nСтатистика вероятности снега:")
print(f"  Средняя вероятность: {data['snow_probability'].mean():.3f}")
print(f"  Медиана: {data['snow_probability'].median():.3f}")
print(f"  Минимум: {data['snow_probability'].min():.3f}")
print(f"  Максимум: {data['snow_probability'].max():.3f}")
print(f"  Стандартное отклонение: {data['snow_probability'].std():.3f}")

print(f"\nРаспределение классов (порог 0.5):")
snow_count = data['snow_label'].sum()
no_snow_count = len(data) - snow_count
print(f"  Снег: {snow_count} ({snow_count/len(data)*100:.1f}%)")
print(f"  Без снега: {no_snow_count} ({no_snow_count/len(data)*100:.1f}%)")

# ============================================
# 3. ПОДГОТОВКА ДАННЫХ
# ============================================
print("\n3. ПОДГОТОВКА ДАННЫХ")
print("-"*50)

# Выбираем признаки для модели
feature_columns = ['temperature', 'humidity', 'pressure', 'wind_speed', 
                   'cloud_ceiling', 'month', 'hour', 'is_winter', 
                   'is_night', 'temp_below_zero']

X = data[feature_columns].values
y = data['snow_probability'].values

# Разделение на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=data['snow_label']
)

# Нормализация данных
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

print(f"Признаки: {feature_columns}")
print(f"Обучающая выборка: {X_train_scaled.shape[0]} образцов")
print(f"Тестовая выборка: {X_test_scaled.shape[0]} образцов")

# ============================================
# 4. СОЗДАНИЕ МОДЕЛИ НЕЙРОННОЙ СЕТИ
# ============================================
print("\n4. СОЗДАНИЕ МОДЕЛИ НЕЙРОННОЙ СЕТИ")
print("-"*50)

def create_snow_prediction_model(input_dim):
    """
    Создание архитектуры нейронной сети для предсказания вероятности снега
    """
    model = models.Sequential([
        # Входной слой
        layers.Input(shape=(input_dim,)),
        
        # Первый скрытый слой
        layers.Dense(256, 
                    activation='relu',
                    kernel_regularizer=regularizers.l2(0.001),
                    name='dense_1'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Второй скрытый слой
        layers.Dense(128, 
                    activation='relu',
                    kernel_regularizer=regularizers.l2(0.001),
                    name='dense_2'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Третий скрытый слой
        layers.Dense(64, 
                    activation='relu',
                    kernel_regularizer=regularizers.l2(0.001),
                    name='dense_3'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        
        # Четвертый скрытый слой
        layers.Dense(32, 
                    activation='relu',
                    kernel_regularizer=regularizers.l2(0.001),
                    name='dense_4'),
        layers.BatchNormalization(),
        
        # Выходной слой (сигмоид для вероятности)
        layers.Dense(1, activation='sigmoid', name='output')
    ])
    return model

# Создание модели
model = create_snow_prediction_model(X_train_scaled.shape[1])

# Компиляция модели (используем binary_crossentropy для вероятности)
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',  # Для вероятностного выхода
    metrics=['mae', 'mse', 'accuracy']
)

# Вывод архитектуры модели
print("\nАрхитектура модели:")
model.summary()

# Подсчет параметров (исправленная версия)
total_params = model.count_params()
trainable_params = sum([np.prod(v.shape) for v in model.trainable_weights])  # Исправлено: v.shape вместо v.get_shape().as_list()
non_trainable_params = sum([np.prod(v.shape) for v in model.non_trainable_weights])  # Исправлено: v.shape

print(f"\nВсего параметров: {total_params:,}")
print(f"Обучаемых параметров: {trainable_params:,} ({trainable_params * 4 / 1024:.2f} KB)")
print(f"Необучаемых параметров: {non_trainable_params:,} ({non_trainable_params * 4 / 1024:.2f} KB)")

# ============================================
# 5. ОБУЧЕНИЕ МОДЕЛИ
# ============================================
print("\n5. ОБУЧЕНИЕ МОДЕЛИ")
print("-"*50)

# Настройка колбэков
early_stopping = callbacks.EarlyStopping(
    monitor='val_loss',
    patience=40,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=20,
    min_lr=0.00001,
    verbose=1
)

# Обучение модели
print("\nНачало обучения...")
history = model.fit(
    X_train_scaled, y_train_scaled,
    validation_split=0.2,
    epochs=150,
    batch_size=64,
    callbacks=[early_stopping, reduce_lr],
    verbose=1
)

# ============================================
# 6. ОЦЕНКА МОДЕЛИ
# ============================================
print("\n6. ОЦЕНКА МОДЕЛИ")
print("-"*50)

# Предсказание на тестовых данных (в нормализованном виде)
y_pred_scaled = model.predict(X_test_scaled, verbose=0)

# Обратное масштабирование
y_pred = scaler_y.inverse_transform(y_pred_scaled).flatten()
y_test_original = y_test

# Вычисление метрик
mse = mean_squared_error(y_test_original, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test_original, y_pred)
r2 = r2_score(y_test_original, y_pred)

print("\nРезультаты на тестовой выборке:")
print(f"  MSE (Среднеквадратичная ошибка):  {mse:.4f}")
print(f"  RMSE (Корень из MSE):            {rmse:.4f}")
print(f"  MAE (Средняя абсолютная ошибка):  {mae:.4f}")
print(f"  R² (Коэффициент детерминации):    {r2:.4f}")

# Оценка бинарной классификации (снег/без снега)
y_pred_binary = (y_pred > 0.5).astype(int)
y_test_binary = (y_test_original > 0.5).astype(int)

print("\nБинарная классификация (порог 0.5):")
print(classification_report(y_test_binary, y_pred_binary, 
                           target_names=['Без снега', 'Снег'],
                           digits=4))

# Матрица ошибок
cm = confusion_matrix(y_test_binary, y_pred_binary)
print("\nМатрица ошибок:")
print(f"                    Предсказано")
print(f"                  Без снега   Снег")
print(f"Фактически Без снега    {cm[0,0]:>6}    {cm[0,1]:>6}")
print(f"          Снег          {cm[1,0]:>6}    {cm[1,1]:>6}")

# Точность
accuracy = (cm[0,0] + cm[1,1]) / np.sum(cm)
print(f"\nТочность классификации: {accuracy:.4f}")

# ============================================
# 7. АНАЛИЗ ВАЖНОСТИ ПРИЗНАКОВ
# ============================================
print("\n7. АНАЛИЗ ВАЖНОСТИ ПРИЗНАКОВ")
print("-"*50)

# Получаем веса первого слоя
first_layer_weights = model.layers[0].get_weights()[0]
feature_importance = np.abs(first_layer_weights).mean(axis=1)

# Сортируем признаки по важности
importance_df = pd.DataFrame({
    'Признак': feature_columns,
    'Важность': feature_importance
}).sort_values('Важность', ascending=False)

print("\nВажность признаков для предсказания снега:")
print(importance_df.to_string(index=False))

# ============================================
# 8. ДЕМОНСТРАЦИЯ РАБОТЫ НА НОВЫХ ДАННЫХ
# ============================================
print("\n8. ДЕМОНСТРАЦИЯ РАБОТЫ НА НОВЫХ ДАННЫХ")
print("-"*50)

# Создаем различные сценарии погоды
test_scenarios = [
    {
        'name': '❄️ Сильный снегопад',
        'features': {
            'temperature': -5, 'humidity': 95, 'pressure': 990,
            'wind_speed': 3, 'cloud_ceiling': 500, 'month': 1,
            'hour': 2, 'is_winter': 1, 'is_night': 1, 'temp_below_zero': 1
        }
    },
    {
        'name': '🌨️ Легкий снег',
        'features': {
            'temperature': -2, 'humidity': 85, 'pressure': 1005,
            'wind_speed': 2, 'cloud_ceiling': 800, 'month': 12,
            'hour': 10, 'is_winter': 1, 'is_night': 0, 'temp_below_zero': 1
        }
    },
    {
        'name': '☀️ Ясная морозная погода',
        'features': {
            'temperature': -10, 'humidity': 60, 'pressure': 1030,
            'wind_speed': 1, 'cloud_ceiling': 3000, 'month': 1,
            'hour': 14, 'is_winter': 1, 'is_night': 0, 'temp_below_zero': 1
        }
    },
    {
        'name': '🌧️ Дождливая погода',
        'features': {
            'temperature': 5, 'humidity': 90, 'pressure': 995,
            'wind_speed': 5, 'cloud_ceiling': 400, 'month': 4,
            'hour': 15, 'is_winter': 0, 'is_night': 0, 'temp_below_zero': 0
        }
    },
    {
        'name': '🌫️ Туман',
        'features': {
            'temperature': 0, 'humidity': 100, 'pressure': 1015,
            'wind_speed': 0, 'cloud_ceiling': 100, 'month': 11,
            'hour': 6, 'is_winter': 0, 'is_night': 0, 'temp_below_zero': 0
        }
    },
    {
        'name': '🌡️ Оттепель',
        'features': {
            'temperature': 2, 'humidity': 88, 'pressure': 1010,
            'wind_speed': 8, 'cloud_ceiling': 600, 'month': 2,
            'hour': 13, 'is_winter': 1, 'is_night': 0, 'temp_below_zero': 0
        }
    }
]

# Преобразуем сценарии в массив признаков
scenario_features = []
scenario_names = []

for scenario in test_scenarios:
    features = [scenario['features'][col] for col in feature_columns]
    scenario_features.append(features)
    scenario_names.append(scenario['name'])

scenario_features = np.array(scenario_features)

# Нормализуем и предсказываем
scenario_features_scaled = scaler_X.transform(scenario_features)
predictions_scaled = model.predict(scenario_features_scaled, verbose=0)
predictions = scaler_y.inverse_transform(predictions_scaled).flatten()

print("\nПредсказания для различных погодных сценариев:")
print("-"*70)
print(f"{'Сценарий':<25} {'Вероятность снега':<20} {'Прогноз':<15}")
print("-"*70)

for name, prob in zip(scenario_names, predictions):
    if prob >= 0.7:
        forecast = "❄️ Ожидается снегопад"
        icon = "❄️"
    elif prob >= 0.4:
        forecast = "🌨️ Возможен снег"
        icon = "🌨️"
    elif prob >= 0.2:
        forecast = "🌧️ Маловероятен снег"
        icon = "🌧️"
    else:
        forecast = "☀️ Снег не ожидается"
        icon = "☀️"
    
    print(f"{name:<25} {prob*100:>6.1f}%{'':<12} {forecast}")

# ============================================
# 9. ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ
# ============================================
print("\n9. ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ")
print("-"*50)

# Проверяем, что matplotlib может отображать графики
try:
    # Создаем фигуру с подграфиками
    fig = plt.figure(figsize=(18, 12))
    fig.suptitle('Анализ модели предсказания вероятности снега', fontsize=16, fontweight='bold')
    
    # 1. График обучения
    ax1 = plt.subplot(3, 3, 1)
    ax1.plot(history.history['loss'], label='Обучающая', linewidth=2)
    ax1.plot(history.history['val_loss'], label='Валидационная', linewidth=2)
    ax1.set_title('Динамика ошибки (Loss)', fontweight='bold')
    ax1.set_xlabel('Эпоха')
    ax1.set_ylabel('Binary Crossentropy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # 2. График MAE
    ax2 = plt.subplot(3, 3, 2)
    ax2.plot(history.history['mae'], label='Обучающая', linewidth=2)
    ax2.plot(history.history['val_mae'], label='Валидационная', linewidth=2)
    ax2.set_title('Средняя абсолютная ошибка (MAE)', fontweight='bold')
    ax2.set_xlabel('Эпоха')
    ax2.set_ylabel('MAE')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. График точности
    ax3 = plt.subplot(3, 3, 3)
    ax3.plot(history.history['accuracy'], label='Обучающая', linewidth=2)
    ax3.plot(history.history['val_accuracy'], label='Валидационная', linewidth=2)
    ax3.set_title('Точность классификации', fontweight='bold')
    ax3.set_xlabel('Эпоха')
    ax3.set_ylabel('Accuracy')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Предсказания vs Реальные значения
    ax4 = plt.subplot(3, 3, 4)
    ax4.scatter(y_test_original, y_pred, alpha=0.4, s=10, c='blue')
    ax4.plot([0, 1], [0, 1], 'r--', linewidth=2, label='Идеальное предсказание')
    ax4.set_title('Предсказанные vs Реальные вероятности', fontweight='bold')
    ax4.set_xlabel('Реальная вероятность снега')
    ax4.set_ylabel('Предсказанная вероятность снега')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Матрица ошибок
    ax5 = plt.subplot(3, 3, 5)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax5, 
                xticklabels=['Без снега', 'Снег'],
                yticklabels=['Без снега', 'Снег'])
    ax5.set_title('Матрица ошибок', fontweight='bold')
    ax5.set_xlabel('Предсказано')
    ax5.set_ylabel('Фактически')
    
    # 6. Важность признаков
    ax6 = plt.subplot(3, 3, 6)
    importance_df_plot = importance_df.head(8)
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(importance_df_plot)))
    bars = ax6.barh(importance_df_plot['Признак'], importance_df_plot['Важность'], color=colors)
    ax6.set_title('Важность признаков', fontweight='bold')
    ax6.set_xlabel('Средняя важность')
    ax6.invert_yaxis()
    ax6.grid(True, alpha=0.3, axis='x')
    
    # 7. Распределение ошибок
    ax7 = plt.subplot(3, 3, 7)
    errors = y_test_original - y_pred
    ax7.hist(errors, bins=50, edgecolor='black', alpha=0.7, color='green')
    ax7.axvline(x=0, color='red', linestyle='--', linewidth=2)
    ax7.set_title('Распределение ошибок', fontweight='bold')
    ax7.set_xlabel('Ошибка предсказания')
    ax7.set_ylabel('Частота')
    ax7.grid(True, alpha=0.3)
    
    # 8. Вероятности для сценариев
    ax8 = plt.subplot(3, 3, 8)
    colors = plt.cm.RdYlGn_r(predictions)
    bars = ax8.bar(range(len(scenario_names)), predictions, color=colors)
    ax8.set_title('Вероятность снега для различных сценариев', fontweight='bold')
    ax8.set_xlabel('Сценарий')
    ax8.set_ylabel('Вероятность снега')
    ax8.set_xticks(range(len(scenario_names)))
    ax8.set_xticklabels([name[:15] for name in scenario_names], rotation=45, ha='right')
    ax8.axhline(y=0.5, color='red', linestyle='--', linewidth=1, label='Порог снега')
    ax8.legend()
    ax8.grid(True, alpha=0.3, axis='y')
    
    # 9. Зависимость от температуры
    ax9 = plt.subplot(3, 3, 9)
    temp_range = np.linspace(-15, 5, 100)
    humidity_fixed = 90
    pressure_fixed = 1000
    predictions_temp = []
    
    for temp in temp_range:
        test_data = np.array([[temp, humidity_fixed, pressure_fixed, 3, 500, 1, 12, 1, 0, 1 if temp < 0 else 0]])
        test_data_scaled = scaler_X.transform(test_data)
        pred_scaled = model.predict(test_data_scaled, verbose=0)
        pred = scaler_y.inverse_transform(pred_scaled)[0, 0]
        predictions_temp.append(pred)
    
    ax9.plot(temp_range, predictions_temp, 'b-', linewidth=2)
    ax9.set_title('Зависимость вероятности снега от температуры', fontweight='bold')
    ax9.set_xlabel('Температура (°C)')
    ax9.set_ylabel('Вероятность снега')
    ax9.grid(True, alpha=0.3)
    ax9.axvline(x=0, color='red', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.show()
    
except Exception as e:
    print(f"При создании графиков возникла ошибка: {e}")
    print("Продолжаем выполнение программы без графиков...")

# ============================================
# 10. СОХРАНЕНИЕ МОДЕЛИ
# ============================================
print("\n10. СОХРАНЕНИЕ МОДЕЛИ")
print("-"*50)

# Сохраняем модель
model.save('snow_prediction_model.h5')
print("Модель сохранена как 'snow_prediction_model.h5'")

# Сохраняем scaler'ы
import pickle
with open('snow_scaler_X.pkl', 'wb') as f:
    pickle.dump(scaler_X, f)
with open('snow_scaler_y.pkl', 'wb') as f:
    pickle.dump(scaler_y, f)
print("Scaler'ы сохранены как 'snow_scaler_X.pkl' и 'snow_scaler_y.pkl'")

# Сохраняем важность признаков
importance_df.to_csv('feature_importance.csv', index=False)
print("Важность признаков сохранена в 'feature_importance.csv'")

# ============================================
# 11. ИТОГОВЫЙ ОТЧЕТ
# ============================================
print("\n" + "="*70)
print("ИТОГОВЫЙ ОТЧЕТ ПО МОДЕЛИ ПРЕДСКАЗАНИЯ СНЕГА")
print("="*70)

print(f"\n📊 Качество модели:")
print(f"  • R² = {r2:.4f} - доля объясненной дисперсии")
print(f"  • MAE = {mae:.4f} - средняя ошибка в предсказании вероятности")
print(f"  • Точность классификации = {accuracy:.4f} ({accuracy*100:.1f}%)")

print(f"\n🔑 Ключевые факторы, влияющие на снегопад:")
for idx, row in importance_df.head(5).iterrows():
    print(f"  • {row['Признак']}: {row['Важность']:.4f}")

print(f"\n❄️ Условия, благоприятные для снега:")
print(f"  • Температура: от -10°C до 0°C")
print(f"  • Влажность: выше 85%")
print(f"  • Давление: ниже 1000 гПа")
print(f"  • Сезон: декабрь-февраль")
print(f"  • Время: ночь или раннее утро")

print("\n" + "="*70)
print("🎯 МОДЕЛЬ ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
print("="*70)

# Функция для интерактивного предсказания
def predict_snow_probability(temperature, humidity, pressure, wind_speed, 
                            cloud_ceiling, month, hour, model_path='snow_prediction_model.h5'):
    """
    Функция для предсказания вероятности снега на основе погодных параметров
    
    Параметры:
    - temperature: температура воздуха (°C)
    - humidity: влажность воздуха (%)
    - pressure: атмосферное давление (гПа)
    - wind_speed: скорость ветра (м/с)
    - cloud_ceiling: высота облачности (м)
    - month: месяц (1-12)
    - hour: час (0-23)
    """
    from tensorflow.keras.models import load_model
    
    # Загрузка модели и scaler'ов
    model = load_model(model_path)
    with open('snow_scaler_X.pkl', 'rb') as f:
        scaler_X = pickle.load(f)
    with open('snow_scaler_y.pkl', 'rb') as f:
        scaler_y = pickle.load(f)
    
    # Подготовка признаков
    is_winter = 1 if month in [12, 1, 2] else 0
    is_night = 1 if (hour < 6 or hour > 20) else 0
    temp_below_zero = 1 if temperature < 0 else 0
    
    features = np.array([[temperature, humidity, pressure, wind_speed, 
                         cloud_ceiling, month, hour, is_winter, is_night, temp_below_zero]])
    
    # Предсказание
    features_scaled = scaler_X.transform(features)
    prediction_scaled = model.predict(features_scaled, verbose=0)
    probability = scaler_y.inverse_transform(prediction_scaled)[0, 0]
    
    return probability

print("\n💡 Пример использования функции предсказания:")
print("""
# Предсказать вероятность снега для Москвы 15 января в 10:00
prob = predict_snow_probability(
    temperature=-8,    # -8°C
    humidity=92,       # 92% влажности
    pressure=998,      # 998 гПа
    wind_speed=4,      # 4 м/с
    cloud_ceiling=400, # 400 м облачность
    month=1,           # январь
    hour=10            # 10 часов утра
)
print(f"Вероятность снега: {prob*100:.1f}%")
""")