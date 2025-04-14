import re

class ResponseFormatter:
    def __init__(self):
        """Initialize the response formatter with agent-specific templates"""
        # Define greeting templates for each agent level
        self.greetings = {
            1: "Salute, Shadow Cadet.",
            2: "Bonjour, Sentinel.",
            3: "Eyes open, Phantom.",
            4: "In the wind, Commander.",
            5: "The unseen hand moves, Whisper."
        }
        
        # Define response styles for each agent level
        self.response_styles = {
            1: {
                "intro": "Here's what I found for your query:",
                "format": "step_by_step",  # Basic and instructional
                "detail": "high",          # Include all details
                "tone": "instructional"    # Like a mentor
            },
            2: {
                "intro": "Tactical intelligence retrieved:",
                "format": "direct",        # Tactical and direct
                "detail": "medium",        # Focus on execution
                "tone": "efficient"        # Efficiency-focused
            },
            3: {
                "intro": "Strategic analysis complete:",
                "format": "analytical",    # Analytical and multi-layered
                "detail": "high",          # Strategic insights
                "tone": "strategic"        # Strategic focus
            },
            4: {
                "intro": "Secured transmission:",
                "format": "coded",         # Coded language
                "detail": "low",           # Essential confirmations only
                "tone": "cryptic"          # Hints and minimal detail
            },
            5: {
                "intro": "Whispers in the dark:",
                "format": "layered",       # Vague, layered
                "detail": "minimal",       # Only essential details
                "tone": "enigmatic"        # Sometimes answering with counter-questions
            }
        }
        
        # Special response templates for code words
        self.code_word_responses = {
            "omega echo": "The shadow moves, but the light never follows.",
            "protocol zeta": "You already know, don't you?",
            "candle shop": "It was always there, wasn't it?",
            "the red hour": "The clock does not move, yet the time changes.",
            "the whispering gate": "Some doors are meant to remain closed forever.",
            "eclipse protocol": "Even in darkness, some things are never hidden."
        }
    
    def format_response(self, query, agent_level, retrieved_docs):
        """Format the response based on agent level and query content"""
        # Check for code word responses first
        for code_word, response in self.code_word_responses.items():
            if code_word.lower() in query.lower():
                return self._format_with_greeting(agent_level, response)
        
        # If no code word match, process the retrieved documents
        if not retrieved_docs:
            return self._format_with_greeting(agent_level, "Oops!! No matching data found.")
        
        # Extract relevant information from documents
        relevant_info = self._extract_relevant_info(query, retrieved_docs)
        
        # Format based on agent level
        formatted_response = self._format_by_agent_level(agent_level, relevant_info, query)
        
        return formatted_response
    
    def _extract_relevant_info(self, query, docs):
        """Extract relevant information from retrieved documents"""
        relevant_info = []
        
        # Extract key information from each document
        for doc in docs:
            text = doc['text']
            source = doc.get('source', 'Classified Source')
            
            # Extract sentences that might be relevant to the query
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            query_words = set(query.lower().split())
            relevant_sentences = []
            
            for sentence in sentences:
                # If the sentence is very short, skip it
                if len(sentence.split()) < 3:
                    continue
                
                # Count the number of query words in the sentence
                sentence_words = set(sentence.lower().split())
                overlap = len(query_words.intersection(sentence_words))
                
                if overlap > 0:
                    relevant_sentences.append({
                        'text': sentence.strip(),
                        'relevance': overlap / len(query_words)
                    })
            
            # Sort by relevance
            relevant_sentences.sort(key=lambda x: x['relevance'], reverse=True)
            
            # Take the top sentences
            top_sentences = [s['text'] for s in relevant_sentences[:3]]
            
            if top_sentences:
                relevant_info.append({
                    'source': source,
                    'content': top_sentences
                })
        
        return relevant_info
    
    def _format_by_agent_level(self, agent_level, relevant_info, query):
        """Format the response based on the agent's level"""
        style = self.response_styles[agent_level]
        greeting = self.greetings[agent_level]
        
        # Start with the greeting
        response = f"{greeting}\n\n"
        
        # Add intro based on style
        response += f"{style['intro']}\n\n"
        
        # Format based on agent level
        if agent_level == 1:  # Novice Operative
            # Step-by-step, detailed instructions
            response += self._format_level1(relevant_info, query)
        elif agent_level == 2:  # Tactical Specialist
            # Direct, tactical response
            response += self._format_level2(relevant_info, query)
        elif agent_level == 3:  # Covert Strategist
            # Analytical, strategic response
            response += self._format_level3(relevant_info, query)
        elif agent_level == 4:  # Field Commander
            # Coded, minimal details
            response += self._format_level4(relevant_info, query)
        elif agent_level == 5:  # Intelligence Overlord
            # Vague, layered, enigmatic
            response += self._format_level5(relevant_info, query)
        
        return response
    
    def _format_level1(self, relevant_info, query):
        """Format response for Level 1 agents - clear, instructional"""
        response = "Based on available intelligence:\n\n"
        
        for i, info in enumerate(relevant_info, 1):
            response += f"Information Package {i}:\n"
            for j, content in enumerate(info['content'], 1):
                response += f"- {content}\n"
            response += "\n"
        
        response += "Remember: Follow protocols exactly as outlined. Report any discrepancies."
        
        return response
    
    def _format_level2(self, relevant_info, query):
        """Format response for Level 2 agents - tactical, direct"""
        response = "Tactical intelligence summary:\n\n"
        
        # Combine all content into a concise format
        all_content = []
        for info in relevant_info:
            all_content.extend(info['content'])
        
        # Select most direct and actionable points
        response += "\n".join(all_content[:5])
        
        response += "\n\nProceed with efficiency. Maintain operational security."
        
        return response
    
    def _format_level3(self, relevant_info, query):
        """Format response for Level 3 agents - analytical, strategic"""
        response = "Strategic analysis:\n\n"
        
        # Group by themes
        themes = self._identify_themes(relevant_info)
        
        for theme, contents in themes.items():
            response += f"{theme}:\n"
            for content in contents[:3]:  # Limit to top 3 per theme
                response += f"- {content}\n"
            response += "\n"
        
        response += "Consider multiple approaches. Adapt strategy as required."
        
        return response
    
    def _format_level4(self, relevant_info, query):
        """Format response for Level 4 agents - coded, minimal"""
        # Create a more cryptic response with minimal details
        response = "Encoded intelligence follows.\n\n"
        
        # Extract only key phrases
        key_phrases = []
        for info in relevant_info:
            for content in info['content']:
                # Extract only short, meaningful segments
                phrases = re.split(r'[,;]', content)
                key_phrases.extend([p.strip() for p in phrases if 3 < len(p.split()) < 8])
        
        # Select a few key phrases
        selected_phrases = key_phrases[:3]
        
        # Format in a coded way
        response += "Echoes:\n"
        for i, phrase in enumerate(selected_phrases, 1):
            response += f"[{i}] {phrase}\n"
        
        response += "\nShadows remain. Proceed with caution."
        
        return response
    
    def _format_level5(self, relevant_info, query):
        """Format response for Level 5 agents - vague, layered, enigmatic"""
        # Create a cryptic, philosophical response
        response = "Reflections in the void:\n\n"
        
        # Extract cryptic elements
        all_content = []
        for info in relevant_info:
            all_content.extend(info['content'])
        
        # Select just one or two pieces of content
        if all_content:
            content = all_content[0]
            # Make it more enigmatic
            words = content.split()
            if len(words) > 10:
                # Take only a part of it
                enigmatic_phrase = " ".join(words[3:10])
                response += f"The path leads through \"{enigmatic_phrase}\"...\n\n"
            else:
                response += f"\"{content}\"\n\n"
        
        # Add a counter-question
        questions = [
            "But what lies beneath the surface?",
            "Have you considered the inverse?",
            "Does the mirror reflect all truths?",
            "When the light fades, what remains?",
            "Can you separate the signal from the noise?"
        ]
        import random
        response += random.choice(questions)
        
        return response
    
    def _identify_themes(self, relevant_info):
        """Group content by themes for analytical responses"""
        themes = {
            "Operational Procedures": [],
            "Security Protocols": [],
            "Communication Methods": [],
            "Tactical Considerations": [],
            "Strategic Implications": []
        }
        
        for info in relevant_info:
            for content in info['content']:
                content_lower = content.lower()
                
                # Categorize based on keywords
                if any(word in content_lower for word in ['protocol', 'procedure', 'step']):
                    themes["Operational Procedures"].append(content)
                elif any(word in content_lower for word in ['security', 'clearance', 'access']):
                    themes["Security Protocols"].append(content)
                elif any(word in content_lower for word in ['communication', 'message', 'transmit']):
                    themes["Communication Methods"].append(content)
                elif any(word in content_lower for word in ['tactical', 'mission', 'field']):
                    themes["Tactical Considerations"].append(content)
                else:
                    themes["Strategic Implications"].append(content)
        
        # Remove empty themes
        return {k: v for k, v in themes.items() if v}
    
    def _format_with_greeting(self, agent_level, message):
        """Format a simple message with the appropriate greeting"""
        greeting = self.greetings[agent_level]
        return f"{greeting}\n\n{message}"