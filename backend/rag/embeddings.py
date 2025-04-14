import os
import pickle
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from charset_normalizer import from_path  # Automatically detects encoding

class EmbeddingEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the embedding engine with a pre-trained model"""
        self.model = SentenceTransformer(model_name)
        self.embeddings_dir = 'data/embeddings'
        self.documents_dir = 'data/documents'

        os.makedirs(self.embeddings_dir, exist_ok=True)
        os.makedirs(self.documents_dir, exist_ok=True)

        self.document_embeddings = self._load_embeddings()
        self.chunks = self._load_chunks()

        if not self.document_embeddings or not self.chunks:
            self.process_documents()

    def _load_embeddings(self):
        path = os.path.join(self.embeddings_dir, 'embeddings.pkl')
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading embeddings: {e}")
        return {}

    def _load_chunks(self):
        path = os.path.join(self.embeddings_dir, 'chunks.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading chunks: {e}")
        return []

    def process_documents(self):
        self.chunks = []
        self.document_embeddings = {}

        for filename in os.listdir(self.documents_dir):
            if filename.lower().endswith(('.txt', '.md', '.docx')):
                file_path = os.path.join(self.documents_dir, filename)

                try:
                    # Auto-detect encoding
                    raw_text = from_path(file_path).best().read()
                except Exception as e:
                    print(f"[ERROR] Could not read {filename}: {e}")
                    continue

                chunks = self._chunk_document(raw_text, filename)
                self.chunks.extend(chunks)

        for i, chunk in enumerate(self.chunks):
            try:
                embedding = self.model.encode(chunk['text'])
                self.document_embeddings[i] = embedding
            except Exception as e:
                print(f"Error embedding chunk {i}: {e}")

        # Save results
        try:
            with open(os.path.join(self.embeddings_dir, 'embeddings.pkl'), 'wb') as f:
                pickle.dump(self.document_embeddings, f)

            with open(os.path.join(self.embeddings_dir, 'chunks.json'), 'w', encoding='utf-8') as f:
                json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving embeddings/chunks: {e}")

    def _chunk_document(self, text, source, chunk_size=200, overlap=50):
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if chunk_words:
                chunk_text = ' '.join(chunk_words)
                chunk = {
                    'text': chunk_text,
                    'source': source,
                    'index': len(chunks),
                    'start_idx': i,
                    'classified': self._is_classified(chunk_text),
                    'clearance_level': self._extract_clearance_level(chunk_text)
                }
                chunks.append(chunk)

        return chunks

    def _is_classified(self, text):
        keywords = ['classified', 'secret', 'confidential', 'level', 'clearance']
        return any(keyword in text.lower() for keyword in keywords)

    def _extract_clearance_level(self, text):
        text = text.lower()
        for level in range(5, 1, -1):
            if f'level {level}' in text or f'level-{level}' in text:
                return level
        return 1

    def get_similar_chunks(self, query, top_k=5):
        query_embedding = self.model.encode(query)
        similarities = []

        for i, embedding in self.document_embeddings.items():
            try:
                similarity = cosine_similarity([query_embedding], [embedding])[0][0]
                similarities.append((i, similarity))
            except Exception as e:
                print(f"Error computing similarity for chunk {i}: {e}")

        similarities.sort(key=lambda x: x[1], reverse=True)

        top_chunks = []
        for i, similarity in similarities[:top_k]:
            chunk = self.chunks[i].copy()
            chunk['similarity'] = float(similarity)
            top_chunks.append(chunk)

        return top_chunks
