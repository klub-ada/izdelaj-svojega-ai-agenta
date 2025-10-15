from datetime import datetime
import random
import requests
import json
import os
from json_repair import repair_json

class EventAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.1" # Choose 3.2 if you need a lighter model - don't forget to download it first
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.conversation_history = [] # Store conversation for context
        # TODO: Add user preferences

    def get_mock_events(self):
        # Mock API call - returns fake events
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            events_file_path = os.path.join(script_dir, "resources", "events.json")
            
            with open(events_file_path, 'r', encoding='utf-8') as file:
                events = json.load(file)
            return events
        except Exception as e:
            print(f"❌ Error loading events: {e}. Using empty list.")
            return []

    def update_user_preferences(self, user_input):
    # Update user preferences based on input using LLM
        user_preferences = self.user_preferences
        
        prompt = f"""You are a JSON-only response system. You must respond with ONLY valid JSON, no other text.

Current user preferences: {json.dumps(user_preferences)}

User said: "{user_input}"

Update the user preferences based on the user's message.
Keep all other fields unchanged and don't remove or add any fields.

For interests, you can ONLY add the following:
- music
- theater
- sports
- entrepreneurship
- technology
- history
If user expresses interest in a topic that is not in the list, do not add anything to the interests.

Examples:
- "I enjoy learning about AI" → add "technology" to interests
- "I'm interested in the middle ages" → add "history" to interests  
- "I hate sports" → remove "sports" from interests if present
" I like animals" → do not add anything to the interests

If user expresses interest in a specific location, update the location field.
Examples:
- "I live in San Francisco" → update "location" to "San Francisco"

For preferred_price, you can only add the following:
- affordable (up to 20 EUR)
- moderate (up to 50 EUR)
For anything above 50 EUR, do not update the preferred_price field.

Examples:
- "I prefer free events" → update "preferred_price" to "affordable"
- "I prefer events up to 50 EUR" → update "preferred_price" to "moderate"

CRITICAL: Respond with ONLY the JSON object, no explanations, no markdown, no code blocks, no extra text.
"""

        try:
            response = self.ask_ollama(prompt)
            
            # Try to parse the response directly as JSON
            try:
                updated_preferences = json.loads(response.strip())
            except json.JSONDecodeError:
                # If direct parsing fails, try with json_repair
                clean_json = repair_json(response.strip())
                updated_preferences = json.loads(clean_json)
                
            # Update user preferences
            print(f"Updated preferences: {updated_preferences}")
            self.user_preferences = updated_preferences
                
        except Exception as e:
            return f"Error updating preferences: {e}"

    # Add conversation turn to history
    def add_to_history(self, user_input, agent_response):
        """Add conversation turn to history"""
        self.conversation_history.append({
            "user": user_input,
            "agent": agent_response
        })
     
    def get_history_context(self):
        """Get conversation history context"""
        history_context = ""
        if self.conversation_history:
            for i, turn in enumerate(self.conversation_history, 1):
                history_context += f"{i}. User: {turn['user']}\n"
                history_context += f"   Agent: {turn['agent']}...\n"
        return history_context
    
    # Send a prompt to the Ollama LLM and get a response
    def ask_ollama(self, prompt):
        
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

    # Run the agent in interactive mode
    def run(self):
        print(f"🤖 Hi! I'm your Event Agent.")
        
        while True: # Loop until the user wants to quit
            try:
                # Get the user input
                user_input = input("👩 You: ").strip()
                
                # If the user input is empty, do nothing
                if not user_input:
                    continue
                
                # If user input contains the word "exit", "quit", or "bye", quit the agent
                if "exit" in user_input.lower() or "quit" in user_input.lower() or "bye" in user_input.lower():
                    print("🤖 Goodbye! Have fun at the events!")
                    break

                # TODO: Update user preferences
                

                # Build conversation history context
                history_context = self.get_history_context()

                # Get events data
                events = self.get_mock_events()

                # The prompt
                # TODO: Add user preferences to the prompt
                context = f"""
You are a helpful event assistant and you should always respond with an event that matches the user's interests.
This is the user's message: {user_input}.
Previous conversation: {history_context}.
These are the events you can choose from: {events}.
Only discuss the events from the list. If there are no events that match the user's interests, say so.
Respond naturally and helpfully.
"""

                response = self.ask_ollama(context)

                # Store conversation in history
                self.add_to_history(user_input, response)

                print(f"🤖 {response}\n")
                
            except KeyboardInterrupt:
                print("\n🤖 Goodbye!")
                break


# Demo usage
if __name__ == "__main__":
    # Create agent
    agent = EventAgent()
    
    # Run the agent in interactive mode
    agent.run()