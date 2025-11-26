import os
import subprocess
import sys

def manual_setup():
    """Ручная настройка для случаев, когда автоматическая не работает"""
    print("🛠️ Ручная настройка RAG системы...")
    
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
    
    print("\n📋 РУКОВОДСТВО ПО УСТАНОВКЕ:")
    print("="*50)
    print("1. Установите зависимости вручную:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
    print("   pip install transformers sentence-transformers faiss-cpu")
    print("   pip install PyPDF2 python-docx numpy scikit-learn accelerate")
    print("\n2. Поместите документы в папку: ./data/documents/")
    print("3. Запустите: python document_processor.py")
    print("4. Запустите: python rag_system.py")
    print("="*50)
    
    # Проверка Python
    print(f"\n💻 Ваша версия Python: {sys.version}")
    
    input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    manual_setup()