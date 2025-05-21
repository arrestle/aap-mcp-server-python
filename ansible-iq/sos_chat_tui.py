import json
import subprocess
import argparse
from textual.app import App, ComposeResult
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Input, Markdown
from textual import log
from mcp_parser.sos_summary import parse_sos_report
import requests


def query_llm(prompt: str) -> str:
    try:
        response = requests.post(
            "http://127.0.0.1:8000/mcp/qwen3",
            json={"prompt": prompt}
        )
        response.raise_for_status()
        result = response.json()
        return result.get("llm_output", "🤖 No response from model.")
    except Exception as e:
        return f"❌ Error querying LLM: {e}"

class SOSChatApp(App):
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, tar_path):
        super().__init__()
        self.tar_path = tar_path
        log(f"🧪 Loading SOS report from: {tar_path}")

        try:
            initial_summary = parse_sos_report(tar_path)
            self.context = initial_summary
            log("✅ SOS summary parsed.")
        except Exception as e:
            log(f"❌ Failed to parse SOS report: {e}")
            self.context = "Error parsing SOS report."

        self.chat_history = f"""🧠 **SOS Chat Ready**

Loaded file: `{tar_path}`  
Parsed SOS report summary below:  

{self.context}

Ask a question below.
"""
        self.chat_output = Markdown(self.chat_history)

    def compose(self) -> ComposeResult:
        with Vertical():
            with ScrollableContainer():
                yield self.chat_output
            yield Input(placeholder="Type a question and hit Enter", id="chat_input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        question = event.value.strip()
        if question.lower() in ("exit", "quit"):
            self.exit()
            return
        if question:
            response = self.call_ollama(question)
            self.chat_history += f"\n\n> {question}\n\n{response}\n"
            self.chat_output.update(self.chat_history)
        event.input.value = ""

    def call_ollama(self, question):
        prompt = f"Context:\n{self.context}\n\nQuestion: {question}"
        try:
            response = requests.post(
                "http://127.0.0.1:8000/mcp/qwen3",
                json={"prompt": prompt}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("llm_output", "🤖 No response from model.")
        except Exception as e:
            return f"❌ MCP server error: {e}"



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with an SOS report using Ollama + Textual")
    parser.add_argument("sosreport", help="Path to the sosreport tarball")
    args = parser.parse_args()

    app = SOSChatApp(args.sosreport)
    app.run()
