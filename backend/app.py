from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from rag.retriever import RAGRetriever
from rag.security import SecurityProtocol
from rag.formatter import ResponseFormatter

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the RAG system
retriever = RAGRetriever()
security = SecurityProtocol()
formatter = ResponseFormatter()

@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query', '')
    agent_level = int(data.get('agentLevel', 1))
    
    # Check if the query is valid
    if not query:
        return jsonify({
            'status': 'error',
            'message': 'Query cannot be empty'
        }), 400
    
    # Check if agent level is valid (1-5)
    if agent_level not in range(1, 6):
        return jsonify({
            'status': 'error',
            'message': 'Invalid agent level'
        }), 400
    
    try:
        # Retrieve relevant documents based on the query
        retrieved_docs = retriever.retrieve(query)
        
        # Apply security protocols
        access_result = security.check_access(retrieved_docs, agent_level, query)
        
        if access_result['denied']:
            return jsonify({
                'status': 'denied',
                'message': access_result['message']
            }), 403
        
        if not retrieved_docs:
            return jsonify({
                'status': 'not_found',
                'message': 'Oops!! No matching data found.'
            }), 404
        
        # Format the response based on agent level and query
        formatted_response = formatter.format_response(
            query=query,
            agent_level=agent_level,
            retrieved_docs=retrieved_docs
        )
        
        return jsonify({
            'status': 'success',
            'response': formatted_response,
            'sources': [doc['source'] for doc in retrieved_docs]
        })
    
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An internal error occurred'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)