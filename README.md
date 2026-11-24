# HF Chatbot

Streamlit chatbot built with LangChain's `HuggingFacePipeline`.

## Features
- Free Hugging Face model (Qwen2.5-0.5B-Instruct), runs on CPU
- Live streaming replies
- Chat history saved to disk, resume any chat after restart or refresh

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Project structure
- `app.py`: Streamlit frontend
- `backend.py`: model loading and streaming
- `storage.py`: saves/loads chats as JSON
- `config.py`: settings