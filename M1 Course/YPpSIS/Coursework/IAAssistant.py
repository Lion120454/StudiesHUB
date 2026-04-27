import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import pickle
import os
import re
from datetime import datetime

class TaskDecompositionAI:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.max_sequence_len = 100
        self.roles = ['Аналитик', 'Разработчик', 'Тестировщик', 'DevOps', 'Project Manager', 'Дизайнер', 'Data Scientist']
        
        # Создаем или загружаем модель
        self.init_model()
        
    def init_model(self):
        """Инициализация нейронной сети"""
        model_path = 'task_decomposer_model.h5'
        tokenizer_path = 'tokenizer.pkl'
        
        if os.path.exists(model_path) and os.path.exists(tokenizer_path):
            # Загрузка существующей модели
            self.model = keras.models.load_model(model_path)
            with open(tokenizer_path, 'rb') as f:
                self.tokenizer = pickle.load(f)
        else:
            # Создание новой модели (будет обучена на примерах)
            self.create_model()
            # Обучаем на тестовых данных
            self.train_demo()
    
    def create_model(self):
        """Создание архитектуры нейронной сети"""
        vocabulary_size = 5000
        embedding_dim = 128
        
        # Модель для понимания текста задачи
        input_text = layers.Input(shape=(self.max_sequence_len,))
        embedding = layers.Embedding(vocabulary_size, embedding_dim)(input_text)
        lstm = layers.LSTM(256, return_sequences=True)(embedding)
        lstm = layers.LSTM(128)(lstm)
        dense = layers.Dense(256, activation='relu')(lstm)
        dropout = layers.Dropout(0.3)(dense)
        
        # Выходные слои: тип задачи, сложность, предложение по ролям
        task_type = layers.Dense(8, activation='softmax', name='task_type')(dropout)
        complexity = layers.Dense(3, activation='softmax', name='complexity')(dropout)
        roles_output = layers.Dense(len(self.roles), activation='sigmoid', name='roles')(dropout)
        
        self.model = keras.Model(inputs=input_text, outputs=[task_type, complexity, roles_output])
        self.model.compile(
            optimizer='adam',
            loss={
                'task_type': 'categorical_crossentropy',
                'complexity': 'categorical_crossentropy',
                'roles': 'binary_crossentropy'
            },
            metrics={
                'task_type': ['accuracy'],
                'complexity': ['accuracy'],
                'roles': ['accuracy']
            }
        )
    
    def text_to_sequence(self, text):
        """Преобразование текста в последовательность индексов"""
        if self.tokenizer is None:
            from tensorflow.keras.preprocessing.text import Tokenizer
            self.tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
            self.tokenizer.fit_on_texts([text])
        
        sequence = self.tokenizer.texts_to_sequences([text])
        padded = tf.keras.preprocessing.sequence.pad_sequences(
            sequence, maxlen=self.max_sequence_len, padding='post'
        )
        return padded
    
    def train_demo(self):
        """Обучение на демонстрационных данных"""
        sample_tasks = [
            "Создать веб-сайт для интернет-магазина с корзиной и оплатой",
            "Разработать мобильное приложение для заказа такси",
            "Создать базу данных для учета сотрудников компании",
            "Настроить CI/CD пайплайн для автоматического деплоя",
            "Разработать API для интеграции с платежной системой",
            "Создать панель администратора для управления пользователями",
            "Настроить мониторинг серверов с алертами",
            "Разработать чат-бота для поддержки клиентов на основе ИИ",
            "Создать систему рекомендаций для интернет-магазина",
            "Написать юнит-тесты для модуля авторизации",
            "Разработать дешборд аналитики с графиками",
            "Настроить резервное копирование базы данных"
        ]
        
        # Тестовые метки
        task_type_labels = [
            [1,0,0,0,0,0,0,0], [0,1,0,0,0,0,0,0], [0,0,1,0,0,0,0,0], [0,0,0,1,0,0,0,0],
            [0,1,0,0,0,0,0,0], [0,0,0,0,1,0,0,0], [0,0,0,1,0,0,0,0], [0,1,0,0,0,0,0,0],
            [0,0,0,0,0,0,1,0], [0,0,0,0,0,1,0,0], [0,0,0,0,0,0,0,1], [0,0,1,0,0,0,0,0]
        ]
        
        complexity_labels = [
            [0,0,1], [0,0,1], [0,1,0], [0,0,1], [0,1,0],
            [0,1,0], [0,0,1], [0,1,0], [0,0,1], [0,1,0],
            [0,1,0], [0,1,0]
        ]
        
        roles_labels = [
            [1,1,0,1,1,1,0], [1,1,1,0,0,1,0], [1,0,0,1,0,0,0], [0,1,1,1,1,0,0],
            [1,1,1,0,1,0,0], [1,1,0,0,1,1,0], [0,1,1,1,1,0,0], [1,1,1,0,0,1,0],
            [1,1,0,1,1,0,1], [1,1,1,0,1,0,0], [1,0,0,0,1,1,1], [0,1,1,1,1,0,0]
        ]
        
        # Создаем начальный токенизатор
        from tensorflow.keras.preprocessing.text import Tokenizer
        self.tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
        self.tokenizer.fit_on_texts(sample_tasks)
        
        # Подготовка данных
        X = []
        for task in sample_tasks:
            seq = self.tokenizer.texts_to_sequences([task])[0]
            padded = tf.keras.preprocessing.sequence.pad_sequences(
                [seq], maxlen=self.max_sequence_len, padding='post'
            )[0]
            X.append(padded)
        
        X = np.array(X)
        
        y_task_type = np.array(task_type_labels)
        y_complexity = np.array(complexity_labels)
        y_roles = np.array(roles_labels)
        
        # Быстрое обучение
        print("Обучение модели на демо-данных...")
        self.model.fit(
            X, 
            {'task_type': y_task_type, 'complexity': y_complexity, 'roles': y_roles},
            epochs=50,
            batch_size=2,
            verbose=0,
            validation_split=0.2
        )
        
        # Сохраняем модель
        self.model.save('task_decomposer_model.h5')
        with open('tokenizer.pkl', 'wb') as f:
            pickle.dump(self.tokenizer, f)
        
        print("Обучение завершено!")
    
    def extract_keywords(self, text):
        """Извлечение ключевых слов из текста задачи"""
        keywords = {
            'tech': [],
            'domain': [],
            'features': [],
            'constraints': []
        }
        
        text_lower = text.lower()
        
        # Технологии
        tech_keywords = {
            'web': ['сайт', 'веб', 'web', 'html', 'css', 'javascript', 'frontend', 'backend'],
            'mobile': ['мобильн', 'mobile', 'ios', 'android', 'react native', 'flutter'],
            'database': ['база данн', 'database', 'sql', 'nosql', 'postgresql', 'mysql', 'mongodb'],
            'cloud': ['облако', 'cloud', 'aws', 'azure', 'gcp', 'деплой'],
            'ai': ['ии', 'ai', 'нейросет', 'machine learning', 'чат бот', 'рекомендац']
        }
        
        # Функциональность
        feature_keywords = {
            'auth': ['авторизац', 'auth', 'логин', 'регистрац', 'пользовател'],
            'payment': ['платеж', 'оплат', 'payment', 'корзин'],
            'api': ['api', 'интеграц', 'endpoint', 'rest'],
            'analytics': ['аналитик', 'analytics', 'отчет', 'график', 'dashboard'],
            'notifications': ['уведомлени', 'notification', 'alert', 'оповещени']
        }
        
        # Извлечение технологий
        for category, words in tech_keywords.items():
            for word in words:
                if word in text_lower:
                    keywords['tech'].append(category)
        
        # Извлечение функционала
        for category, words in feature_keywords.items():
            for word in words:
                if word in text_lower:
                    keywords['features'].append(category)
        
        return keywords
    
    def generate_detailed_subtasks(self, task_description, task_type, keywords):
        """Генерация подробных персонализированных подзадач"""
        task_lower = task_description.lower()
        subtasks = []
        
        # Этап 1: Анализ и планирование
        subtasks.append({
            'name': '📋 Анализ требований и планирование',
            'details': self.generate_analysis_stage(task_description, keywords),
            'duration': '1-2 дня',
            'responsible': 'Аналитик, PM'
        })
        
        # Этап 2: Проектирование
        subtasks.append({
            'name': '🎨 Проектирование и архитектура',
            'details': self.generate_design_stage(task_description, task_type, keywords),
            'duration': '2-3 дня',
            'responsible': 'Архитектор, Дизайнер'
        })
        
        # Этап 3: Разработка основных компонентов
        main_dev_tasks = self.generate_development_stage(task_description, task_type, keywords)
        for task in main_dev_tasks:
            subtasks.append(task)
        
        # Этап 4: Интеграция и тестирование
        subtasks.append({
            'name': '🧪 Интеграция и тестирование',
            'details': self.generate_testing_stage(task_description, keywords),
            'duration': '2-4 дня',
            'responsible': 'Разработчик, Тестировщик'
        })
        
        # Этап 5: Документация и обучение
        subtasks.append({
            'name': '📚 Документация и обучение',
            'details': self.generate_documentation_stage(task_description, keywords),
            'duration': '1-2 дня',
            'responsible': 'Вся команда'
        })
        
        # Этап 6: Деплой и сопровождение
        subtasks.append({
            'name': '🚀 Деплой и пост-релизное сопровождение',
            'details': self.generate_deployment_stage(task_description, keywords),
            'duration': '1-3 дня',
            'responsible': 'DevOps, Разработчик'
        })
        
        return subtasks
    
    def generate_analysis_stage(self, task, keywords):
        """Детали этапа анализа"""
        details = []
        details.append("• Сбор и анализ требований заказчика")
        details.append("• Определение MVP и приоритетов")
        details.append("• Оценка рисков и технических ограничений")
        
        if 'auth' in keywords['features']:
            details.append("• Анализ требований к безопасности и авторизации")
        if 'payment' in keywords['features']:
            details.append("• Анализ платежных систем и требований к безопасности транзакций")
        if 'api' in keywords['features']:
            details.append("• Изучение API сторонних сервисов для интеграции")
        if 'analytics' in keywords['features']:
            details.append("• Определение ключевых метрик для аналитики")
            
        return '\n'.join(details)
    
    def generate_design_stage(self, task, task_type, keywords):
        """Детали этапа проектирования"""
        details = []
        
        if 'web' in task_type.lower() or 'сайт' in task.lower():
            details.append("• Проектирование UI/UX (прототипы, wireframes)")
            details.append("• Дизайн адаптивного интерфейса")
            details.append("• Создание дизайн-системы компонентов")
            if 'payment' in keywords['features']:
                details.append("• Дизайн корзины и процесса оплаты")
                
        elif 'мобильн' in task.lower():
            details.append("• Проектирование мобильного интерфейса (iOS/Android)")
            details.append("• Создание дизайн-системы для мобильной платформы")
            details.append("• Дизайн навигации и жестов")
            
        else:
            details.append("• Проектирование архитектуры решения")
            details.append("• Выбор технологического стека")
            details.append("• Создание ER-диаграмм для базы данных")
        
        if 'api' in keywords['features']:
            details.append("• Проектирование RESTful API (OpenAPI спецификация)")
            details.append("• Разработка архитектуры микросервисов")
            
        if 'analytics' in keywords['features']:
            details.append("• Проектирование аналитической модели данных")
            details.append("• Дизайн дашбордов и отчетов")
            
        return '\n'.join(details)
    
    def generate_development_stage(self, task, task_type, keywords):
        """Генерация подзадач разработки"""
        dev_tasks = []
        
        # Определяем специфичные для задачи подзадачи
        task_lower = task.lower()
        
        if 'чат бот' in task_lower or 'support' in task_lower:
            dev_tasks.append({
                'name': '🤖 Разработка чат-бота',
                'details': "• Настройка NLP модели для понимания запросов\n• Создание базы знаний и ответов\n• Интеграция с мессенджерами/API\n• Обучение модели на диалогах",
                'duration': '3-5 дней',
                'responsible': 'Разработчик, Data Scientist'
            })
            
        if 'дашборд' in task_lower or 'аналитик' in task_lower:
            dev_tasks.append({
                'name': '📊 Разработка дашборда аналитики',
                'details': "• Настройка ETL процессов\n• Создание визуализаций данных\n• Реализация фильтров и дата-пикеров\n• Оптимизация загрузки данных",
                'duration': '3-4 дня',
                'responsible': 'Разработчик, Аналитик'
            })
            
        if 'api' in task_lower:
            dev_tasks.append({
                'name': '🔌 Разработка API',
                'details': "• Создание эндпоинтов для CRUD операций\n• Валидация входных данных\n• Реализация JWT/сессий\n• Документация API (Swagger)",
                'duration': '2-3 дня',
                'responsible': 'Разработчик'
            })
            
        if 'база данн' in task_lower:
            dev_tasks.append({
                'name': '🗄️ Работа с базой данных',
                'details': "• Написание оптимизированных запросов\n• Настройка индексов для быстрого поиска\n• Реализация миграций\n• Настройка connection pool",
                'duration': '2-3 дня',
                'responsible': 'Разработчик'
            })
        
        # Основные задачи разработки
        if not dev_tasks:  # Если нет специфичных, добавляем общие
            dev_tasks.append({
                'name': '💻 Основная разработка',
                'details': f"• Разработка бэкенд компонентов согласно архитектуре\n• Создание пользовательского интерфейса\n• Реализация бизнес-логики\n• Интеграция с внешними сервисами",
                'duration': '4-6 дней',
                'responsible': 'Разработчики'
            })
            
        # Добавляем тестирование в процессе разработки
        dev_tasks.append({
            'name': '✅ Unit и интеграционное тестирование',
            'details': "• Написание unit-тестов для ключевых модулей\n• Создание тестов API\n• Мокинг внешних зависимостей\n• Покрытие кода тестами (минимум 80%)",
            'duration': '2-3 дня',
            'responsible': 'Разработчик'
        })
        
        return dev_tasks
    
    def generate_testing_stage(self, task, keywords):
        """Детали этапа тестирования"""
        details = []
        details.append("• Функциональное тестирование всех сценариев")
        details.append("• Регрессионное тестирование")
        details.append("• Нагрузочное тестирование под нагрузкой")
        
        if 'auth' in keywords['features']:
            details.append("• Тестирование безопасности (OWASP топ-10)")
            details.append("• Проверка восстановления пароля и сессий")
            
        if 'payment' in keywords['features']:
            details.append("• Тестирование платежного шлюза")
            details.append("• Проверка обработки платежных ошибок")
            
        if 'api' in keywords['features']:
            details.append("• Тестирование API (postman/automation)")
            details.append("• Проверка rate limiting и throttling")
            
        details.append("• Проведение пользовательского тестирования (UAT)")
        details.append("• Составление отчета о тестировании")
        
        return '\n'.join(details)
    
    def generate_documentation_stage(self, task, keywords):
        """Детали этапа документации"""
        details = []
        details.append("• Подготовка технической документации")
        details.append("• Написание инструкции для пользователей")
        details.append("• Создание видео-туториалов (при необходимости)")
        
        if 'api' in keywords['features']:
            details.append("• Документирование API эндпоинтов")
            details.append("• Подготовка примеров запросов/ответов")
            
        details.append("• Проведение обучения команды")
        details.append("• Создание wiki страниц проекта")
        
        return '\n'.join(details)
    
    def generate_deployment_stage(self, task, keywords):
        """Детали этапа деплоя"""
        details = []
        details.append("• Настройка CI/CD пайплайна")
        details.append("• Конфигурация production окружения")
        
        if 'cloud' in keywords['tech']:
            details.append("• Настройка облачных сервисов (AWS/GCP/Azure)")
            details.append("• Балансировка нагрузки и авто-скейлинг")
            
        details.append("• Настройка мониторинга и алертов")
        details.append("• Резервное копирование и восстановление")
        details.append("• План отката при проблемах")
        
        return '\n'.join(details)
    
    def decompose_task(self, task_description):
        """Декомпозиция задачи и распределение ролей"""
        # Предобработка
        sequence = self.text_to_sequence(task_description)
        
        # Предсказание
        task_type_pred, complexity_pred, roles_pred = self.model.predict(sequence, verbose=0)
        
        # Определение типа задачи (расширенная классификация)
        task_types = [
            'Веб-разработка', 'Мобильная разработка', 'Базы данных', 
            'DevOps', 'Админ-панель', 'Тестирование', 
            'Data Science/AI', 'Аналитика'
        ]
        task_type = task_types[np.argmax(task_type_pred[0])]
        
        # Определение сложности
        complexities = ['Низкая (1-3 дня)', 'Средняя (3-10 дней)', 'Высокая (10+ дней)']
        complexity = complexities[np.argmax(complexity_pred[0])]
        
        # Определение необходимых ролей
        threshold = 0.3
        needed_roles = []
        for i, prob in enumerate(roles_pred[0]):
            if prob > threshold:
                needed_roles.append(self.roles[i])
        
        if not needed_roles:
            top_indices = np.argsort(roles_pred[0])[-3:]
            needed_roles = [self.roles[i] for i in top_indices]
        
        # Извлечение ключевых слов
        keywords = self.extract_keywords(task_description)
        
        # Генерация подробных подзадач
        subtasks = self.generate_detailed_subtasks(task_description, task_type, keywords)
        
        # Форматирование подзадач для отображения
        formatted_subtasks = []
        for i, subtask in enumerate(subtasks, 1):
            formatted_subtasks.append(f"{i}. {subtask['name']}")
            formatted_subtasks.append(f"   📝 Детали:")
            for line in subtask['details'].split('\n'):
                formatted_subtasks.append(f"      {line}")
            formatted_subtasks.append(f"   ⏱️ Срок: {subtask['duration']}")
            formatted_subtasks.append(f"   👤 Ответственные: {subtask['responsible']}")
            formatted_subtasks.append("")
        
        return {
            'task_type': task_type,
            'complexity': complexity,
            'roles': needed_roles,
            'subtasks': formatted_subtasks,
            'detailed_subtasks': subtasks
        }

class AIAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ИИ Ассистент для декомпозиции задач v2.0")
        self.root.geometry("1000x800")
        self.root.configure(bg='#1e1e1e')
        
        self.ai = TaskDecompositionAI()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Стили
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1e1e1e', foreground='#e0e0e0', font=('Segoe UI', 10))
        style.configure('TButton', background='#0e639c', foreground='white', padding=10)
        style.configure('TLabelframe', background='#1e1e1e', foreground='#e0e0e0')
        style.configure('TLabelframe.Label', background='#1e1e1e', foreground='#e0e0e0', font=('Segoe UI', 10, 'bold'))
        
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#1e1e1e')
        title_frame.pack(fill="x", pady=20)
        
        title_label = tk.Label(
            title_frame, 
            text="🧠 ИИ Ассистент для интеллектуальной декомпозиции задач", 
            font=('Segoe UI', 18, 'bold'),
            bg='#1e1e1e',
            fg='#00bcd4'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Автоматическая детализация и распределение ролей",
            font=('Segoe UI', 11),
            bg='#1e1e1e',
            fg='#888888'
        )
        subtitle_label.pack()
        
        # Фрейм для ввода
        input_frame = ttk.LabelFrame(self.root, text="Введите описание задачи", padding=15)
        input_frame.pack(fill="both", padx=20, pady=10)
        
        self.task_input = scrolledtext.ScrolledText(
            input_frame, 
            height=6, 
            font=('Segoe UI', 11),
            bg='#2d2d2d',
            fg='#e0e0e0',
            insertbackground='#e0e0e0',
            wrap='word'
        )
        self.task_input.pack(fill="both", expand=True)
        
        # Примеры задач
        examples_frame = tk.Frame(input_frame, bg='#1e1e1e')
        examples_frame.pack(fill="x", pady=5)
        
        examples_label = tk.Label(
            examples_frame,
            text="Примеры: ",
            font=('Segoe UI', 9, 'bold'),
            bg='#1e1e1e',
            fg='#00bcd4'
        )
        examples_label.pack(side='left')
        
        examples = [
            "📱 Разработать мобильное приложение для заказа такси с отслеживанием в реальном времени",
            "💳 Создать интернет-магазин с интеграцией платежной системы и личным кабинетом",
            "🤖 Разработать чат-бота с ИИ для технической поддержки",
            "📊 Создать дашборд для аналитики продаж в реальном времени"
        ]
        
        for example in examples:
            btn = tk.Button(
                examples_frame,
                text=example[:40] + "...",
                command=lambda e=example: self.set_example(e),
                font=('Segoe UI', 8),
                bg='#2d2d2d',
                fg='#e0e0e0',
                cursor='hand2',
                relief='flat'
            )
            btn.pack(side='left', padx=5)
        
        # Кнопки действий
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(pady=10)
        
        self.decompose_btn = tk.Button(
            button_frame,
            text="🔍 Декомпозировать задачу",
            command=self.decompose_task,
            font=('Segoe UI', 12, 'bold'),
            bg='#0e639c',
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2',
            relief='raised'
        )
        self.decompose_btn.pack(side="left", padx=10)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑️ Очистить все",
            command=self.clear_all,
            font=('Segoe UI', 11),
            bg='#d32f2f',
            fg='white',
            padx=25,
            pady=10,
            cursor='hand2',
            relief='raised'
        )
        self.clear_btn.pack(side="left", padx=10)
        
        self.export_btn = tk.Button(
            button_frame,
            text="💾 Экспорт результата",
            command=self.export_results,
            font=('Segoe UI', 11),
            bg='#4caf50',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            relief='raised'
        )
        self.export_btn.pack(side="left", padx=10)
        
        # Фрейм для результатов
        results_frame = ttk.LabelFrame(self.root, text="Результаты анализа", padding=15)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Разделитель на две колонки
        paned = ttk.PanedWindow(results_frame, orient='horizontal')
        paned.pack(fill='both', expand=True)
        
        # Левая колонка - общая информация
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Правая колонка - подзадачи
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # Левая колонка содержимое
        info_panel = ttk.LabelFrame(left_frame, text="📊 Общая информация", padding=10)
        info_panel.pack(fill="both", expand=True, pady=5)
        
        self.type_label = tk.Label(
            info_panel,
            text="Тип задачи: -",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e1e1e',
            fg='#00bcd4',
            anchor='w'
        )
        self.type_label.pack(fill="x", pady=5)
        
        self.complexity_label = tk.Label(
            info_panel,
            text="Сложность: -",
            font=('Segoe UI', 11, 'bold'),
            bg='#1e1e1e',
            fg='#ff9800',
            anchor='w'
        )
        self.complexity_label.pack(fill="x", pady=5)
        
        # Роли
        roles_panel = ttk.LabelFrame(left_frame, text="👥 Необходимые роли", padding=10)
        roles_panel.pack(fill="both", expand=True, pady=5)
        
        self.roles_text = tk.Text(
            roles_panel,
            height=8,
            font=('Segoe UI', 10),
            bg='#2d2d2d',
            fg='#e0e0e0',
            wrap='word'
        )
        roles_scroll = ttk.Scrollbar(roles_panel, orient="vertical", command=self.roles_text.yview)
        self.roles_text.configure(yscrollcommand=roles_scroll.set)
        self.roles_text.pack(side="left", fill="both", expand=True)
        roles_scroll.pack(side="right", fill="y")
        
        # Правая колонка - подзадачи
        subtasks_panel = ttk.LabelFrame(right_frame, text="📋 Детальная декомпозиция подзадач", padding=10)
        subtasks_panel.pack(fill="both", expand=True)
        
        self.subtasks_text = scrolledtext.ScrolledText(
            subtasks_panel,
            font=('Segoe UI', 10),
            bg='#2d2d2d',
            fg='#e0e0e0',
            wrap='word'
        )
        self.subtasks_text.pack(fill="both", expand=True)
        
        # Статус бар
        self.status_bar = tk.Label(
            self.root,
            text="✅ Готов к работе | ИИ модель загружена",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#2d2d2d',
            fg='#888888',
            font=('Segoe UI', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Словарь для хранения текущих результатов
        self.current_result = None
    
    def set_example(self, example):
        self.task_input.delete("1.0", tk.END)
        self.task_input.insert("1.0", example)
        self.status_bar.config(text="Пример задачи загружен")
    
    def decompose_task(self):
        task = self.task_input.get("1.0", tk.END).strip()
        
        if not task:
            messagebox.showwarning("Внимание", "Пожалуйста, введите описание задачи")
            return
        
        # Отключаем кнопку на время обработки
        self.decompose_btn.config(state='disabled', text='🔄 Анализирую задачу...')
        self.status_bar.config(text="🧠 ИИ анализирует задачу и генерирует персонализированные подзадачи...")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self.process_task, args=(task,))
        thread.daemon = True
        thread.start()
    
    def process_task(self, task):
        try:
            result = self.ai.decompose_task(task)
            self.current_result = result
            
            # Обновляем UI в главном потоке
            self.root.after(0, self.update_results, result)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def update_results(self, result):
        # Обновляем тип и сложность
        self.type_label.config(text=f"📌 Тип задачи: {result['task_type']}")
        self.complexity_label.config(text=f"⚡ Сложность: {result['complexity']}")
        
        # Обновляем роли
        self.roles_text.delete("1.0", tk.END)
        roles_display = ""
        for role in result['roles']:
            role_icons = {
                'Аналитик': '📊', 'Разработчик': '💻', 'Тестировщик': '🐛',
                'DevOps': '🔧', 'Project Manager': '📋', 'Дизайнер': '🎨',
                'Data Scientist': '📈'
            }
            icon = role_icons.get(role, '👤')
            roles_display += f"{icon} {role}\n\n"
        self.roles_text.insert("1.0", roles_display)
        
        # Обновляем подзадачи
        self.subtasks_text.delete("1.0", tk.END)
        subtasks_display = ""
        for line in result['subtasks']:
            if line.startswith("   "):
                subtasks_display += f"{line}\n"
            else:
                subtasks_display += f"\n{line}\n"
        self.subtasks_text.insert("1.0", subtasks_display)
        
        # Обновляем статус
        total_days = sum([int(re.findall(r'\d+', st['duration'])[0]) if re.findall(r'\d+', st['duration']) else 0 
                         for st in result['detailed_subtasks']])
        self.status_bar.config(text=f"✅ Анализ завершен! Общая длительность проекта: {total_days} дней")
        self.decompose_btn.config(state='normal', text='🔍 Декомпозировать задачу')
    
    def show_error(self, error):
        messagebox.showerror("Ошибка", f"Произошла ошибка при анализе:\n{error}")
        self.status_bar.config(text="❌ Ошибка при анализе задачи")
        self.decompose_btn.config(state='normal', text='🔍 Декомпозировать задачу')
    
    def export_results(self):
        if not self.current_result:
            messagebox.showwarning("Внимание", "Нет результатов для экспорта")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Сохранить результаты"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ИИ АССИСТЕНТ ДЛЯ ДЕКОМПОЗИЦИИ ЗАДАЧ\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"ЗАДАЧА:\n{self.task_input.get('1.0', tk.END).strip()}\n\n")
                f.write(f"ТИП ЗАДАЧИ: {self.current_result['task_type']}\n")
                f.write(f"СЛОЖНОСТЬ: {self.current_result['complexity']}\n\n")
                f.write("НЕОБХОДИМЫЕ РОЛИ:\n")
                for role in self.current_result['roles']:
                    f.write(f"  - {role}\n")
                f.write("\n" + "=" * 80 + "\n\n")
                f.write("ДЕТАЛЬНАЯ ДЕКОМПОЗИЦИЯ ПОДЗАДАЧ:\n\n")
                
                for line in self.current_result['subtasks']:
                    if line and not line.startswith("   "):
                        f.write(f"\n{line}\n")
                    else:
                        f.write(f"{line}\n")
            
            messagebox.showinfo("Успех", f"Результаты сохранены в:\n{filename}")
    
    def clear_all(self):
        self.task_input.delete("1.0", tk.END)
        self.roles_text.delete("1.0", tk.END)
        self.subtasks_text.delete("1.0", tk.END)
        self.type_label.config(text="Тип задачи: -")
        self.complexity_label.config(text="Сложность: -")
        self.current_result = None
        self.status_bar.config(text="Все поля очищены | Готов к новой задаче")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = AIAssistantApp(root)
    
    # Центрируем окно
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()