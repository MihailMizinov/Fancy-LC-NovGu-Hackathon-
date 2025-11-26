import os
import subprocess
import sys
import platform

def setup_environment():
    """Автоматическая настройка среды"""
    print("🛠️ Настройка RAG системы для компании 'Сплав'...")
    
    # Создание директорий
    directories = [
        './data/documents',
        './data/vector_db', 
        './data/models',
        './logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Создана директория: {directory}")
    
    print("\n📝 Пожалуйста, поместите ваши документы в папку:")
    print("  ./data/documents/")
    print("\n📄 Поддерживаемые форматы: PDF, DOCX, TXT")
    
    # Информация о системе
    print(f"\n💻 Информация о системе:")
    print(f"  ОС: {platform.system()} {platform.release()}")
    print(f"  Python: {sys.version}")
    print(f"  Архитектура: {platform.architecture()[0]}")
    
    # Проверка установки зависимостей
    print("\n📦 Установка зависимостей...")
    
    # Сначала пробуем установить torch отдельно, так как он может требовать специфичные версии
    try:
        print("🔧 Установка PyTorch...")
        # Для Windows с Python 3.12 используем совместимую версию
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "torch>=2.1.0", "torchvision", "torchaudio", 
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])
        print("✅ PyTorch успешно установлен")
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка установки PyTorch. Пробуем альтернативный способ...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "torch>=2.1.0", "torchvision", "torchaudio"
            ])
            print("✅ PyTorch успешно установлен (альтернативный способ)")
        except subprocess.CalledProcessError:
            print("❌ Критическая ошибка: Не удалось установить PyTorch")
            print("📚 Решение: Установите PyTorch вручную с официального сайта")
            return False
    
    # Установка остальных зависимостей
    try:
        print("🔧 Установка остальных зависимостей...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Все зависимости успешно установлены")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        print("🔄 Пробуем альтернативный метод установки...")
        
        # Альтернативный метод: устанавливаем пакеты по одному
        packages = [
            "transformers>=4.35.0",
            "sentence-transformers>=2.2.2", 
            "faiss-cpu>=1.7.4",
            "PyPDF2>=3.0.1",
            "python-docx>=0.8.11",
            "numpy>=1.24.0",
            "scikit-learn>=1.3.0",
            "accelerate>=0.24.0"
        ]
        
        for package in packages:
            try:
                print(f"🔧 Установка {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} установлен")
            except subprocess.CalledProcessError:
                print(f"⚠️ Не удалось установить {package}, продолжаем...")
    
    print("\n🎉 Настройка завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Поместите документы в ./data/documents/")
    print("2. Запустите: python document_processor.py")
    print("3. Запустите: python rag_system.py")
    print("\n💬 Для тестирования просто запустите python rag_system.py")
    
    return True

if __name__ == "__main__":
    setup_environment()