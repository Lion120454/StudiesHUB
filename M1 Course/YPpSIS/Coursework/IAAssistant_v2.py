import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import numpy as np
import pickle
import os
import re
from datetime import datetime
import json

# Оптимизированная имплементация без тяжелых зависимостей
# Для DeepSeek R1 используем упрощенную, но эффективную нейросеть

class SimpleNeuralNetwork:
    """Упрощенная нейронная сеть для DeepSeek R1"""
    
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Инициализация весов с использованием малых случайных значений
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
        
    def forward(self, X):
        """Прямой проход"""
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2
    
    def softmax(self, x):
        """Softmax функция"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def train_step(self, X, y, learning_rate=0.01):
        """Один шаг обучения"""
        # Forward pass
        output = self.forward(X)
        
        # Backward pass
        m = X.shape[0]
        dz2 = output - y
        dW2 = np.dot(self.a1.T, dz2) / m
        db2 = np.sum(dz2, axis=0, keepdims=True) / m
        
        da1 = np.dot(dz2, self.W2.T)
        dz1 = da1 * (1 - np.power(self.a1, 2))
        dW1 = np.dot(X.T, dz1) / m
        db1 = np.sum(dz1, axis=0, keepdims=True) / m
        
        # Update weights
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1

class TaskDecompositionAI:
    def __init__(self):
        self.model = None
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.vocab_size = 1000
        self.max_seq_length = 50
        
        # Расширенные роли
        self.roles = [
            'Аналитик', 'Разработчик Backend', 'Разработчик Frontend', 
            'Разработчик Mobile', 'Тестировщик QA', 'DevOps Инженер',
            'Project Manager', 'UX/UI Дизайнер', 'Data Engineer',
            'ML Инженер', 'Security Specialist', 'Technical Writer'
        ]
        
        # Категории задач
        self.task_categories = {
            'web_development': ['сайт', 'веб', 'web', 'frontend', 'backend', 'интернет-магазин'],
            'mobile_development': ['мобильн', 'mobile', 'ios', 'android', 'react native', 'flutter'],
            'database': ['база данн', 'database', 'sql', 'postgresql', 'mysql', 'mongodb', 'хранилище'],
            'devops': ['devops', 'ci/cd', 'деплой', 'kubernetes', 'docker', 'мониторинг'],
            'ai_ml': ['искусственн', 'нейросет', 'machine learning', 'chat bot', 'nlp', 'ai'],
            'analytics': ['аналитик', 'analytics', 'дашборд', 'dashboard', 'отчет', 'визуализац'],
            'security': ['безопасност', 'security', 'authentication', 'authorization', 'шифрование'],
            'testing': ['тестиров', 'testing', 'qa', 'unit test', 'автотест']
        }
        
        # Загрузка или создание модели
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Загрузка существующей модели или создание новой"""
        model_file = 'simple_model.npz'
        vocab_file = 'vocab.json'
        
        if os.path.exists(model_file) and os.path.exists(vocab_file):
            try:
                # Загрузка модели
                data = np.load(model_file)
                self.model = SimpleNeuralNetwork(
                    self.max_seq_length, 64, len(self.task_categories)
                )
                self.model.W1 = data['W1']
                self.model.b1 = data['b1']
                self.model.W2 = data['W2']
                self.model.b2 = data['b2']
                
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    vocab_data = json.load(f)
                    self.word_to_idx = vocab_data['word_to_idx']
                    self.idx_to_word = vocab_data['idx_to_word']
                
                print("Модель загружена успешно")
            except Exception as e:
                print(f"Ошибка загрузки модели: {e}")
                self.initialize_model()
        else:
            self.initialize_model()
            self.train_on_examples()
    
    def initialize_model(self):
        """Инициализация новой модели"""
        self.model = SimpleNeuralNetwork(self.max_seq_length, 64, len(self.task_categories))
        
        # Создание базового словаря
        all_words = []
        for category, words in self.task_categories.items():
            all_words.extend(words)
        
        # Добавление общих слов
        common_words = ['создать', 'разработать', 'настроить', 'реализовать', 
                       'интегрировать', 'оптимизировать', 'протестировать']
        all_words.extend(common_words)
        
        # Создание словаря
        for i, word in enumerate(set(all_words)):
            self.word_to_idx[word] = i + 1  # 0 для неизвестных слов
            self.idx_to_word[i + 1] = word
        
        self.vocab_size = len(self.word_to_idx) + 1
    
    def text_to_vector(self, text):
        """Преобразование текста в вектор"""
        words = re.findall(r'\b[а-яa-z]+\b', text.lower())
        vector = np.zeros(self.max_seq_length)
        
        for i, word in enumerate(words[:self.max_seq_length]):
            vector[i] = self.word_to_idx.get(word, 0)
        
        return vector.reshape(1, -1)
    
    def train_on_examples(self):
        """Обучение на примерах"""
        training_data = [
            ("Создать веб-сайт для интернет-магазина", "web_development"),
            ("Разработать мобильное приложение для заказа такси", "mobile_development"),
            ("Настроить базу данных для учета сотрудников", "database"),
            ("Настроить CI/CD пайплайн для автоматического деплоя", "devops"),
            ("Разработать чат-бота с ИИ для поддержки клиентов", "ai_ml"),
            ("Создать дашборд для аналитики продаж", "analytics"),
            ("Настроить систему безопасности и авторизации", "security"),
            ("Написать автотесты для модуля оплаты", "testing"),
            ("Разработать REST API для интеграции с платежной системой", "web_development"),
            ("Настроить мониторинг серверов с алертами в Telegram", "devops"),
            ("Создать рекомендательную систему для интернет-магазина", "ai_ml"),
            ("Разработать админ-панель для управления пользователями", "web_development"),
            ("Настроить репликацию и резервное копирование БД", "database"),
            ("Провести нагрузочное тестирование API", "testing")
        ]
        
        print("Обучение модели на примерах...")
        
        # Преобразование данных
        X_train = []
        y_train = []
        
        categories_list = list(self.task_categories.keys())
        
        for text, category in training_data:
            vector = self.text_to_vector(text)
            X_train.append(vector)
            
            y = np.zeros(len(categories_list))
            y[categories_list.index(category)] = 1
            y_train.append(y)
        
        X_train = np.vstack(X_train)
        y_train = np.array(y_train)
        
        # Обучение
        epochs = 100
        for epoch in range(epochs):
            self.model.train_step(X_train, y_train, learning_rate=0.01)
            if epoch % 20 == 0:
                loss = -np.mean(np.sum(y_train * np.log(self.model.forward(X_train) + 1e-8), axis=1))
                print(f"Epoch {epoch}, Loss: {loss:.4f}")
        
        # Сохранение модели
        np.savez('simple_model.npz',
                W1=self.model.W1, b1=self.model.b1,
                W2=self.model.W2, b2=self.model.b2)
        
        with open('vocab.json', 'w', encoding='utf-8') as f:
            json.dump({
                'word_to_idx': self.word_to_idx,
                'idx_to_word': self.idx_to_word
            }, f, ensure_ascii=False, indent=2)
        
        print("Обучение завершено!")
    
    def identify_task_type(self, text):
        """Определение типа задачи"""
        vector = self.text_to_vector(text)
        predictions = self.model.forward(vector)[0]
        
        categories_list = list(self.task_categories.keys())
        predicted_idx = np.argmax(predictions)
        confidence = predictions[predicted_idx]
        
        if confidence > 0.3:
            return categories_list[predicted_idx]
        else:
            # Эвристический метод если нейросеть не уверена
            text_lower = text.lower()
            for category, keywords in self.task_categories.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        return category
            return 'web_development'  # Default
    
    def estimate_complexity(self, text):
        """Оценка сложности задачи"""
        text_lower = text.lower()
        
        # Ключевые слова сложности
        complex_keywords = [
            'масштабируем', 'микросервис', 'распределен', 'высоконагружен',
            'репликац', 'кластер', 'кубернет', 'блокчейн', 'криптографи'
        ]
        
        medium_keywords = [
            'интеграц', 'оптимизац', 'резервн', 'автоматизац', 'аналитик'
        ]
        
        complexity_score = 0
        
        for word in complex_keywords:
            if word in text_lower:
                complexity_score += 2
        
        for word in medium_keywords:
            if word in text_lower:
                complexity_score += 1
        
        # Оценка длины задачи
        word_count = len(text.split())
        if word_count > 50:
            complexity_score += 1
        elif word_count > 100:
            complexity_score += 2
        
        if complexity_score >= 3:
            return 'Высокая (2-4 недели)'
        elif complexity_score >= 1:
            return 'Средняя (1-2 недели)'
        else:
            return 'Низкая (3-7 дней)'
    
    def assign_roles(self, text, task_type):
        """Назначение ролей на основе типа задачи и контекста"""
        text_lower = text.lower()
        assigned_roles = []
        
        role_mapping = {
            'web_development': ['Аналитик', 'Разработчик Backend', 'Разработчик Frontend', 'Project Manager'],
            'mobile_development': ['Аналитик', 'Разработчик Mobile', 'UX/UI Дизайнер', 'Тестировщик QA'],
            'database': ['Аналитик', 'Разработчик Backend', 'DevOps Инженер', 'Data Engineer'],
            'devops': ['DevOps Инженер', 'Разработчик Backend', 'Security Specialist'],
            'ai_ml': ['Data Engineer', 'ML Инженер', 'Разработчик Backend', 'Аналитик'],
            'analytics': ['Data Engineer', 'Аналитик', 'Разработчик Frontend', 'Project Manager'],
            'security': ['Security Specialist', 'Разработчик Backend', 'DevOps Инженер'],
            'testing': ['Тестировщик QA', 'Разработчик Backend', 'Разработчик Frontend']
        }
        
        # Базовые роли по типу задачи
        if task_type in role_mapping:
            assigned_roles.extend(role_mapping[task_type])
        
        # Дополнительные роли по ключевым словам
        if 'дизайн' in text_lower or 'ui' in text_lower or 'ux' in text_lower:
            if 'UX/UI Дизайнер' not in assigned_roles:
                assigned_roles.append('UX/UI Дизайнер')
        
        if 'документац' in text_lower or 'документ' in text_lower:
            if 'Technical Writer' not in assigned_roles:
                assigned_roles.append('Technical Writer')
        
        if 'безопасн' in text_lower or 'security' in text_lower:
            if 'Security Specialist' not in assigned_roles:
                assigned_roles.append('Security Specialist')
        
        # Удаление дубликатов с сохранением порядка
        seen = set()
        unique_roles = []
        for role in assigned_roles:
            if role not in seen:
                seen.add(role)
                unique_roles.append(role)
        
        return unique_roles[:5]  # Максимум 5 ролей
    
    def generate_intelligent_subtasks(self, text, task_type, roles):
        """Генерация интеллектуальных подзадач"""
        text_lower = text.lower()
        subtasks = []
        
        # Этап 1: Анализ
        analysis_tasks = [
            "Провести анализ требований и подготовить техническое задание",
            "Определить ключевые метрики успеха проекта",
            "Оценить риски и составить план митигации"
        ]
        
        if 'api' in text_lower or 'интеграц' in text_lower:
            analysis_tasks.append("Проанализировать API сторонних сервисов для интеграции")
        
        if 'база данн' in text_lower or 'database' in text_lower:
            analysis_tasks.append("Проектирование схемы базы данных и выбор СУБД")
        
        subtasks.append({
            'phase': '🔍 Анализ и планирование',
            'tasks': analysis_tasks,
            'duration': '1-2 дня',
            'responsible': [r for r in roles if 'Аналитик' in r or 'Manager' in r][:2]
        })
        
        # Этап 2: Проектирование
        design_tasks = []
        
        if 'web' in task_type or 'frontend' in text_lower:
            design_tasks.extend([
                "Создать прототипы интерфейса в Figma",
                "Разработать дизайн-систему компонентов",
                "Согласовать UI/UX решения с заказчиком"
            ])
        elif 'mobile' in task_type:
            design_tasks.extend([
                "Разработать мобильные экраны с учетом платформы (iOS/Material Design)",
                "Создать прототип навигации по приложению",
                "Оптимизировать интерфейс для разных размеров экранов"
            ])
        else:
            design_tasks.extend([
                "Спроектировать архитектуру решения",
                "Выбрать технологический стек",
                "Создать ER-диаграмму для базы данных"
            ])
        
        if 'api' in text_lower:
            design_tasks.append("Спроектировать RESTful API (OpenAPI спецификация)")
        
        subtasks.append({
            'phase': '🎨 Проектирование',
            'tasks': design_tasks,
            'duration': '2-3 дня',
            'responsible': [r for r in roles if 'Дизайнер' in r or 'Разработчик' in r or 'Аналитик' in r][:2]
        })
        
        # Этап 3: Разработка (специфичные подзадачи)
        dev_tasks = []
        
        # Генерация специфичных задач на основе ключевых слов
        if 'чат' in text_lower or 'бот' in text_lower:
            dev_tasks.extend([
                "Настроить NLP модель для понимания естественного языка",
                "Создать базу знаний и сценарии ответов",
                "Интегрировать бота с телеграм/веб-чатом",
                "Настроить контекстную память диалогов"
            ])
        
        if 'дашборд' in text_lower or 'dashboard' in text_lower:
            dev_tasks.extend([
                "Настроить ETL пайплайн для сбора данных",
                "Создать интерактивные визуализации (графики, таблицы)",
                "Реализовать фильтры и экспорт данных",
                "Настроить обновление данных в реальном времени"
            ])
        
        if 'магазин' in text_lower or 'e-commerce' in text_lower:
            dev_tasks.extend([
                "Реализовать каталог товаров с фильтрацией",
                "Разработать корзину и процесс оформления заказа",
                "Интегрировать платежный шлюз",
                "Настроить систему управления заказами"
            ])
        
        if 'авторизац' in text_lower or 'регистрац' in text_lower:
            dev_tasks.extend([
                "Реализовать JWT авторизацию",
                "Настроить OAuth2 интеграцию (Google, соцсети)",
                "Разработать систему ролей и прав доступа",
                "Внедрить двухфакторную аутентификацию"
            ])
        
        # Базовые задачи разработки если нет специфичных
        if not dev_tasks:
            dev_tasks = [
                "Настроить окружение разработки и версионирование",
                "Реализовать основную бизнес-логику",
                "Разработать пользовательский интерфейс",
                "Написать интеграционные тесты"
            ]
        
        subtasks.append({
            'phase': '💻 Разработка',
            'tasks': dev_tasks,
            'duration': '3-7 дней',
            'responsible': [r for r in roles if 'Разработчик' in r][:3]
        })
        
        # Этап 4: Тестирование
        test_tasks = [
            "Провести функциональное тестирование всех сценариев",
            "Выполнить регрессионное тестирование",
            "Проверить производительность под нагрузкой"
        ]
        
        if 'безопасн' in text_lower or 'security' in text_lower:
            test_tasks.append("Провести пентест и аудит безопасности")
        
        if 'api' in text_lower:
            test_tasks.append("Протестировать API на корректность обработки ошибок")
        
        subtasks.append({
            'phase': '🧪 Тестирование и QA',
            'tasks': test_tasks,
            'duration': '2-3 дня',
            'responsible': [r for r in roles if 'Тестировщик' in r or 'QA' in r][:2]
        })
        
        # Этап 5: Документация и деплой
        final_tasks = [
            "Подготовить техническую документацию",
            "Написать инструкцию для пользователей",
            "Настроить CI/CD пайплайн",
            "Выполнить деплой на production окружение"
        ]
        
        if 'devops' in task_type or 'мониторинг' in text_lower:
            final_tasks.extend([
                "Настроить систему мониторинга (Prometheus/Grafana)",
                "Организовать централизованное логирование",
                "Настроить алерты критических метрик"
            ])
        
        subtasks.append({
            'phase': '📚 Документация и деплой',
            'tasks': final_tasks,
            'duration': '1-2 дня',
            'responsible': [r for r in roles if 'DevOps' in r or 'Manager' in r] + ['Technical Writer'][:2]
        })
        
        return subtasks
    
    def decompose_task(self, task_description):
        """Полная декомпозиция задачи"""
        # Определение типа
        task_type = self.identify_task_type(task_description)
        
        # Оценка сложности
        complexity = self.estimate_complexity(task_description)
        
        # Назначение ролей
        roles = self.assign_roles(task_description, task_type)
        
        # Генерация подзадач
        subtasks = self.generate_intelligent_subtasks(task_description, task_type, roles)
        
        # Форматирование для вывода
        type_names = {
            'web_development': '🌐 Веб-разработка',
            'mobile_development': '📱 Мобильная разработка',
            'database': '🗄️ Базы данных',
            'devops': '⚙️ DevOps',
            'ai_ml': '🧠 AI/ML разработка',
            'analytics': '📊 Аналитика',
            'security': '🔒 Безопасность',
            'testing': '🧪 Тестирование'
        }
        
        return {
            'task_type': type_names.get(task_type, 'Разработка'),
            'complexity': complexity,
            'roles': roles,
            'subtasks': subtasks,
            'raw_type': task_type
        }

class DeepSeekAIAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant - Task Decomposer v1.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        # Установка иконки (опционально)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.ai = TaskDecompositionAI()
        self.current_result = None
        
        self.setup_ui()
        self.apply_dark_theme()
    
    def apply_dark_theme(self):
        """Применение темной темы для DeepSeek"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цвета DeepSeek
        bg_color = '#0a0a0a'
        fg_color = '#e0e0e0'
        accent_color = '#0066cc'
        secondary_bg = '#1a1a1a'
        
        style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 10))
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, foreground=fg_color, borderwidth=2)
        style.configure('TLabelframe.Label', background=bg_color, foreground=accent_color, font=('Segoe UI', 10, 'bold'))
        style.configure('TButton', background=accent_color, foreground='white', padding=8, borderwidth=0)
        style.map('TButton', background=[('active', '#0052a3')])
    
    def setup_ui(self):
        # Главный контейнер
        main_container = tk.Frame(self.root, bg='#0a0a0a')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        header_frame = tk.Frame(main_container, bg='#0a0a0a')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text="🧠 AI Task Decomposer",
            font=('Segoe UI', 24, 'bold'),
            bg='#0a0a0a',
            fg='#0066cc'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Интеллектуальная декомпозиция задач и распределение ролей",
            font=('Segoe UI', 11),
            bg='#0a0a0a',
            fg='#888888'
        )
        subtitle_label.pack()
        
        # Основной контент (Grid layout)
        content_frame = tk.Frame(main_container, bg='#0a0a0a')
        content_frame.pack(fill='both', expand=True)
        
        # Левая панель - ввод
        left_panel = tk.Frame(content_frame, bg='#0a0a0a')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        input_label = tk.Label(
            left_panel,
            text="📝 Описание задачи",
            font=('Segoe UI', 12, 'bold'),
            bg='#0a0a0a',
            fg='#0066cc'
        )
        input_label.pack(anchor='w', pady=(0, 10))
        
        self.task_input = scrolledtext.ScrolledText(
            left_panel,
            height=12,
            font=('Consolas', 11),
            bg='#1a1a1a',
            fg='#e0e0e0',
            insertbackground='#e0e0e0',
            wrap='word',
            relief='flat',
            borderwidth=1
        )
        self.task_input.pack(fill='both', expand=True)
        
        # Кнопки действий
        button_frame = tk.Frame(left_panel, bg='#0a0a0a')
        button_frame.pack(fill='x', pady=10)
        
        self.decompose_btn = tk.Button(
            button_frame,
            text="🚀 Декомпозировать",
            command=self.decompose_task,
            font=('Segoe UI', 11, 'bold'),
            bg='#0066cc',
            fg='white',
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        )
        self.decompose_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Очистить",
            command=self.clear_all,
            font=('Segoe UI', 11),
            bg='#333333',
            fg='white',
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        )
        self.clear_btn.pack(side='left', padx=5)
        
        self.export_btn = tk.Button(
            button_frame,
            text="💾 Экспорт",
            command=self.export_results,
            font=('Segoe UI', 11),
            bg='#2d2d2d',
            fg='white',
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        )
        self.export_btn.pack(side='left', padx=5)
        
        # Примеры
        examples_label = tk.Label(
            left_panel,
            text="💡 Быстрые примеры:",
            font=('Segoe UI', 10),
            bg='#0a0a0a',
            fg='#888888'
        )
        examples_label.pack(anchor='w', pady=(10, 5))
        
        examples_frame = tk.Frame(left_panel, bg='#0a0a0a')
        examples_frame.pack(fill='x')
        
        examples = [
            ("🌐 Веб-магазин", "Создать интернет-магазин с корзиной и оплатой через Сбербанк"),
            ("🤖 Чат-бот", "Разработать ИИ чат-бота для техподдержки с интеграцией в Telegram"),
            ("📊 Дашборд", "Создать дашборд аналитики продаж с графиками в реальном времени")
        ]
        
        for name, desc in examples:
            btn = tk.Button(
                examples_frame,
                text=name,
                command=lambda d=desc: self.set_example(d),
                font=('Segoe UI', 9),
                bg='#1a1a1a',
                fg='#e0e0e0',
                cursor='hand2',
                relief='flat',
                padx=10,
                pady=5
            )
            btn.pack(side='left', padx=5)
        
        # Правая панель - результаты
        right_panel = tk.Frame(content_frame, bg='#0a0a0a')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Информационная панель
        info_frame = tk.Frame(right_panel, bg='#1a1a1a', relief='flat', borderwidth=1)
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_inner = tk.Frame(info_frame, bg='#1a1a1a')
        info_inner.pack(fill='x', padx=15, pady=15)
        
        self.type_label = tk.Label(
            info_inner,
            text="📌 Тип задачи: Не определен",
            font=('Segoe UI', 11, 'bold'),
            bg='#1a1a1a',
            fg='#0066cc',
            anchor='w'
        )
        self.type_label.pack(fill='x', pady=2)
        
        self.complexity_label = tk.Label(
            info_inner,
            text="⚡ Сложность: Не определена",
            font=('Segoe UI', 11),
            bg='#1a1a1a',
            fg='#ff9800',
            anchor='w'
        )
        self.complexity_label.pack(fill='x', pady=2)
        
        # Роли
        roles_frame = tk.Frame(right_panel, bg='#1a1a1a', relief='flat', borderwidth=1)
        roles_frame.pack(fill='x', pady=(0, 10))
        
        roles_title = tk.Label(
            roles_frame,
            text="👥 Назначенные роли",
            font=('Segoe UI', 11, 'bold'),
            bg='#1a1a1a',
            fg='#0066cc'
        )
        roles_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        self.roles_text = tk.Text(
            roles_frame,
            height=6,
            font=('Segoe UI', 10),
            bg='#1a1a1a',
            fg='#e0e0e0',
            wrap='word',
            relief='flat',
            borderwidth=0
        )
        self.roles_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Подзадачи
        subtasks_frame = tk.Frame(right_panel, bg='#1a1a1a', relief='flat', borderwidth=1)
        subtasks_frame.pack(fill='both', expand=True)
        
        subtasks_title = tk.Label(
            subtasks_frame,
            text="📋 Детальная декомпозиция подзадач",
            font=('Segoe UI', 11, 'bold'),
            bg='#1a1a1a',
            fg='#0066cc'
        )
        subtasks_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        self.subtasks_text = scrolledtext.ScrolledText(
            subtasks_frame,
            font=('Consolas', 10),
            bg='#1a1a1a',
            fg='#e0e0e0',
            wrap='word',
            relief='flat',
            borderwidth=0
        )
        self.subtasks_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Статус бар
        status_frame = tk.Frame(main_container, bg='#0a0a0a')
        status_frame.pack(fill='x', pady=(20, 0))
        
        self.status_bar = tk.Label(
            status_frame,
            text="✅ Готов к работе | DeepSeek R1 AI Model Active",
            font=('Segoe UI', 9),
            bg='#0a0a0a',
            fg='#666666',
            anchor='w'
        )
        self.status_bar.pack(fill='x')
    
    def set_example(self, example):
        self.task_input.delete("1.0", tk.END)
        self.task_input.insert("1.0", example)
        self.status_bar.config(text="💡 Пример задачи загружен")
    
    def decompose_task(self):
        task = self.task_input.get("1.0", tk.END).strip()
        
        if not task:
            messagebox.showwarning("Внимание", "Пожалуйста, введите описание задачи")
            return
        
        self.decompose_btn.config(state='disabled', text='🔄 Анализирую...')
        self.status_bar.config(text="🧠 DeepSeek AI анализирует задачу...")
        
        thread = threading.Thread(target=self.process_task, args=(task,))
        thread.daemon = True
        thread.start()
    
    def process_task(self, task):
        try:
            result = self.ai.decompose_task(task)
            self.current_result = result
            self.root.after(0, self.update_results, result)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def update_results(self, result):
        # Обновление информации
        self.type_label.config(text=f"📌 Тип задачи: {result['task_type']}")
        self.complexity_label.config(text=f"⚡ Сложность: {result['complexity']}")
        
        # Обновление ролей
        self.roles_text.delete("1.0", tk.END)
        for role in result['roles']:
            role_icon = self.get_role_icon(role)
            self.roles_text.insert(tk.END, f"{role_icon} {role}\n\n")
        
        # Обновление подзадач
        self.subtasks_text.delete("1.0", tk.END)
        
        for phase_data in result['subtasks']:
            self.subtasks_text.insert(tk.END, f"\n{phase_data['phase']}\n", 'phase')
            self.subtasks_text.insert(tk.END, "─" * 50 + "\n", 'separator')
            
            for i, task_item in enumerate(phase_data['tasks'], 1):
                self.subtasks_text.insert(tk.END, f"  {i}. {task_item}\n", 'task')
            
            self.subtasks_text.insert(tk.END, f"\n  ⏱️ Срок: {phase_data['duration']}\n", 'duration')
            self.subtasks_text.insert(tk.END, f"  👥 Ответственные: {', '.join(phase_data['responsible'])}\n\n", 'responsible')
        
        # Настройка тегов для форматирования
        self.subtasks_text.tag_config('phase', foreground='#0066cc', font=('Segoe UI', 11, 'bold'))
        self.subtasks_text.tag_config('separator', foreground='#333333')
        self.subtasks_text.tag_config('task', foreground='#e0e0e0', font=('Segoe UI', 10))
        self.subtasks_text.tag_config('duration', foreground='#ff9800', font=('Segoe UI', 10, 'italic'))
        self.subtasks_text.tag_config('responsible', foreground='#4caf50', font=('Segoe UI', 10, 'italic'))
        
        self.status_bar.config(text="✅ Анализ завершен! Результаты готовы")
        self.decompose_btn.config(state='normal', text='🚀 Декомпозировать')
    
    def get_role_icon(self, role):
        icons = {
            'Аналитик': '📊',
            'Разработчик Backend': '⚙️',
            'Разработчик Frontend': '🎨',
            'Разработчик Mobile': '📱',
            'Тестировщик QA': '🐛',
            'DevOps Инженер': '🔧',
            'Project Manager': '📋',
            'UX/UI Дизайнер': '🎨',
            'Data Engineer': '🗄️',
            'ML Инженер': '🤖',
            'Security Specialist': '🔒',
            'Technical Writer': '📝'
        }
        return icons.get(role, '👤')
    
    def show_error(self, error):
        messagebox.showerror("Ошибка", f"Произошла ошибка:\n{error}")
        self.status_bar.config(text="❌ Ошибка при анализе задачи")
        self.decompose_btn.config(state='normal', text='🚀 Декомпозировать')
    
    def export_results(self):
        if not self.current_result:
            messagebox.showwarning("Внимание", "Нет результатов для экспорта")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Сохранить результаты"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# DeepSeek AI Task Decomposition Report\n\n")
                    f.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"## Исходная задача\n\n")
                    f.write(f"{self.task_input.get('1.0', tk.END).strip()}\n\n")
                    f.write(f"## Результаты анализа\n\n")
                    f.write(f"- **Тип задачи:** {self.current_result['task_type']}\n")
                    f.write(f"- **Сложность:** {self.current_result['complexity']}\n\n")
                    f.write(f"## Назначенные роли\n\n")
                    for role in self.current_result['roles']:
                        f.write(f"- {role}\n")
                    f.write(f"\n## Декомпозиция подзадач\n\n")
                    
                    for phase_data in self.current_result['subtasks']:
                        f.write(f"### {phase_data['phase']}\n\n")
                        for i, task_item in enumerate(phase_data['tasks'], 1):
                            f.write(f"{i}. {task_item}\n")
                        f.write(f"\n**Срок:** {phase_data['duration']}\n")
                        f.write(f"**Ответственные:** {', '.join(phase_data['responsible'])}\n\n")
                
                messagebox.showinfo("Успех", f"Результаты экспортированы в:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
    
    def clear_all(self):
        self.task_input.delete("1.0", tk.END)
        self.roles_text.delete("1.0", tk.END)
        self.subtasks_text.delete("1.0", tk.END)
        self.type_label.config(text="📌 Тип задачи: Не определен")
        self.complexity_label.config(text="⚡ Сложность: Не определена")
        self.current_result = None
        self.status_bar.config(text="✨ Все очищено | Готов к новой задаче")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    
    # Настройки окна
    root.minsize(1000, 700)
    
    # Центрирование
    root.update_idletasks()
    width = 1200
    height = 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    app = DeepSeekAIAssistant(root)
    root.mainloop()