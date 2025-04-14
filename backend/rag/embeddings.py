import os
import pickle
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the embedding engine with a pre-trained model"""
        self.model = SentenceTransformer(model_name)
        self.embeddings_dir = 'data/embeddings'
        self.documents_dir = 'data/documents'
        
        # Create directories if they don't exist
        os.makedirs(self.embeddings_dir, exist_ok=True)
        os.makedirs(self.documents_dir, exist_ok=True)
        
        # Load or initialize embeddings
        self.document_embeddings = self._load_embeddings()
        self.chunks = self._load_chunks()
        
        # If no embeddings found, process the documents
        if not self.document_embeddings or not self.chunks:
            self.process_documents()
    
    def _load_embeddings(self):
        """Load pre-computed embeddings from disk"""
        embedding_path = os.path.join(self.embeddings_dir, 'embeddings.pkl')
        if os.path.exists(embedding_path):
            with open(embedding_path, 'rb') as f:
                return pickle.load(f)
        return {}
    
    def _load_chunks(self):
        """Load document chunks from disk"""
        chunks_path = os.path.join(self.embeddings_dir, 'chunks.json')
        if os.path.exists(chunks_path):
            with open(chunks_path, 'r') as f:
                return json.load(f)
        return []
    
    def process_documents(self):
        """Process all documents in the documents directory"""
        self.chunks = []
        document_texts = {}
        
        # Read and chunk all documents
        for filename in os.listdir(self.documents_dir):
            if filename.endswith('.txt') or filename.endswith('.md') or filename.endswith('.docx'):
                file_path = os.path.join(self.documents_dir, filename)
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    document_text = f.read()
                
                document_texts[filename] = document_text
                
                # Chunk the document
                chunks = self._chunk_document(document_text, filename)
                self.chunks.extend(chunks)
        
        # Generate embeddings for all chunks
        self.document_embeddings = {}
        
        for i, chunk in enumerate(self.chunks):
            text = chunk['text']
            embedding = self.model.encode(text)
            self.document_embeddings[i] = embedding
        
        # Save embeddings and chunks
        with open(os.path.join(self.embeddings_dir, 'embeddings.pkl'), 'wb') as f:
            pickle.dump(self.document_embeddings, f)
        
        with open(os.path.join(self.embeddings_dir, 'chunks.json'), 'w') as f:
            json.dump(self.chunks, f)
    
    def _chunk_document(self, text, source, chunk_size=200, overlap=50):
        """Split document into overlapping chunks"""
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
        """Determine if text contains classified information"""
        keywords = ['classified', 'secret', 'confidential', 'level', 'clearance']
        return any(keyword in text.lower() for keyword in keywords)
    
    def _extract_clearance_level(self, text):
        """Extract the required clearance level from text"""
        # Default to level 1 if no specific level is found
        level = 1
        
        # Look for level indicators in the text
        if 'level 5' in text.lower() or 'level-5' in text.lower():
            level = 5
        elif 'level 4' in text.lower() or 'level-4' in text.lower():
            level = 4
        elif 'level 3' in text.lower() or 'level-3' in text.lower():
            level = 3
        elif 'level 2' in text.lower() or 'level-2' in text.lower():
            level = 2
        
        return level
    
    def get_similar_chunks(self, query, top_k=5):
        """Find chunks most similar to the query"""
        query_embedding = self.model.encode(query)
        
        # Calculate similarities between the query and all document chunks
        similarities = []
        for i, embedding in self.document_embeddings.items():
            similarity = cosine_similarity([query_embedding], [embedding])[0][0]
            similarities.append((i, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get the top k chunks
        top_chunks = []
        for i, similarity in similarities[:top_k]:
            chunk = self.chunks[i].copy()
            chunk['similarity'] = float(similarity)
            top_chunks.append(chunk)
        
        return top_chunks