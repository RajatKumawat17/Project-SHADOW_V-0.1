from rag.embeddings import EmbeddingEngine
import re
import networkx as nx

class RAGRetriever:
    def __init__(self):
        """Initialize the RAG retriever with the embedding engine"""
        self.embedding_engine = EmbeddingEngine()
        self.code_words = self._extract_code_words()
        self.knowledge_graph = self._build_knowledge_graph()
    
    def _extract_code_words(self):
        """Extract code words from documents for special handling"""
        code_words = {}
        
        for chunk in self.embedding_engine.chunks:
            text = chunk['text'].lower()
            
            # Extract potential code words/phrases
            patterns = [
                r'"([^"]+)"',                  # Text in quotes
                r'operation ([a-z\s]+)',       # Operations
                r'protocol ([a-z\s]+)',        # Protocols
                r'project ([a-z\s]+)',         # Projects
                r'omega ([a-z\s]+)',           # Omega related terms
                r'safehouse ([a-z0-9\-]+)'     # Safehouses
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if len(match.split()) <= 3:  # Limit to short phrases
                        code_words[match.strip()] = chunk
        
        return code_words
    
    def _build_knowledge_graph(self):
        """Build a knowledge graph connecting related information"""
        G = nx.Graph()
        
        # Add nodes for each chunk
        for i, chunk in enumerate(self.embedding_engine.chunks):
            G.add_node(i, **chunk)
        
        # Connect related chunks based on keywords and references
        for i, chunk_i in enumerate(self.embedding_engine.chunks):
            text_i = chunk_i['text'].lower()
            
            for j, chunk_j in enumerate(self.embedding_engine.chunks):
                if i == j:
                    continue
                    
                text_j = chunk_j['text'].lower()
                
                # Check for shared code words
                for code_word in self.code_words:
                    if code_word in text_i and code_word in text_j:
                        G.add_edge(i, j, relation=f"shared_{code_word}")
                
                # Check for procedural relationships
                if ('step 1' in text_i and 'step 2' in text_j) or \
                   ('rule' in text_i and 'rule' in text_j):
                    G.add_edge(i, j, relation="procedural_sequence")
        
        return G
    
    def retrieve(self, query):
        """Retrieve relevant documents based on the query"""
        # First, check if the query contains code words
        code_word_matches = []
        for code_word, chunk in self.code_words.items():
            if code_word.lower() in query.lower():
                code_word_matches.append(chunk)
        
        # Next, get vector similarity matches
        vector_matches = self.embedding_engine.get_similar_chunks(query, top_k=5)
        
        # Combine results, prioritizing code word matches
        combined_matches = code_word_matches.copy()
        
        for match in vector_matches:
            # Check if this match is already in combined_matches
            if match not in combined_matches:
                combined_matches.append(match)
        
        # If we have matches, expand with graph traversal to get related content
        if combined_matches and len(combined_matches) > 0:
            expanded_matches = self._expand_with_graph_traversal(combined_matches)
            return expanded_matches[:7]  # Limit to top results
        
        return combined_matches
    
    def _expand_with_graph_traversal(self, initial_matches, max_depth=1):
        """Use graph traversal to find related information"""
        expanded_matches = initial_matches.copy()
        indices_in_expanded = [self.embedding_engine.chunks.index(match) 
                               if match in self.embedding_engine.chunks 
                               else -1 for match in initial_matches]
        indices_in_expanded = [idx for idx in indices_in_expanded if idx != -1]
        
        # For each matching chunk, find related chunks in the knowledge graph
        for idx in indices_in_expanded:
            if idx in self.knowledge_graph:
                # Get neighbors up to max_depth
                neighbors = set()
                current = {idx}
                
                for _ in range(max_depth):
                    next_nodes = set()
                    for node in current:
                        next_nodes.update(self.knowledge_graph.neighbors(node))
                    neighbors.update(next_nodes)
                    current = next_nodes
                
                # Add related chunks to expanded_matches
                for neighbor in neighbors:
                    if neighbor not in indices_in_expanded:
                        related_chunk = self.embedding_engine.chunks[neighbor]
                        if related_chunk not in expanded_matches:
                            expanded_matches.append(related_chunk)
        
        # Sort expanded matches by relevance (assuming initial matches are most relevant)
        return sorted(expanded_matches, 
                      key=lambda x: -1 if x in initial_matches else expanded_matches.index(x))