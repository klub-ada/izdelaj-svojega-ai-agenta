from datetime import datetime
import random
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
            "preferred_price": "",
            "date": ""
        }
        self.current_date = datetime.now().strftime("%Y-%m-%d")
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
                "date": "2025-11-15",
                "organizer": "Slovenian Tech Community",
                "venue": "Cankarjev dom",
                "price": "20 EUR"
            },
            {
                "id": "2",
                "name": "Ljubljana Jazz Festival",
                "category": "music",
                "location": "Ljubljana",
                "date": "2025-11-20",
                "organizer": "Ljubljana Festival",
                "venue": "Kino Šiška",
                "price": "25 EUR"
            },
            {
                "id": "3",
                "name": "Startup Networking Evening",
                "category": "networking",
                "location": "Koper",
                "date": "2025-11-25",
                "organizer": "Koper Business Network",
                "venue": "Koper Conference Centre",
                "price": "30 EUR"
            },
            {
                "id": "4",
                "name": "Classical Concert at Ljubljana Castle",
                "category": "culture",
                "location": "Ljubljana",
                "date": "2025-11-28",
                "organizer": "Ljubljana Festival",
                "venue": "Ljubljana Castle",
                "price": "15 EUR"
            },
            {
                "id": "5",
                "name": "Alpine Hiking Workshop",
                "category": "outdoor",
                "location": "Bled",
                "date": "2025-11-05",
                "organizer": "Slovenian Alpine Association",
                "venue": "Bled Castle",
                "price": "50 EUR"
            },
            {
                "id": "6",
                "name": "Maribor Theatre Performance",
                "category": "culture",
                "location": "Maribor",
                "date": "2025-11-10",
                "organizer": "Maribor Theatre",
                "venue": "Maribor Castle",
                "price": "30 EUR"
            }
        ]
    
    def follow_organizer(self, organizer_name=None):
        """Follow an event organizer"""
        if not organizer_name:
            return "Please specify an organizer name to follow."

        # Check if organizer exists in knowledge graph
        if organizer_name in self.knowledge_graph["organizers"]:
            self.knowledge_graph["organizers"][organizer_name]["user_follows"] = True
            return f"✓ Now following {organizer_name}. You'll see more events from them!"

        # If not in knowledge graph, add them
        self.knowledge_graph["organizers"][organizer_name] = {
            "focus": [],
            "quality": "unknown",
            "user_follows": True
        }
        return f"✓ Now following {organizer_name}."    
    
    def get_event_details(self, event_id=None):
        """Get detailed information about a specific event"""
        events = self.get_mock_events()

        if event_id:
            for event in events:
                if str(event.get("id")) == str(event_id):
                    return event
            return None

        # If no ID provided, return first event
        return events[0] if events else None

    def score_event(self, event):
        """Score event based on knowledge graph"""
        score = 0
        reasons = []

        # If no preferences, return a random score
        if self.learned_preferences["location"] == "" and self.learned_preferences["preferred_price"] == "" and self.learned_preferences["interests"] == []:
            return random.randint(0, 3), ["suggested event"]
        
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
    
    def llm_score_events(self, events):
        """Use Ollama to score a list of events against the current user preferences.

        Returns a list of event dicts augmented with 'score' (int) and 'reasons' (list).
        Returns None if the LLM response cannot be parsed or validated so caller can fall back.
        """
        if not events:
            return []

        # Prepare a compact events payload for the prompt
        events_brief = []
        for e in events:
            events_brief.append({
                "id": e.get("id"),
                "name": e.get("name"),
                "category": e.get("category"),
                "location": e.get("location"),
                "date": e.get("date"),
                "organizer": e.get("organizer"),
                "venue": e.get("venue")
            })

        prompt = f"""You are an assistant that ranks events for a specific user. Respond with ONLY valid JSON (no explanations).

User preferences: {json.dumps(self.learned_preferences)}

Today's date: {self.current_date}

Events: {json.dumps(events_brief)}

For each event return an object with these fields:
- id: the event id
- score: integer 0-5 (5 = very relevant, 0 = not relevant)
- reasons: array of 1-3 short strings explaining the score (e.g. "matches interest: music", "in user's city")

Return a JSON array like: [{"id":"1","score":4,"reasons":["matches interest"]}, ...]
CRITICAL: ONLY output JSON, no extra text.
"""
        raw = self.ask_ollama(prompt)

        # Try to parse the response
        try:
            parsed = json.loads(raw.strip())
        except Exception:
            try:
                repaired = repair_json(raw.strip())
                parsed = json.loads(repaired)
            except Exception:
                return None

        # Validate structure
        if not isinstance(parsed, list):
            return None

        score_map = {}
        for obj in parsed:
            if not isinstance(obj, dict):
                continue
            eid = str(obj.get("id")) if obj.get("id") is not None else None
            score = obj.get("score")
            reasons = obj.get("reasons") or []
            try:
                score_int = int(score)
            except Exception:
                continue
            if eid is None:
                continue
            score_map[eid] = {"score": max(0, min(5, score_int)), "reasons": reasons}

        # Merge scores back into full event objects
        augmented = []
        for e in events:
            entry = dict(e)
            meta = score_map.get(str(e.get("id")))
            if meta:
                entry["score"] = meta["score"]
                entry["reasons"] = meta.get("reasons", [])
            else:
                entry["score"] = 0
                entry["reasons"] = []
            augmented.append(entry)

        augmented.sort(key=lambda x: x.get("score", 0), reverse=True)
        return augmented

    def suggest_events(self):
        """Get events and score them using the LLM first; fallback to keyword/graph scoring."""
        events = self.get_mock_events()

        # Try LLM scoring
        llm_scored = None
        try:
            llm_scored = self.llm_score_events(events)
        except Exception:
            llm_scored = None

        scored_events = []
        if llm_scored:
            for event in llm_scored:
                if event.get("score", 0) > 0:
                    # keep original event fields and attach reasons
                    base = {k: v for k, v in event.items() if k not in ("score", "reasons")}
                    scored_events.append({**base, "score": event["score"], "reasons": event.get("reasons", [])})
        else:
            # Fallback to local scoring
            for event in events:
                score, reasons = self.score_event(event)
                if score > 0:
                    scored_events.append({
                        **event,
                        "score": score,
                        "reasons": reasons
                    })

        scored_events.sort(key=lambda x: x.get("score", 0), reverse=True)
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
- "I'm available on Friday" → update "date" to "Friday"
- "I'm available on Friday and Saturday" → update "date" to "Friday,Saturday"
- "I'm interested in events in the next two weeks" → update "date" to "next two weeks"

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


    def follow_organizer(self, organizer_name=None):
        """Follow an event organizer"""
        if not organizer_name:
            return "Please specify an organizer name to follow."

        # Check if organizer exists in knowledge graph
        if organizer_name in self.knowledge_graph["organizers"]:
            self.knowledge_graph["organizers"][organizer_name]["user_follows"] = True
            return f"✓ Now following {organizer_name}. You'll see more events from them!"

        # If not in knowledge graph, add them
        self.knowledge_graph["organizers"][organizer_name] = {
            "focus": [],
            "quality": "unknown",
            "user_follows": True
        }
        return f"✓ Now following {organizer_name}."
    
    def compare_events(self, event_id_1, event_id_2):
        """Compare two events side by side"""
        event1 = self.get_event_details(event_id_1)
        event2 = self.get_event_details(event_id_2)

        if not event1:
            return f"Event {event_id_1} not found."
        if not event2:
            return f"Event {event_id_2} not found."

        comparison = f"""📊 Comparing Events:

Event 1: {event1['name']}
  📅 Date: {event1['date']}
  📍 Location: {event1['location']}
  🏢 Venue: {event1['venue']}
  🏷️ Category: {event1['category']}
  💰 Price: {event1['price']}

Event 2: {event2['name']}
  📅 Date: {event2['date']}
  📍 Location: {event2['location']}
  🏢 Venue: {event2['venue']}
  🏷️ Category: {event2['category']}
  💰 Price: {event2['price']}
"""
        return comparison
        
    def decide_action(self, user_input):
        """Agent decides what action to take"""
        prompt = f"""Based on this user input, decide what action to take.

    User input: "{user_input}"

    Available actions:
    - "suggest_events": Show personalized event recommendations
    - "get_event_details": Get detailed information about a specific event
    - "update_user_preferences": Extract and update user preferences
    - "follow_organizer": Follow an event organizer
    - "compare_events": Compare two events
    - "ask_clarification": Ask user for more information
    - "quit": Quit the agent, end the conversation
    - "general_chat": Have a normal conversation

    Respond with ONLY the action name, nothing else."""

        action = self.ask_ollama(prompt).strip().lower()
        return action

    def execute_action(self, action, user_input):
        """Execute a single action based on the decided action"""
        action = action.strip().lower()

        # Handle each action by calling the appropriate tool or method
        if action == "search_events" or action == "suggest_events":
            return self.suggest_events()
        elif action == "get_event_details":
            # Try to extract event ID from user input using LLM
            prompt = f"""Extract the event ID from this user input. User said: "{user_input}"
            
If there's a number that refers to an event, respond with just that number.
If no event ID is mentioned, respond with "none".
Only respond with the number or "none", nothing else."""

            event_id = self.ask_ollama(prompt).strip().lower()
            if event_id != "none":
                details = self.get_event_details(event_id)
                if details:
                    return f"Event: {details['name']}\n📅 {details['date']}\n📍 {details['location']} at {details['venue']}\n🏷️ {details['category']}\n👤 Organized by {details['organizer']}"
                return f"Event with ID {event_id} not found."
            return "Please specify which event you'd like details about."

        elif action == "follow_organizer":
            # Try to extract organizer name from user input using LLM
            organizers = list(self.knowledge_graph["organizers"].keys())
            prompt = f"""Extract the organizer name from this user input: "{user_input}"

Available organizers: {', '.join(organizers)}

Respond with ONLY the organizer name if found, or "none" if no organizer is mentioned.
Match the exact name from the available organizers list."""

            organizer_name = self.ask_ollama(prompt).strip()
            if organizer_name != "none" and organizer_name in organizers:
                return self.follow_organizer(organizer_name)

            # Fallback: try simple string matching
            for org in organizers:
                if org.lower() in user_input.lower():
                    return self.follow_organizer(org)

            return f"Please specify which organizer you'd like to follow. Available: {', '.join(organizers)}"

        elif action == "compare_events":
            # Try to extract two event IDs from user input
            prompt = f"""Extract two event IDs from this user input: "{user_input}"
            
Respond with two numbers separated by a comma (e.g., "1,2").
If you can't find two event IDs, respond with "none".
Only respond with numbers and comma, or "none"."""

            result = self.ask_ollama(prompt).strip().lower()
            if result != "none" and "," in result:
                ids = result.split(",")
                if len(ids) == 2:
                    return self.compare_events(ids[0].strip(), ids[1].strip())
            return "Please specify two event IDs to compare (e.g., 'compare events 1 and 2')."

        elif action == "update_user_preferences":
            self.update_user_preferences(user_input)
            return "preferences_updated"

        elif action == "general_chat" or action == "ask_clarification":
            return self.chat(user_input)

        elif action == "quit":
            return "quit"

        else:
            # Unknown action - try to handle gracefully by defaulting to chat
            print(f"⚠️ Warning: Unknown action '{action}' - defaulting to general chat")
            return self.chat(user_input)

    def chat(self, user_input):
        """Main chat interface"""
         # Build conversation history context
        history_context = ""
        if self.conversation_history:
            for i, turn in enumerate(self.conversation_history, 1):
                history_context += f"{i}. User: {turn['user']}\n"
                history_context += f"   Agent: {turn['agent'][:300]}...\n"  # Truncate long responses
        
        # Regular conversation with context about user
        user_preferences = json.dumps(self.learned_preferences)

        context = f"""You are a helpful event assistant.
These are the user's preferences: {user_preferences}

Previous conversation: {history_context}

Current user message: {user_input}

IMPORTANT: Only discuss real events that exist in the system. Do not create or suggest new events.
If the user asks about events, tell them to ask for "suggest events" to see available options.

Respond naturally and helpfully."""
        
        return self.ask_ollama(context)

    def plan_and_execute(self, user_input):
        """Agent decides on action and executes it using LLM-based decision making"""
        # Step 1: Decide what action to take (using LLM)
        action = self.decide_action(user_input)

        # Step 2: Check if user wants to quit
        if action == "quit":
            return "quit"

        # Step 3: Execute the decided action
        result = self.execute_action(action, user_input)

        # Step 4: If result is "quit", propagate it
        if result == "quit":
            return "quit"

        # Step 5: Format the result properly
        if result == "preferences_updated":
            return "✓ I've updated your preferences."
        elif isinstance(result, list):
            # It's a list of events - format them nicely
            if not result:
                return "No events match your current interests. Try updating your preferences!"

            formatted_events = []
            for i, event in enumerate(result[:5], 1):  # Show top 5
                event_info = f"{i}. **{event['name']}**"
                event_info += f"\n   📅 {event['date']}"
                event_info += f"\n   📍 Location: {event['location']}"
                event_info += f"\n   💰 Price: {event['price']}"
                if event.get('reasons'):
                    event_info += f"\n   💡 Why: {', '.join(event['reasons'])}"
                formatted_events.append(event_info)
            return "Here are some events for you:\n\n" + "\n\n".join(formatted_events)
        else:
            # Return result as-is (it's already formatted)
            return result

    def run(self):
        """Run the agent in interactive mode with agentic workflow"""
        print(f"🤖 Hi! I'm your Event Agent.")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if "exit" in user_input.lower() or "quit" in user_input.lower() or "bye" in user_input.lower():
                    print("🤖 Goodbye! Have fun at the events!")
                    break

                # Use agentic plan-and-execute workflow
                response = self.plan_and_execute(user_input)

                # Check if agent decided to quit
                if response == "quit":
                    print("🤖 Goodbye! Have fun at the events!")
                    break

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