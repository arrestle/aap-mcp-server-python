# minimal_test.py


import psutil
print(f"Free RAM: {psutil.virtual_memory().available / 1024**3:.1f}GB")


from llama_cpp import Llama

model = Llama(
    model_path="./models/qwen3-1.7b-q4_0.gguf",
    n_ctx=2048,  # Minimum for Qwen3 models
    n_batch=512,
    verbose=False
)
print("Model loaded successfully.")

output = model.create_chat_completion(
    messages=[{"role": "user", "content": "hello"}],
    temperature=0.7,
    max_tokens=512,
    stop=["<|endoftext|>", "<|im_end|>"]  # Qwen3 stop tokens
)

# Print the entire response, not just the first line or a truncated part
full_response = output['choices'][0]['message']['content']
print(full_response)
