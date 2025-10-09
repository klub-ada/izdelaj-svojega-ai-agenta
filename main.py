import requests
import json
from json_repair import repair_json

class EventAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.1"
        self.knowledge_graph = self._default_knowledge_graph() # Knowledge about the world
        self.learned_preferences = { # This will get updated with user's inputs
            "interests": [],
            "location": "",
            "preferred_price": ""
        }
        self.conversation_history = [] # Store conversation for context
    
    def add_to_history(self, user_input, agent_response):
        """Add conversation turn to history"""
        self.conversation_history.append({
            "user": user_input,
            "agent": agent_response
        })
        # Keep only last 10 conversations to avoid context getting too long
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def _default_knowledge_graph(self):
        """Initialize default knowledge graph"""
        return {
            
            # VENUES
            "venues": {
                "Cankarjev dom": {
                    "location": "Ljubljana",
                    "type": "cultural center",
                    "good_for": ["music", "theater", "arts", "culture"]
                },
                "Kino Šiška": {
                    "location": "Ljubljana", 
                    "type": "music venue",
                    "good_for": ["music", "concerts", "alternative culture"]
                },
                "Ljubljana Castle": {
                    "location": "Ljubljana",
                    "type": "historic venue",
                    "good_for": ["culture", "history", "events", "tourism"]
                },
                "Maribor Castle": {
                    "location": "Maribor",
                    "type": "historic venue", 
                    "good_for": ["culture", "history", "events"]
                },
                "Koper Conference Centre": {
                    "location": "Koper",
                    "type": "conference center",
                    "good_for": ["business", "networking", "conferences"]
                },
                "Bled Castle": {
                    "location": "Bled",
                    "type": "historic venue",
                    "good_for": ["culture", "history", "tourism", "events"]
                }
            },
            
            # ORGANIZERS
            "organizers": {
                "Ljubljana Festival": {
                    "focus": ["music", "culture", "arts"],
                    "quality": "high",
                    "user_follows": False
                },
                "Slovenian Tech Community": {
                    "focus": ["technology", "AI", "startups"],
                    "quality": "high", 
                    "user_follows": False
                },
                "Maribor Theatre": {
                    "focus": ["theater", "drama", "culture"],
                    "quality": "high",
                    "user_follows": False
                },
                "Slovenian Alpine Association": {
                    "focus": ["outdoor", "hiking", "mountaineering"],
                    "quality": "high",
                    "user_follows": False
                },
                "Koper Business Network": {
                    "focus": ["business", "networking", "entrepreneurship"],
                    "quality": "high",
                    "user_follows": False
                }
            },
            
            # RELATIONSHIPS
            "relationships": {
                "interest_keywords": {
                    "technology": ["AI", "tech", "startup", "coding", "developer", "programming"],
                    "music": ["jazz", "concert", "band", "live music", "festival", "classical"],
                    "networking": ["meetup", "happy hour", "mixer", "network", "business"],
                    "culture": ["theater", "drama", "arts", "exhibition", "museum"],
                    "outdoor": ["hiking", "mountaineering", "nature", "alpine", "sports"],
                    "business": ["conference", "workshop", "entrepreneurship", "startup"]
                },
                "related_interests": {
                    "technology": ["networking", "business"],
                    "music": ["culture", "arts"],
                    "networking": ["technology", "business"],
                    "culture": ["music", "arts"],
                    "outdoor": ["sports"],
                    "business": ["technology", "networking"]
                }
            }
        }
    
    def get_mock_events(self):
        """Mock API call - returns fake events"""
        return [
            {
                "id": "1",
                "name": "Slovenian AI & Tech Summit",
                "category": "technology",
                "location": "Ljubljana",
                "date": "2024-03-15",
                "organizer": "Slovenian Tech Community",
                "venue": "Cankarjev dom"
            },
            {
                "id": "2",
                "name": "Ljubljana Jazz Festival",
                "category": "music",
                "location": "Ljubljana",
                "date": "2024-03-20",
                "organizer": "Ljubljana Festival",
                "venue": "Kino Šiška"
            },
            {
                "id": "3",
                "name": "Startup Networking Evening",
                "category": "networking",
                "location": "Koper",
                "date": "2024-03-25",
                "organizer": "Koper Business Network",
                "venue": "Koper Conference Centre"
            },
            {
                "id": "4",
                "name": "Classical Concert at Ljubljana Castle",
                "category": "culture",
                "location": "Ljubljana",
                "date": "2024-03-28",
                "organizer": "Ljubljana Festival",
                "venue": "Ljubljana Castle"
            },
            {
                "id": "5",
                "name": "Alpine Hiking Workshop",
                "category": "outdoor",
                "location": "Bled",
                "date": "2024-04-05",
                "organizer": "Slovenian Alpine Association",
                "venue": "Bled Castle"
            },
            {
                "id": "6",
                "name": "Maribor Theatre Performance",
                "category": "culture",
                "location": "Maribor",
                "date": "2024-04-10",
                "organizer": "Maribor Theatre",
                "venue": "Maribor Castle"
            }
        ]

    def score_event(self, event):
        """Score event based on knowledge graph"""
        score = 0
        reasons = []
        
        # Check interest match
        user_interests = self.learned_preferences["interests"]
        if event.get("category") in user_interests:
            score += 3
            reasons.append(f"matches {event['category']} interest")
        
        # Check location
        if event.get("location") == self.learned_preferences["location"]:
            score += 2
            reasons.append("in your city")
        
        # Check if organizer is followed
        organizer = event.get("organizer")
        if organizer in self.knowledge_graph["organizers"]:
            if self.knowledge_graph["organizers"][organizer].get("user_follows"):
                score += 2
                reasons.append("by organizer you follow")
        
        return score, reasons

    def suggest_events(self):
        """Get events from API and score them using knowledge graph"""
        # Get events (mocked API call)
        events = self.get_mock_events()
        
        # Score each event using knowledge graph
        scored_events = []
        for event in events:
            score, reasons = self.score_event(event)
            if score > 0:
                scored_events.append({
                    **event,
                    "score": score,
                    "reasons": reasons
                })
        
        # Sort by score
        scored_events.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_events
    
    def ask_ollama(self, prompt):
        """Send prompt to Ollama and get response"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {e}"
    
    def update_user_preferences(self, user_input):
        """Update user interests based on input using LLM"""
        user_preferences = self.learned_preferences
        
        prompt = f"""<|im_start|>system
