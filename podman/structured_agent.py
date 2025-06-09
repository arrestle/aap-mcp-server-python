import json
import re
from typing import Callable, Dict
from pydantic import BaseModel, ValidationError
from llama_cpp import Llama

class AnalysisResult(BaseModel):
    summary: str
    critical_errors: int
    recommendations: list[str]

class StructuredAgent:
    def __init__(self, model_path):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=40960,  # Match Qwen3's training context
            verbose=False
        )
    
    def generate_structured_response(self, prompt):
        structured_prompt = f"""JSON Output Format:
{{
    "summary": "concise problem summary",
    "critical_errors": <int>,
    "recommendations": ["action1", "action2"]
}}

Input: {prompt}
Output:"""
        
        response = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": structured_prompt}],
            temperature=0.2,
            max_tokens=512
        )
        return response['choices'][0]['message']['content']

    def _extract_json(self, raw_response: str) -> dict:
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in model response")
        
        json_str = json_match.group()
        json_str = json_str.replace("'", '"')
        json_str = re.sub(r',\s*}', '}', json_str)
        
        return json.loads(json_str)

    def analyze_sos(self, prompt) -> AnalysisResult:
        try:
            raw_content = self.generate_structured_response(prompt)
            json_data = self._extract_json(raw_content)
            return AnalysisResult.model_validate(json_data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Validation failed. Raw model output:\n{raw_content}")
            raise

# Example usage
if __name__ == "__main__":
    agent = StructuredAgent("models/qwen3-1.7b-q4_0.gguf")
    try:
        result = agent.analyze_sos("""
            Analyze this SOS report:
            - High CPU usage (95% sustained)
            - 3 failed cron jobs
            - 2 firewall rule conflicts
        """)
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
