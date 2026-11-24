from pathlib import Path

# Free, small instruct model that runs on CPU. Alternatives:
# "Qwen/Qwen2.5-1.5B-Instruct", "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
# "microsoft/Phi-3-mini-4k-instruct" (needs more RAM)
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

MAX_NEW_TOKENS = 512
TEMPERATURE = 0.7
TOP_P = 0.9

SYSTEM_PROMPT = "You are a helpful, concise assistant."

# How many recent messages are sent to the model (keeps prompt small and fast)
MAX_HISTORY_MESSAGES = 12

DB_PATH = Path(__file__).parent / "chats.db"