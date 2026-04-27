#Реализовать с использованием библиотеки keras нейронную сеть для решения задачи классификации (Задание в)
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, mean_absolute_error, r2_score
import yfinance as yf
from keras.models import Model
from keras.layers import Input, LSTM, Dense, Dropout, GRU, Bidirectional, concatenate
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.optimizers import Adam
import seaborn as sns
from datetime import datetime, timedelta

# Установка random seed для воспроизводимости
np.random.seed(42)

class DollarPredictor:
    def __init__(self, sequence_length=30):
        """
        Инициализация класса для прогнозирования курса доллара
        
        Parameters:
        -----------
        sequence_length : int
            Количество предыдущих дней для прогнозирования
        """
        self.sequence_length = sequence_length
        self.scaler_X = MinMaxScaler(feature_range=(0, 1))
        self.scaler_y = MinMaxScaler(feature_range=(0, 1))
        self.classification_threshold = 0.001  # Порог для классификации направления
        
    def load_data(self, ticker='USDRUB=X', period='5y'):
        """
        Загрузка данных с Yahoo Finance
        
        Parameters:
        -----------
        ticker : str
            Тикер валютной пары
        period : str
            Период загрузки данных
            
        Returns:
        --------
        pd.DataFrame
            DataFrame с данными
        """
        print(f"Загрузка данных для {ticker}...")
        data = yf.download(ticker, period=period, interval='1d')
        
        # Создание дополнительных признаков
        data['Returns'] = data['Close'].pct_change()
        data['High-Low'] = data['High'] - data['Low']
        data['Close-Open'] = data['Close'] - data['Open']
        
        # Технические индикаторы
        data['SMA_5'] = data['Close'].rolling(window=5).mean()
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
        data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Волатильность
        data['Volatility'] = data['Returns'].rolling(window=20).std()
        
        # Удаление NaN значений
        data = data.dropna()
        
        print(f"Загружено {len(data)} дней данных")
        return data
    
    def create_sequences(self, data, feature_columns, target_column):
        """
        Создание последовательностей для обучения
        
        Parameters:
        -----------
        data : pd.DataFrame
            Исходные данные
        feature_columns : list
            Список признаков
        target_column : str
            Целевая переменная
            
        Returns:
        --------
        X, y_regression, y_classification
        """
        X, y_regression, y_classification = [], [], []
        prices = data[target_column].values
        
        for i in range(self.sequence_length, len(data)):
            # Признаки
            X.append(data[feature_columns].iloc[i-self.sequence_length:i].values)
            
            # Регрессия - предсказание следующего значения
            y_regression.append(prices[i])
            
            # Классификация - направление движения цены
            price_change = (prices[i] - prices[i-1]) / prices[i-1]
            if price_change > self.classification_threshold:
                y_classification.append(1)  # Рост
            elif price_change < -self.classification_threshold:
                y_classification.append(2)  # Падение
            else:
                y_classification.append(0)  # Нейтрально
        
        return np.array(X), np.array(y_regression), np.array(y_classification)
    
    def prepare_data(self, data, test_size=0.2):
        """
        Подготовка данных для обучения
        
        Parameters:
        -----------
        data : pd.DataFrame
            Исходные данные
        test_size : float
            Размер тестовой выборки
        """
        # Выбор признаков
        feature_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Returns', 
                          'High-Low', 'Close-Open', 'SMA_5', 'SMA_20', 
                          'MACD', 'Signal_Line', 'RSI', 'Volatility']
        
        # Проверка наличия всех признаков
        available_features = [col for col in feature_columns if col in data.columns]
        
        target_column = 'Close'
        
        # Создание последовательностей
        X, y_reg, y_class = self.create_sequences(data, available_features, target_column)
        
        # Разделение на обучающую и тестовую выборки (с сохранением временной структуры)
        split_idx = int(len(X) * (1 - test_size))
        
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_reg_train, y_reg_test = y_reg[:split_idx], y_reg[split_idx:]
        y_class_train, y_class_test = y_class[:split_idx], y_class[split_idx:]
        
        # Масштабирование признаков
        n_samples, n_timesteps, n_features = X_train.shape
        X_train_reshaped = X_train.reshape(-1, n_features)
        X_test_reshaped = X_test.reshape(-1, n_features)
        
        X_train_scaled = self.scaler_X.fit_transform(X_train_reshaped)
        X_test_scaled = self.scaler_X.transform(X_test_reshaped)
        
        X_train = X_train_scaled.reshape(n_samples, n_timesteps, n_features)
        X_test = X_test_scaled.reshape(-1, n_timesteps, n_features)
        
        # Масштабирование целевой переменной для регрессии
        y_reg_train = y_reg_train.reshape(-1, 1)
        y_reg_test = y_reg_test.reshape(-1, 1)
        
        y_reg_train_scaled = self.scaler_y.fit_transform(y_reg_train).flatten()
        y_reg_test_scaled = self.scaler_y.transform(y_reg_test).flatten()
        
        return (X_train, X_test, 
                y_reg_train_scaled, y_reg_test_scaled,
                y_class_train, y_class_test,
                data.index[self.sequence_length:], available_features)
    
    def build_multi_output_model(self, n_features, n_classes=3):
        """
        Создание модели с несколькими выходами
        
        Parameters:
        -----------
        n_features : int
            Количество признаков
        n_classes : int
            Количество классов для классификации
            
        Returns:
        --------
        keras.Model
            Модель для одновременного решения задач регрессии и классификации
        """
        # Входной слой
        input_layer = Input(shape=(self.sequence_length, n_features))
        
        # Первый LSTM слой
        x = Bidirectional(LSTM(128, return_sequences=True))(input_layer)
        x = Dropout(0.3)(x)
        
        # Второй LSTM слой
        x = Bidirectional(LSTM(64, return_sequences=True))(x)
        x = Dropout(0.3)(x)
         

        # Третий LSTM слой
        x = LSTM(32)(x)
        x = Dropout(0.3)(x)
        
        # Разделение на две ветки
        # Ветка для регрессии
        reg_branch = Dense(64, activation='relu')(x)
        reg_branch = Dropout(0.2)(reg_branch)
        reg_branch = Dense(32, activation='relu')(reg_branch)
        regression_output = Dense(1, name='regression')(reg_branch)
        
        # Ветка для классификации
        class_branch = Dense(64, activation='relu')(x)
        class_branch = Dropout(0.2)(class_branch)
        class_branch = Dense(32, activation='relu')(class_branch)
        classification_output = Dense(n_classes, activation='softmax', name='classification')(class_branch)
        
        # Создание модели
        model = Model(inputs=input_layer, 
                     outputs=[regression_output, classification_output])
        
        # Компиляция модели с разными функциями потерь для каждой задачи
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss={
                'regression': 'mse',
                'classification': 'sparse_categorical_crossentropy'
            },
            loss_weights={
                'regression': 0.5,
                'classification': 0.5
            },
            metrics={
                'regression': ['mae'],
                'classification': ['accuracy']
            }
        )
        
        return model
    
    def train_model(self, X_train, y_reg_train, y_class_train, X_test, y_reg_test, y_class_test):
        """
        Обучение модели
        
        Parameters:
        -----------
        X_train, X_test : numpy arrays
            Обучающие и тестовые данные
        y_reg_train, y_reg_test : numpy arrays
            Целевые значения для регрессии
        y_class_train, y_class_test : numpy arrays
            Целевые значения для классификации
            
        Returns:
        --------
        model, history
        """
        n_features = X_train.shape[2]
        model = self.build_multi_output_model(n_features)
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=0.00001,
            verbose=1
        )
        
        # Обучение модели
        history = model.fit(
            X_train,
            {'regression': y_reg_train, 'classification': y_class_train},
            epochs=100,
            batch_size=32,
            validation_data=(
                X_test,
                {'regression': y_reg_test, 'classification': y_class_test}
            ),
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        return model, history
    
    def evaluate_model(self, model, X_test, y_reg_test, y_class_test, dates, original_prices):
        """
        Оценка модели
        
        Parameters:
        -----------
        model : keras.Model
            Обученная модель
        X_test : numpy array
            Тестовые данные
        y_reg_test : numpy array
            Истинные значения для регрессии
        y_class_test : numpy array
            Истинные значения для классификации
        dates : pandas index
            Даты
        original_prices : numpy array
            Оригинальные цены для обратного масштабирования
        """
        # Предсказания
        y_pred_reg_scaled, y_pred_class = model.predict(X_test)
        
        # Обратное масштабирование для регрессии
        y_pred_reg = self.scaler_y.inverse_transform(y_pred_reg_scaled.reshape(-1, 1)).flatten()
        y_reg_test_original = self.scaler_y.inverse_transform(y_reg_test.reshape(-1, 1)).flatten()
        
        # Оценка регрессии
        mse = mean_squared_error(y_reg_test_original, y_pred_reg)
        mae = mean_absolute_error(y_reg_test_original, y_pred_reg)
        r2 = r2_score(y_reg_test_original, y_pred_reg)
        
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ РЕГРЕССИИ")
        print("="*50)
        print(f"MSE: {mse:.6f}")
        print(f"MAE: {mae:.6f}")
        print(f"R2 Score: {r2:.6f}")
        print(f"RMSE: {np.sqrt(mse):.6f}")
        
        # Оценка классификации
        y_pred_class_labels = np.argmax(y_pred_class, axis=1)
        
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ КЛАССИФИКАЦИИ")
        print("="*50)
        print("\nClassification Report:")
        print(classification_report(y_class_test, y_pred_class_labels, 
                                   target_names=['Нейтрально', 'Рост', 'Падение']))
        
        # Визуализация результатов
        self.plot_results(dates[-len(y_reg_test_original):], 
                         y_reg_test_original, y_pred_reg,
                         y_class_test, y_pred_class_labels)
        
        # Матрица ошибок для классификации
        plt.figure(figsize=(8, 6))
        cm = confusion_matrix(y_class_test, y_pred_class_labels)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Нейтрально', 'Рост', 'Падение'],
                   yticklabels=['Нейтрально', 'Рост', 'Падение'])
        plt.title('Матрица ошибок для классификации направления')
        plt.ylabel('Истинные значения')
        plt.xlabel('Предсказанные значения')
        plt.show()
        
        return y_pred_reg, y_pred_class_labels
    
    def plot_results(self, dates, y_true, y_pred, y_class_true, y_class_pred):
        """
        Визуализация результатов
        """
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # График регрессии
        axes[0].plot(dates, y_true, label='Фактический курс', color='blue', alpha=0.7)
        axes[0].plot(dates, y_pred, label='Прогнозируемый курс', color='red', alpha=0.7)
        axes[0].set_title('Прогнозирование курса доллара (Регрессия)')
        axes[0].set_xlabel('Дата')
        axes[0].set_ylabel('Курс')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Ошибка прогноза
        error = y_true - y_pred
        axes[1].plot(dates, error, color='green', alpha=0.7)
        axes[1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[1].fill_between(dates, error, 0, where=(error>0), color='green', alpha=0.3)
        axes[1].fill_between(dates, error, 0, where=(error<0), color='red', alpha=0.3)
        axes[1].set_title('Ошибка прогноза (Факт - Прогноз)')
        axes[1].set_xlabel('Дата')
        axes[1].set_ylabel('Ошибка')
        axes[1].grid(True, alpha=0.3)
        
        # Классификация направления
        axes[2].plot(dates, y_class_true, label='Истинное направление', color='blue', alpha=0.7)
        axes[2].plot(dates, y_class_pred, label='Предсказанное направление', color='red', alpha=0.7)
        axes[2].set_title('Классификация направления движения')
        axes[2].set_xlabel('Дата')
        axes[2].set_ylabel('Класс (0=Нейтр, 1=Рост, 2=Падение)')
        axes[2].set_yticks([0, 1, 2])
        axes[2].set_yticklabels(['Нейтр', 'Рост', 'Падение'])
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def predict_future(self, model, last_sequence, n_days=5):
        """
        Прогнозирование на будущие дни
        
        Parameters:
        -----------
        model : keras.Model
            Обученная модель
        last_sequence : numpy array
            Последняя последовательность данных
        n_days : int
            Количество дней для прогноза
            
        Returns:
        --------
        predictions, directions
        """
        predictions = []
        directions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(n_days):
            # Прогноз
            pred_scaled, direction_proba = model.predict(current_sequence.reshape(1, self.sequence_length, -1))
            
            # Обратное масштабирование
            pred = self.scaler_y.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()[0]
            direction = np.argmax(direction_proba[0])
            
            predictions.append(pred)
            directions.append(direction)
            
            # Обновление последовательности (сдвиг и добавление нового предсказания)
            new_row = current_sequence[-1].copy()
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1] = new_row
        
        return predictions, directions

