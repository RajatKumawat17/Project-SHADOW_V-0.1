import re

class SecurityProtocol:
    def __init__(self):
        """Initialize security protocols for RAG system"""
        # Define keywords that indicate classified information
        self.sensitive_keywords = [
            'classified', 'secret', 'confidential', 'top secret',
            'level 5', 'level 4', 'level 3', 'level-5', 'level-4', 'level-3',
            'restricted', 'Eyes Only', 'Clearance Required'
        ]
        
        # Special protocols requiring specific clearance
        self.special_protocols = {
            'project eclipse': 5,
            'protocol zeta': 4,
            'operation void': 5,
            'facility x-17': 4,
            'omega wave': 5,
            'shadow step': 3,
            'cipher seed': 4,
            'protocol red mist': 3
        }
    
    def check_access(self, retrieved_docs, agent_level, query):
        """Check if agent has sufficient clearance for the retrieved information"""
        result = {'denied': False, 'message': ''}
        
        # Check for special protocols in the query
        for protocol, required_level in self.special_protocols.items():
            if protocol.lower() in query.lower() and agent_level < required_level:
                result['denied'] = True
                result['message'] = f"Access Denied – Clearance Insufficient. Level {required_level} required."
                return result
        
        # Check the clearance level required for each document
        for doc in retrieved_docs:
            # Extract the highest clearance level mentioned in the document
            required_level = self._extract_required_level(doc)
            
            # If agent's level is lower than required
            if required_level > agent_level:
                result['denied'] = True
                result['message'] = f"Access Denied – Clearance Insufficient. Level {required_level} required."
                return result
        
        return result
    
    def _extract_required_level(self, doc):
        """Extract the required clearance level from a document"""
        # Start with minimum clearance level
        max_level = 1
        
        # Check for explicit level requirements
        text = doc['text'].lower()
        
        # Look for patterns like "Level X" or "Level-X"
        level_patterns = [
            r'level\s*(\d+)',
            r'level-(\d+)',
            r'clearance\s*level\s*(\d+)'
        ]
        
        for pattern in level_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    level = int(match)
                    max_level = max(max_level, level)
                except ValueError:
                    continue
        
        # Check for sensitive keywords indicating high clearance
        if any(keyword in text for keyword in ['top secret', 'level 5', 'level-5']):
            max_level = max(max_level, 5)
        elif any(keyword in text for keyword in ['secret', 'level 4', 'level-4']):
            max_level = max(max_level, 4)
        elif any(keyword in text for keyword in ['confidential', 'level 3', 'level-3']):
            max_level = max(max_level, 3)
        elif any(keyword in text for keyword in ['restricted', 'level 2', 'level-2']):
            max_level = max(max_level, 2)
        
        return max_level