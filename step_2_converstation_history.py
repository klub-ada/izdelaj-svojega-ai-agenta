from datetime import datetime
import random
import requests
import json
from json_repair import repair_json

class EventAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.1" # Choose 3.2 if you need a lighter model - don't forget to download it first
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        # TODO: Add conversation history to the agent
        

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

                # TODO: Add conversation history to the prompt
                history_context = "..."

                context = f"You are a helpful event assistant. Respond naturally and helpfully to the user's message: {user_input}."

                response = self.ask_ollama(context)

                # TODO: Store conversation in history


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