You are a JSON-only response system. You must respond with ONLY valid JSON, no other text.

Current user preferences: {json.dumps(user_preferences)}

User said: "{user_input}"

Update the user preferences based on the user's message.
Keep all other fields unchanged and don't remove or add any fields.

Examples:
- "I love cooking" → add "cooking" to interests
- "I'm interested in photography" → add "photography" to interests  
- "I hate sports" → remove "sports" from interests if present
- "My name is John" → update "name" to "John"
- "I live in San Francisco" → update "location" to "San Francisco"
- "I prefer free events" → update "preferred_price" to "free"

CRITICAL: Respond with ONLY the JSON object, no explanations, no markdown, no code blocks, no extra text.
<|im_end|>
<|im_start|>assistant
{json.dumps(user_preferences)}<|im_end|>
<|im_start|>user
{user_input}<|im_end|>
<|im_start|>assistant"""

        # TODO: limit possible interests to a predefined list ?

        try:
            response = self.ask_ollama(prompt)
            
            # Try to parse the response directly as JSON
            try:
                updated_preferences = json.loads(response.strip())
            except json.JSONDecodeError:
                # If direct parsing fails, try with json_repair
                clean_json = repair_json(response.strip())
                updated_preferences = json.loads(clean_json)
                
            # Update the learned preferences
            print(f"Updated preferences: {updated_preferences}")
            self.learned_preferences = updated_preferences
                
        except Exception as e:
            return f"Error updating preferences: {e}"

    def chat(self, user_input):
        """Main chat interface"""
        # Check if user wants event suggestions
        if any(keyword in user_input.lower() for keyword in ["suggest", "events", "recommend", "what events"]):
            suggested_events = self.suggest_events()
            
            if not suggested_events:
                return "No events match your current interests. Try updating your preferences!"
            
            # Format events nicely without showing scores
            formatted_events = []
            for i, event in enumerate(suggested_events, 1):
                event_info = f"{i}. **{event['name']}**\n"
                event_info += f"   📅 {event['date']}\n"
                event_info += f"   📍 {event['location']}\n"
                event_info += f"   🏢 {event['venue']}\n"
                event_info += f"   👤 {event['organizer']}\n"
                if event.get('reasons'):
                    event_info += f"   💡 Why: {', '.join(event['reasons'])}\n"
                formatted_events.append(event_info)
            
            return "Here are some events that might interest you:\n\n" + "\n".join(formatted_events)
            
        
        # Regular conversation with context about user
        user_preferences = json.dumps(self.learned_preferences)
        
        # Build conversation history context
        history_context = ""
        if self.conversation_history:
            for i, turn in enumerate(self.conversation_history, 1):
                history_context += f"{i}. User: {turn['user']}\n"
                history_context += f"   Agent: {turn['agent'][:300]}...\n"  # Truncate long responses
        
        context = f"""You are a helpful event assistant.
These are the user's preferences: {user_preferences}

Previous conversation: {history_context}

Current user message: {user_input}

IMPORTANT: Only discuss real events that exist in the system. Do not create or suggest new events.
If the user asks about events, tell them to ask for "suggest events" to see available options.

Respond naturally and helpfully."""
        
        return self.ask_ollama(context)
    
    def run(self):
        """Run the agent in interactive mode"""
        print(f"🤖 Hi! I'm your Event Agent.")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("🤖 Goodbye! Have fun at the events!")
                    break

                responseUpdate = self.update_user_preferences(user_input)
                response = self.chat(user_input)
                
                # Store conversation in history
                self.add_to_history(user_input, response)
                
                print(f"🤖 {response}\n")
                
            except KeyboardInterrupt:
                print("\n🤖 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


# Demo usage
if __name__ == "__main__":
    # Create agent
    agent = EventAgent()
    
    # Run interactive mode
    agent.run()