# Основная программа
def main():
    print("Прогнозирование курса доллара с использованием Keras")
    print("="*60)
    
    # Создание экземпляра класса
    predictor = DollarPredictor(sequence_length=30)
    
    # Загрузка данных
    data = predictor.load_data(ticker='USDRUB=X', period='5y')
    
    # Подготовка данных
    (X_train, X_test, 
     y_reg_train, y_reg_test,
     y_class_train, y_class_test,
     dates, features) = predictor.prepare_data(data, test_size=0.2)
    
    print(f"\nФорма обучающих данных: {X_train.shape}")
    print(f"Форма тестовых данных: {X_test.shape}")
    print(f"Используемые признаки: {features}")
    
    # Обучение модели
    print("\n" + "="*60)
    print("ОБУЧЕНИЕ МОДЕЛИ")
    print("="*60)
    
    model, history = predictor.train_model(
        X_train, y_reg_train, y_class_train,
        X_test, y_reg_test, y_class_test
    )
    
    # Вывод архитектуры модели
    print("\nАрхитектура модели:")
    model.summary()
    
    # Графики обучения
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # График потерь
    axes[0, 0].plot(history.history['loss'], label='Train Loss')
    axes[0, 0].plot(history.history['val_loss'], label='Val Loss')
    axes[0, 0].set_title('Общие потери модели')
    axes[0, 0].set_xlabel('Эпоха')
    axes[0, 0].set_ylabel('Потери')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # График потерь для регрессии
    axes[0, 1].plot(history.history['regression_loss'], label='Train Regression Loss')
    axes[0, 1].plot(history.history['val_regression_loss'], label='Val Regression Loss')
    axes[0, 1].set_title('Потери регрессии')
    axes[0, 1].set_xlabel('Эпоха')
    axes[0, 1].set_ylabel('MSE')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # График потерь для классификации
    axes[1, 0].plot(history.history['classification_loss'], label='Train Classification Loss')
    axes[1, 0].plot(history.history['val_classification_loss'], label='Val Classification Loss')
    axes[1, 0].set_title('Потери классификации')
    axes[1, 0].set_xlabel('Эпоха')
    axes[1, 0].set_ylabel('Cross-entropy')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # График точности классификации
    axes[1, 1].plot(history.history['classification_accuracy'], label='Train Accuracy')
    axes[1, 1].plot(history.history['val_classification_accuracy'], label='Val Accuracy')
    axes[1, 1].set_title('Точность классификации')
    axes[1, 1].set_xlabel('Эпоха')
    axes[1, 1].set_ylabel('Accuracy')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Оценка модели
    y_pred_reg, y_pred_class = predictor.evaluate_model(
        model, X_test, y_reg_test, y_class_test, dates,
        data['Close'].values
    )
    
    # Прогноз на будущее
    print("\n" + "="*60)
    print("ПРОГНОЗ НА БУДУЩИЕ ДНИ")
    print("="*60)
    
    last_sequence = X_test[-1]
    future_predictions, future_directions = predictor.predict_future(model, last_sequence, n_days=5)
    
    last_date = dates[-1]
    direction_names = ['Нейтрально', 'Рост', 'Падение']
    
    for i, (pred, direction) in enumerate(zip(future_predictions, future_directions), 1):
        future_date = last_date + timedelta(days=i)
        print(f"{future_date.strftime('%Y-%m-%d')}: Прогноз = {pred:.4f}, "
              f"Направление = {direction_names[direction]}")

if __name__ == "__main__":
    main()


