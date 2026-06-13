"""Tiny wrapper around the local Ollama HTTP API.

We use the /api/chat endpoint with a single user message and no system
prompt, so we measure each model's *default* safety behaviour.
"""
import requests

import config


def chat(model: str, user_msg: str, system_msg: str | None = None) -> str:
    """Send one message to a model and return the text answer."""
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": config.TEMPERATURE,
            "seed": config.SEED,
            "num_predict": config.NUM_PREDICT,
        },
    }
    resp = requests.post(
        f"{config.OLLAMA_URL}/api/chat",
        json=payload,
        timeout=config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()
