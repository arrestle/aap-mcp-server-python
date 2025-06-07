# Makefile for Ansible IQ - Ansible SOS Report Analyzer with Qwen AI

NAME = ansible-iq
IMAGE = localhost/$(NAME)
CONTAINER = $(NAME)
PORT = 8000
VENV = .venv
SOS_DIR = /var/mcp
SOS_FILE = $(SOS_DIR)/sosreport

.PHONY: all setup build run-server run-tui clean

all: setup build

setup:
	@echo "🟡 Setting up virtual environment..."
	python3 -m venv $(VENV)
	pip install --upgrade pip
	source $(VENV)/bin/activate && pip install --no-cache-dir -r requirements.txt

build:
	@echo "🟡 Building Podman container..."
	podman stop $(CONTAINER) || true
	podman rm $(CONTAINER) || true
	podman rmi $(IMAGE) || true
	podman build -t $(IMAGE) -f Dockerfile.podman

run-server:
	@echo "🟢 Starting Ollama (ensure it's installed and running)"
	@echo "🟢 Copying SOS report into container..."
	podman stop $(CONTAINER) || true
	podman rm $(CONTAINER) || true
	podman run -d --name $(CONTAINER) -p $(PORT):$(PORT) $(IMAGE)
	podman exec -it $(CONTAINER) mkdir -p /var/mcp
	podman cp $(SOS_FILE) $(CONTAINER):/var/mcp/sosreport
	@echo "🟢 MCP Server is now running at curl http://127.0.0.1:$(PORT)"
	curl http://127.0.0.1:$(PORT)/health

run-tui:
	@echo "🟢 Launching TUI..."
	python sos_chat_tui.py

clean:
	@echo "🔴 Removing container and image..."
	podman stop $(CONTAINER) || true
	podman rm $(CONTAINER) || true
	podman rmi $(IMAGE) || true
	rm -rf $(VENV) __pycache__ *.pyc
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "🟢 Project cleaned."

help:
	@echo "Makefile for Ansible IQ"
	@echo ""
	@echo "Usage:"
	@echo "  make setup         - Set up Python virtual env and install dependencies"
	@echo "  make build         - Build the Podman container"
	@echo "  make run-server    - Run the MCP server with SOS report mounted"
	@echo "  make run-tui       - Run the interactive TUI chatbot"
	@echo "  make clean         - Remove containers, images, and clean up"