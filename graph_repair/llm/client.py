from __future__ import annotations

import logging
from typing import Union

from ollama import Client as OllamaClient
from openai import OpenAI

import config


def get_llm_client() -> Union[OpenAI, OllamaClient]:
    provider = config.LLM_PROVIDER.lower()

    if provider == "lm-studio":
        try:
            return OpenAI(
                base_url=f"{config.LM_STUDIO_HOST}/v1",
                api_key="lm-studio",
            )
        except Exception as exc:
            logging.exception("Failed connection to LM Studio")
            raise RuntimeError(
                f"Failed to connect to LM Studio at {config.LM_STUDIO_HOST}. "
                "Make sure LM Studio is running with a model loaded."
            ) from exc

    try:
        return OllamaClient(host=config.OLLAMA_HOST, headers=config.OLLAMA_AUTH_HEADER)
    except Exception as exc:
        logging.exception("Failed connection to Ollama")
        raise RuntimeError(
            f"Failed to connect to Ollama at {config.OLLAMA_HOST}. "
            "Check OLLAMA_HOST and OLLAMA_BEARER_TOKEN."
        ) from exc


def stream_chat_text(prompt: str) -> str:
    client = get_llm_client()
    provider = config.LLM_PROVIDER.lower()
    messages = [{"role": "user", "content": prompt}]
    output = ""

    if provider == "lm-studio":
        create_kwargs: dict = {
            "model": config.LM_STUDIO_MODEL,
            "messages": messages,
            "stream": True,
        }
        if config.LLM_SEED is not None:
            create_kwargs["seed"] = config.LLM_SEED
            create_kwargs["temperature"] = 0.0
        stream = client.chat.completions.create(**create_kwargs)
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                output += content
                print(content, end="", flush=True)
        print()
        return output.strip()

    ollama_kwargs: dict = {}
    if config.LLM_SEED is not None:
        ollama_kwargs["options"] = {"seed": config.LLM_SEED, "temperature": 0.0}
    for part in client.chat(config.OLLAMA_MODEL, messages=messages, stream=True, **ollama_kwargs):
        content = part["message"]["content"]
        output += content
        print(content, end="", flush=True)
    print()
    return output.strip()

