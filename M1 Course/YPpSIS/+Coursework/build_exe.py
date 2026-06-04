#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Единый скрипт для сборки AI Task Decomposer в EXE файл
"""

import os
import sys
import subprocess
import shutil

# ============================================================
# НАСТРОЙКИ - УКАЖИТЕ ПУТЬ К ВАШЕЙ ПРОГРАММЕ ЗДЕСЬ
# ============================================================

# Укажите имя вашего файла (измените на нужное)
SOURCE_FILE = "C:/Users/dimaa/source/StudiesHUB/M1 Course/YPpSIS/Coursework/IAAssistant.py"  # ← ИЗМЕНИТЕ НА ИМЯ ВАШЕГО ФАЙЛА

# ============================================================

def check_source_file():
    """Проверка существования исходного файла"""
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Ошибка: Файл {SOURCE_FILE} не найден!")
        print(f"\n📁 Текущая папка: {os.getcwd()}")
        print("\n📄 Доступные Python файлы:")
        for file in os.listdir('.'):
            if file.endswith('.py'):
                print(f"  - {file}")
        return False
    print(f"✅ Найден файл: {SOURCE_FILE}")
    return True

def install_requirements():
    """Установка необходимых пакетов"""
    packages = ['numpy', 'openpyxl', 'pillow']
    
    print("\n📦 Проверка необходимых пакетов...")
    for package in packages:
        try:
            __import__(package)
            print(f"  ✓ {package} уже установлен")
        except ImportError:
            print(f"  ⬇ Установка {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ Все пакеты установлены\n")

def create_simple_icon():
    """Создание простой иконки"""
    try:
        from PIL import Image, ImageDraw
        
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Фон
        draw.rectangle([0, 0, size, size], fill=(0, 102, 204))
        
        # Круг
        draw.ellipse([50, 50, 206, 206], fill=(255, 255, 255, 200))
        
        # Текст "AI"
        draw.text((95, 90), "AI", fill=(0, 102, 204))
        
        # Шестеренка
        draw.rectangle([180, 180, 220, 220], fill=(255, 255, 255))
        
        img.save("icon.ico", format="ICO", sizes=[(256, 256)])
        print("  ✓ Иконка создана: icon.ico")
        return True
    except ImportError:
        print("  ⚠ Pillow не установлен, пропускаем создание иконки")
        return False
    except Exception as e:
        print(f"  ⚠ Не удалось создать иконку: {e}")
        return False

def build_exe():
    """Сборка EXE файла"""
    print("\n🔨 Начинаем сборку EXE файла...")
    print("⏱ Это может занять 2-5 минут...\n")
    
    # Сначала удаляем старые файлы сборки
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Правильная команда для PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",  # Запускаем PyInstaller как модуль
        '--onefile',  # Один EXE файл
        '--windowed',  # Без консольного окна
        '--name', 'AI_Task_Decomposer',  # Имя выходного файла
        '--noconfirm',  # Не спрашивать подтверждение
        '--clean',  # Очистить временные файлы
    ]
    
    # Добавляем иконку если есть
    if os.path.exists('icon.ico'):
        cmd.extend(['--icon', 'icon.ico'])
    
    # Добавляем скрытые импорты
    cmd.extend([
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'numpy',
        '--hidden-import', 'PIL',
        '--hidden-import', 'PIL._tkinter_finder',
        '--collect-all', 'openpyxl',
    ])
    
    # Добавляем исходный файл
    cmd.append(SOURCE_FILE)
    
    print(f"🔧 Команда: python -m PyInstaller --onefile --windowed --name AI_Task_Decomposer {SOURCE_FILE}")
    print("\n⏳ Пожалуйста, подождите...\n")
    
    try:
        # Запускаем PyInstaller
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n" + "="*50)
            print("  ✅ СБОРКА УСПЕШНО ЗАВЕРШЕНА!")
            print("="*50)
            
            exe_path = os.path.abspath('dist/AI_Task_Decomposer.exe')
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"\n📁 Файл: {exe_path}")
                print(f"📊 Размер: {size:.2f} MB")
                print("\n🚀 Для запуска дважды кликните по файлу")
                
                # Копируем в текущую папку
                shutil.copy2(exe_path, 'AI_Task_Decomposer.exe')
                print(f"\n📋 Также создана копия: AI_Task_Decomposer.exe")
                return True
            else:
                # Проверяем другие возможные имена
                alt_path = os.path.abspath(f'dist/{SOURCE_FILE.replace(".py", ".exe")}')
                if os.path.exists(alt_path):
                    print(f"\n📁 Файл найден: {alt_path}")
                    shutil.copy2(alt_path, 'AI_Task_Decomposer.exe')
                    return True
                else:
                    print("\n❌ EXE файл не найден после сборки!")
                    return False
        else:
            print("\n❌ Ошибка при сборке!")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False

def main():
    """Главная функция"""
    print("="*60)
    print("  🚀 AI TASK DECOMPOSER - СОЗДАНИЕ EXE ФАЙЛА")
    print("="*60)
    print()
    
    # Проверяем исходный файл
    if not check_source_file():
        print("\n💡 Укажите правильное имя файла в переменной SOURCE_FILE")
        print(f"   Сейчас установлено: SOURCE_FILE = '{SOURCE_FILE}'")
        input("\nНажмите Enter для выхода...")
        return
    
    # Устанавливаем зависимости
    install_requirements()
    
    # Создаем иконку
    print("\n🎨 Создание иконки...")
    create_simple_icon()
    
    # Собираем EXE
    success = build_exe()
    
    if success:
        print("\n" + "="*60)
        print("  🎉 ПОЗДРАВЛЯЮ! EXE ФАЙЛ УСПЕШНО СОЗДАН!")
        print("="*60)
        print("\n📌 Файлы:")
        print("   - dist/AI_Task_Decomposer.exe")
        print("   - AI_Task_Decomposer.exe (копия в текущей папке)")
    else:
        print("\n❌ К сожалению, не удалось создать EXE файл")
        print("\n💡 Попробуйте запустить вручную:")
        print(f"   pyinstaller --onefile --windowed --name AI_Task_Decomposer {SOURCE_FILE}")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()