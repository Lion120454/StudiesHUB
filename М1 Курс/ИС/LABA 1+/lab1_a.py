#Реализовать и разобрать алгоритм обратного распространенияошибки на языке python реализованный с параллельными вычислениями. Задание а.
import numpy as np
import multiprocessing as mp
from multiprocessing import Pool
import time
from typing import List, Tuple
import matplotlib.pyplot as plt

class ParallelNeuralNetwork:
    """
    Нейронная сеть с параллельным обучением методом обратного распространения ошибки
    """
    def __init__(self, layer_sizes: List[int], learning_rate: float = 0.01):
        """
        layer_sizes: список размеров слоев [input_size, hidden_size, ..., output_size]
        learning_rate: скорость обучения
        """
        self.layer_sizes = layer_sizes
        self.learning_rate = learning_rate
        self.num_layers = len(layer_sizes)
        
        # Инициализация весов и смещений
        self.weights = []
        self.biases = []
        
        for i in range(self.num_layers - 1):
            # Инициализация Xavier/Glorot для лучшей сходимости
            w = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros((1, layer_sizes[i + 1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Сигмоидальная функция активации"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))  # Защита от переполнения
    
    def sigmoid_derivative(self, x: np.ndarray) -> np.ndarray:
        """Производная сигмоидальной функции"""
        sig = (x)
        return sig * (1 - sig)
    
    def forward_pass(self, X: np.ndarray) -> List[np.ndarray]:
        """
        Прямой проход по сети
        Возвращает активации всех слоев
        """
        activations = [X]
        current = X
        
        for i in range(self.num_layers - 1):
            z = np.dot(current, self.weights[i]) + self.biases[i]
            current = self.sigmoid(z)
            activations.append(current)
        
        return activations
    
    def backward_pass(self, activations: List[np.ndarray], y_true: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Обратный проход для вычисления градиентов
        """
        m = y_true.shape[0]  # количество примеров
        grad_weights = [np.zeros_like(w) for w in self.weights]
        grad_biases = [np.zeros_like(b) for b in self.biases]
        
        # Выходной слой
        delta = (activations[-1] - y_true) * self.sigmoid_derivative(activations[-1])
        
        # Обратное распространение
        for layer in range(self.num_layers - 2, -1, -1):
            grad_weights[layer] = np.dot(activations[layer].T, delta) / m
            grad_biases[layer] = np.sum(delta, axis=0, keepdims=True) / m
            
            if layer > 0:
                delta = np.dot(delta, self.weights[layer].T) * self.sigmoid_derivative(activations[layer])
        
        return grad_weights, grad_biases
    
    def compute_loss(self, y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """Вычисление среднеквадратичной ошибки"""
        return np.mean((y_pred - y_true) ** 2)

def train_worker(args):
    """
    Функция для параллельного обучения на подмножестве данных
    """
    network_params, X_batch, y_batch, worker_id = args
    
    # Создаем локальную копию сети
    local_network = ParallelNeuralNetwork(network_params['layer_sizes'], 
                                         network_params['learning_rate'])
    local_network.weights = [w.copy() for w in network_params['weights']]
    local_network.biases = [b.copy() for b in network_params['biases']]
    
    # Прямой проход
    activations = local_network.forward_pass(X_batch)
    
    # Обратный проход для вычисления градиентов
    grad_weights, grad_biases = local_network.backward_pass(activations, y_batch)
    
    # Вычисляем локальную ошибку
    loss = local_network.compute_loss(activations[-1], y_batch)
    
    return grad_weights, grad_biases, loss, worker_id

class ParallelBackpropagation:
    """
    Класс для управления параллельным обучением
    """
    def __init__(self, network: ParallelNeuralNetwork, num_workers: int = 4):
        self.network = network
        self.num_workers = min(num_workers, mp.cpu_count())
        print(f"Используется {self.num_workers} процессов")
        
    def parallel_training_step(self, X: np.ndarray, y: np.ndarray, batch_size: int = 32):
        """
        Один шаг параллельного обучения
        """
        num_samples = X.shape[0]
        
        # Разбиваем данные на батчи для параллельной обработки
        indices = np.random.permutation(num_samples)
        batch_starts = range(0, num_samples, batch_size)
        
        all_grad_weights = []
        all_grad_biases = []
        batch_losses = []
        
        # Создаем пул процессов
        with Pool(processes=self.num_workers) as pool:
            for start_idx in batch_starts:
                end_idx = min(start_idx + batch_size, num_samples)
                batch_indices = indices[start_idx:end_idx]
                
                X_batch = X[batch_indices]
                y_batch = y[batch_indices]
                
                # Подготавливаем параметры для каждого воркера
                network_params = {
                    'layer_sizes': self.network.layer_sizes,
                    'learning_rate': self.network.learning_rate,
                    'weights': self.network.weights,
                    'biases': self.network.biases
                }
                
                # Разбиваем батч на еще меньшие части для параллельной обработки
                mini_batch_size = max(1, len(X_batch) // self.num_workers)
                mini_batches = []
                
                for i in range(0, len(X_batch), mini_batch_size):
                    mini_X = X_batch[i:i + mini_batch_size]
                    mini_y = y_batch[i:i + mini_batch_size]
                    if len(mini_X) > 0:
                        mini_batches.append((network_params, mini_X, mini_y, i))
                
                # Параллельно обрабатываем мини-батчи
                if mini_batches:
                    results = pool.map(train_worker, mini_batches)
                    
                    # Агрегируем результаты
                    batch_grad_weights = [np.zeros_like(w) for w in self.network.weights]
                    batch_grad_biases = [np.zeros_like(b) for b in self.network.biases]
                    
                    total_samples = 0
                    for grad_w, grad_b, loss, _ in results:
                        for i in range(len(batch_grad_weights)):
                            # Взвешиваем по размеру батча
                            batch_grad_weights[i] += grad_w[i] * len(grad_w[i]) if i < len(grad_w) else 0
                            batch_grad_biases[i] += grad_b[i] * len(grad_b[i]) if i < len(grad_b) else 0
                        batch_losses.append(loss)
                        total_samples += 1
                    
                    # Усредняем градиенты
                    if total_samples > 0:
                        for i in range(len(batch_grad_weights)):
                            batch_grad_weights[i] /= total_samples
                            batch_grad_biases[i] /= total_samples
                        
                        all_grad_weights.append(batch_grad_weights)
                        all_grad_biases.append(batch_grad_biases)
        
        # Усредняем градиенты по всем батчам
        if all_grad_weights:
            avg_grad_weights = [np.zeros_like(w) for w in self.network.weights]
            avg_grad_biases = [np.zeros_like(b) for b in self.network.biases]
            
            for grad_w, grad_b in zip(all_grad_weights, all_grad_biases):
                for i in range(len(avg_grad_weights)):
                    avg_grad_weights[i] += grad_w[i]
                    avg_grad_biases[i] += grad_b[i]
            
            for i in range(len(avg_grad_weights)):
                avg_grad_weights[i] /= len(all_grad_weights)
                avg_grad_biases[i] /= len(all_grad_biases)
            
            # Обновляем веса
            for i in range(len(self.network.weights)):
                self.network.weights[i] -= self.network.learning_rate * avg_grad_weights[i]
                self.network.biases[i] -= self.network.learning_rate * avg_grad_biases[i]
        
        return np.mean(batch_losses) if batch_losses else 0
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, 
              batch_size: int = 32, verbose: bool = True):
        """
        Полный цикл обучения
        """
        losses = []
        
        for epoch in range(epochs):
            start_time = time.time()
            
            # Параллельный шаг обучения
            loss = self.parallel_training_step(X, y, batch_size)
            losses.append(loss)
            
            if verbose and (epoch + 1) % 10 == 0:
                elapsed_time = time.time() - start_time
                print(f"Эпоха {epoch + 1}/{epochs}, Потери: {loss:.6f}, "
                      f"Время: {elapsed_time:.3f}с")
        
        return losses

# ИСПРАВЛЕННАЯ функция генерации данных
def generate_sample_data(n_samples: int = 1000):
    """Генерация синтетических данных для задачи классификации"""
    np.random.seed(42)
    
    # Генерируем два класса
    X = np.random.randn(n_samples, 2)
    
    # Создаем метки классов (0 или 1) как float
    y = (X[:, 0] ** 2 + X[:, 1] ** 2 < 1).astype(np.float32).reshape(-1, 1)
    
    # Добавляем немного шума - теперь это безопасно, так как y уже float
    noise = 0.1 * np.random.randn(n_samples, 1).astype(np.float32)
    y = y + noise
    
    # Клиппинг для сохранения в диапазоне [0, 1]
    y = np.clip(y, 0, 1)
    
    return X, y

def compare_parallel_vs_sequential():
    """Сравнение параллельного и последовательного обучения"""
    # Генерируем данные
    X, y = generate_sample_data(2000)
    
    # Создаем сети
    layer_sizes = [2, 10, 8, 1]
    
    # Параллельное обучение
    print("=== Параллельное обучение ===")
    network_parallel = ParallelNeuralNetwork(layer_sizes, learning_rate=0.1)
    trainer_parallel = ParallelBackpropagation(network_parallel, num_workers=4)
    
    start_time = time.time()
    losses_parallel = trainer_parallel.train(X, y, epochs=50, batch_size=128, verbose=True)
    parallel_time = time.time() - start_time
    
    # Последовательное обучение
    print("\n=== Последовательное обучение ===")
    network_seq = ParallelNeuralNetwork(layer_sizes, learning_rate=0.1)
    
    start_time = time.time()
    losses_seq = []
    for epoch in range(50):
        # Простое последовательное обучение
        activations = network_seq.forward_pass(X)
        grad_w, grad_b = network_seq.backward_pass(activations, y)
        
        # Обновление весов
        for i in range(len(network_seq.weights)):
            network_seq.weights[i] -= network_seq.learning_rate * grad_w[i]
            network_seq.biases[i] -= network_seq.learning_rate * grad_b[i]
        
        loss = network_seq.compute_loss(activations[-1], y)
        losses_seq.append(loss)
        
        if (epoch + 1) % 10 == 0:
            print(f"Эпоха {epoch + 1}/50, Потери: {loss:.6f}")
    
    sequential_time = time.time() - start_time
    
    # Вывод результатов сравнения
    print(f"\n=== Результаты сравнения ===")
    print(f"Время параллельного обучения: {parallel_time:.3f} секунд")
    print(f"Время последовательного обучения: {sequential_time:.3f} секунд")
    print(f"Ускорение: {sequential_time/parallel_time:.2f}x")
    
    # Визуализация
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(losses_parallel, label='Параллельное', color='blue')
    plt.plot(losses_seq, label='Последовательное', color='red', alpha=0.7)
    plt.xlabel('Эпоха')
    plt.ylabel('Потери')
    plt.title('Сходимость обучения')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    times = ['Параллельное', 'Последовательное']
    values = [parallel_time, sequential_time]
    colors = ['blue', 'red']
    plt.bar(times, values, color=colors, alpha=0.7)
    plt.ylabel('Время (секунды)')
    plt.title('Сравнение времени выполнения')
    for i, v in enumerate(values):
        plt.text(i, v + 0.1, f'{v:.2f}с', ha='center')
    
    plt.tight_layout()
    plt.show()

def demonstrate_prediction():
    """Демонстрация предсказаний обученной сети"""
    # Генерируем данные
    X, y = generate_sample_data(1000)
    
    # Создаем и обучаем сеть
    network = ParallelNeuralNetwork([2, 10, 8, 1], learning_rate=0.1)
    trainer = ParallelBackpropagation(network, num_workers=4)
    
    print("Обучение сети...")
    losses = trainer.train(X, y, epochs=100, batch_size=64, verbose=True)
    
    # Тестирование на новых данных
    X_test, y_test = generate_sample_data(200)
    
    # Прямой проход для предсказаний
    activations = network.forward_pass(X_test)
    predictions = activations[-1]
    
    # Вычисляем точность
    accuracy = np.mean((predictions > 0.5) == (y_test > 0.5))
    print(f"\nТочность на тестовых данных: {accuracy:.2%}")
    
    # Визуализация результатов
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.plot(losses)
    plt.xlabel('Эпоха')
    plt.ylabel('Потери')
    plt.title('Динамика обучения')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    # Визуализация границ решения
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                         np.linspace(y_min, y_max, 100))
    
    Z = network.forward_pass(np.c_[xx.ravel(), yy.ravel()])[-1]
    Z = Z.reshape(xx.shape)
    
    plt.contourf(xx, yy, Z, alpha=0.3, cmap='RdBu', levels=20)
    plt.scatter(X_test[:, 0], X_test[:, 1], c=y_test.ravel(), 
               cmap='RdBu', edgecolor='black', alpha=0.6)
    plt.xlabel('Признак 1')
    plt.ylabel('Признак 2')
    plt.title('Границы решения')
    plt.colorbar()
    
    plt.subplot(1, 3, 3)
    plt.scatter(y_test, predictions, alpha=0.6)
    plt.plot([0, 1], [0, 1], 'r--', label='Идеальное предсказание')
    plt.xlabel('Истинные значения')
    plt.ylabel('Предсказания')
    plt.title('Предсказания vs Истина')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Настраиваем multiprocessing для Windows
    mp.freeze_support()
    
    print("Алгоритм обратного распространения ошибки с параллельными вычислениями")
    print("=" * 60)
    
    # Демонстрация предсказаний
    demonstrate_prediction()
    
    # Сравнение производительности
    compare_parallel_vs_sequential()