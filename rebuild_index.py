import os
from document_processor import DocumentProcessor
from retrieval_system import RetrievalSystem
import config

def rebuild_index():
    """Перестроение векторного индекса с улучшенными настройками"""
    print("🔄 Перестроение векторного индекса с улучшенными настройками...")
    
    # Создаем процессор с улучшенными настройками
    processor = DocumentProcessor(
        chunk_size=800,   # Меньшие чанки для лучшего качества
        chunk_overlap=150
    )
    
    # Обрабатываем документы заново
    chunks = processor.process_documents()
    
    if chunks:
        print("🔨 Построение улучшенного векторного индекса...")
        retrieval = RetrievalSystem()
        retrieval.build_index(chunks, config.SYSTEM_CONFIG['paths']['vector_db'])
        print("✅ Улучшенный индекс успешно построен!")
        print(f"📊 Создано {len(chunks)} чанков")
    else:
        print("❌ Не удалось обработать документы")

if __name__ == "__main__":
    rebuild_index()