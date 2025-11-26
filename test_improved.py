from rag_system import RAGSystem

def test_improved_system():
    print("🧪 Тестирование улучшенной системы...")
    
    system = RAGSystem()
    
    if not system.initialize_system():
        print("❌ Не удалось инициализировать систему")
        return
    
    # Тестовые вопросы
    test_questions = [
        "Как полностью называется документ с обозначением РБ-089-14?",
        "Какие требования к сварке?",
        "Что такое НП-045-18?",
        "сколько пипися попа",  # Глупый вопрос для проверки отказа
        "дпопо"  # Бессмысленный вопрос
    ]
    
    for question in test_questions:
        print(f"\n🎯 Вопрос: {question}")
        answer, sources, confidence = system.process_question(question)
        print(f"💡 Ответ: {answer}")
        print(f"📊 Уверенность: {confidence:.3f}")
        
        if sources:
            print(f"📚 Источники: {len(sources)}")
            for source in sources[:2]:
                print(f"   - {os.path.basename(source['source'])} (схожесть: {source['similarity']:.3f})")
        else:
            print("❌ Источники не найдены")
        
        print("-" * 50)

if __name__ == "__main__":
    test_improved_system()