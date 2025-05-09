import json
import subprocess
import argparse
from textual.app import App, ComposeResult
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Input, Markdown
from textual import log
from main import parse_sos_report  # make sure main.py is in the same directory


class SOSChatApp(App):
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, tar_path):
        super().__init__()
        self.tar_path = tar_path
        log(f"🧪 Loading SOS report from: {tar_path}")

        try:
            findings = parse_sos_report(tar_path)
            log(f"✅ Parsed {len(findings)} findings from SOS report.")
        except Exception as e:
            log(f"❌ Failed to parse SOS report: {e}")
            findings = [{"error": str(e)}]

        self.context = "\n".join(json.dumps(f, indent=2) for f in findings)

        self.chat_history = f"""🧠 **SOS Chat Ready**

Loaded file: `{tar_path}`  
Parsed {len(findings)} finding(s).  
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
            result = subprocess.run(
                ["ollama", "run", "gemma3", prompt],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"❌ Ollama failed: {e.stderr.strip()}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with an SOS report using Ollama + Textual")
    parser.add_argument("sosreport", help="Path to the sosreport tarball")
    args = parser.parse_args()

    app = SOSChatApp(args.sosreport)
    app.run()
