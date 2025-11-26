import numpy as np
import faiss
import json
import os
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import config
import time
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class RetrievalSystem:
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = config.SYSTEM_CONFIG['retrieval']['model']
        
        print("🔧 Загрузка модели для эмбеддингов...")
        self.model = self._load_model_with_retry(model_name)
        
        self.index = None
        self.chunks = []
        self.metadata = []

    def _load_model_with_retry(self, model_name, max_retries=3, retry_delay=10):
        for attempt in range(max_retries):
            try:
                print(f"Попытка {attempt + 1}/{max_retries} загрузки модели...")
                session = requests.Session()
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                model = SentenceTransformer(model_name)
                print("✅ Модель успешно загружена")
                return model
                
            except requests.exceptions.ChunkedEncodingError as e:
                print(f"❌ Обрыв соединения (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"🕒 Повтор через {retry_delay} сек...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
            except Exception as e:
                print(f"❌ Ошибка загрузки (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise e
        raise Exception("Не удалось загрузить модель")

    def build_index(self, chunks, index_path):
        print("🔨 Создание эмбеддингов...")
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype(np.float32))
        
        self.chunks = chunks
        self.metadata = chunks
        
        os.makedirs(index_path, exist_ok=True)
        faiss.write_index(self.index, f"{index_path}/faiss.index")
        with open(f"{index_path}/metadata.json", 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Индекс построен. Чанков: {len(chunks)}")

    def load_index(self, index_path):
        self.index = faiss.read_index(f"{index_path}/faiss.index")
        with open(f"{index_path}/metadata.json", 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        print(f"✅ Индекс загружен. Чанков: {len(self.metadata)}")

    def search(self, query, top_k=None, similarity_threshold=None):
        if top_k is None:
            top_k = config.SYSTEM_CONFIG['retrieval']['top_k']          # 8
        if similarity_threshold is None:
            similarity_threshold = config.SYSTEM_CONFIG['retrieval']['similarity_threshold']  # 0.5

        print(f"🔍 Поиск: top_k={top_k}, threshold={similarity_threshold}")

        if self.index is None:
            raise ValueError("Индекс не загружен")
        
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Ищем в 3 раза больше кандидатов, чтобы после фильтра осталось достаточно
        search_k = min(top_k * 3, len(self.metadata))
        scores, indices = self.index.search(query_embedding.astype(np.float32), search_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= len(self.metadata):
                continue
            if score >= similarity_threshold:
                results.append({
                    'text': self.metadata[idx]['text'],
                    'source': self.metadata[idx]['source'],
                    'page': self.metadata[idx].get('page', 1),
                    'similarity': float(score)
                })
                if len(results) >= top_k:
                    break

        print(f"✅ Найдено релевантных чанков: {len(results)}")
        return results[:top_k]

    def calculate_confidence(self, query, context_chunks):
        if not context_chunks:
            return 0.0
        
        avg_similarity = sum(chunk['similarity'] for chunk in context_chunks) / len(context_chunks)
        
        context_text = " ".join([chunk['text'] for chunk in context_chunks])
        query_emb = self.model.encode([query])
        context_emb = self.model.encode([context_text])
        cross_sim = cosine_similarity(query_emb, context_emb)[0][0]
        
        confidence = (avg_similarity + cross_sim) / 2
        return round(confidence, 4)