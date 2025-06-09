# sos_chat_tui.py

import requests
import sys
import json
from rich.console import Console
from rich.markdown import Markdown

console = Console()
MCP_SERVER_URL = "http://127.0.0.1:8000/mcp/qwen3"

def stream_query_to_mcp(prompt):
    try:
        with requests.post(MCP_SERVER_URL, json={"prompt": prompt}, stream=True) as r:
            buffer = ""
            for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    buffer += chunk

                    # Try to parse JSON lines
                    lines = buffer.split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                            except json.JSONDecodeError:
                                continue
                    # Keep incomplete line in buffer
                    buffer = lines[-1] if len(lines) > 1 else buffer

            # After loop, process remaining buffer
            if buffer.strip():
                try:
                    data = json.loads(buffer)
                    if "response" in data:
                        yield data["response"]
                except json.JSONDecodeError:
                    pass

    except requests.exceptions.ConnectionError:
        yield "[ERROR] Could not connect to MCP server. Is it running?"
    except Exception as e:
        yield f"[ERROR] {str(e)}"


def main():
    console.print(Markdown("# 🤖 Ansible IQ - SOS Report Assistant"))
    console.print("Enter your question below. Type 'exit' or 'quit' to quit.\n")

    while True:
        try:
            user_input = input("💬 You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break

            console.print("[AI]: ", end="")

            full_response = ""
            display_buffer = ""

            for response_line in stream_query_to_mcp(user_input):
                if response_line.startswith("[ERROR"):
                    console.print(response_line)
                    break

                # Merge small chunks into readable phrases
                display_buffer += response_line

                # If we have a complete phrase (ends with punctuation), flush buffer
                if any(display_buffer.strip().endswith(p) for p in [".", "?", "!", ":", "\n"]):
                    full_response += display_buffer
                    try:
                        console.print(Markdown(display_buffer), end="")
                    except:
                        console.print(display_buffer, end="")
                    display_buffer = ""

            # Print any leftover text after done
            if display_buffer:
                full_response += display_buffer
                try:
                    console.print(Markdown(display_buffer), end="")
                except:
                    console.print(display_buffer, end="")

            print("\n" + "-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n👋 Interrupted. Exiting...")
            break


if __name__ == "__main__":
    main()