from typing import Iterator

from langchain_huggingface import HuggingFacePipeline

import config


def load_llm() -> HuggingFacePipeline:
    """Download (first run only) and load the model as a LangChain HuggingFacePipeline."""
    return HuggingFacePipeline.from_model_id(
        model_id=config.MODEL_ID,
        task="text-generation",
        pipeline_kwargs={
            "max_new_tokens": config.MAX_NEW_TOKENS,
            "do_sample": True,
            "temperature": config.TEMPERATURE,
            "top_p": config.TOP_P,
            "return_full_text": False,  # only return the newly generated text
        },
    )


def build_prompt(llm: HuggingFacePipeline, messages: list[dict]) -> str:
    """Turn chat messages into the model's own chat-template prompt."""
    history = messages[-config.MAX_HISTORY_MESSAGES:]
    chat = [{"role": "system", "content": config.SYSTEM_PROMPT}] + history
    tokenizer = llm.pipeline.tokenizer
    return tokenizer.apply_chat_template(
        chat, tokenize=False, add_generation_prompt=True
    )


def stream_reply(llm: HuggingFacePipeline, messages: list[dict]) -> Iterator[str]:
    """Yield the answer token-by-token (chunk-by-chunk)."""
    prompt = build_prompt(llm, messages)
    for chunk in llm.stream(prompt):
        yield chunk