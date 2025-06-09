# basic_agent.py
from llama_cpp import Llama

class SimpleAgent:
    def __init__(self, model_path):
        self.llm = Llama(model_path=model_path, n_ctx=32768)
        
    def respond(self, prompt):
        return self.llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

# Usage
agent = SimpleAgent("models/qwen3-1.7b-q4_0.gguf")
print(agent.respond("Analyze this SOS report snippet: ..."))
