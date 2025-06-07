# sos_chat_tui.py

import requests
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# Configuration
MCP_SERVER_URL = "http://localhost:8000/mcp/qwen3"

def stream_query_to_mcp(prompt):
    """Send prompt to MCP server and stream response line-by-line."""
    try:
        with requests.post(MCP_SERVER_URL, json={"prompt": prompt}, stream=True) as r:
            if r.status_code != 200:
                yield f"[ERROR] Server returned status code {r.status_code}"
                return

            buffer = ""
            for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    lines = buffer.splitlines()
                    for line in lines[:-1]:
                        yield line
                    buffer = lines[-1]
            if buffer:
                yield buffer
    except requests.exceptions.ConnectionError:
        yield "[ERROR] Could not connect to MCP server. Is it running?"
    except Exception as e:
        yield f"[ERROR] {str(e)}"

def main():
    console.print(Panel.fit("🤖 Ansible IQ - SOS Report Assistant", style="bold cyan"))

    console.print("\nEnter your question below. Type 'exit' or 'quit' to quit.\n")

    while True:
        try:
            user_input = input("💬 You: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                console.print("👋 Goodbye!")
                break

            console.print("[AI]: ", end="")
            full_response = ""

            for response_line in stream_query_to_mcp(user_input):
                # Accumulate full response
                full_response += response_line

                # Try to render as Markdown
                try:
                    console.print(Markdown(response_line), end="")
                except:
                    console.print(response_line, end="")

            print("\n" + "-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Interrupted. Exiting...")
            break

if __name__ == "__main__":
    main()