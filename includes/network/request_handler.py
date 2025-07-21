from typing import Dict, Tuple
import re
import requests

from ..config.models import ProviderConfig, ModelConfig


def make_headers(provider: ProviderConfig, model_name: str) -> Dict[str, str]:
    """
    Return the HTTP header dict required for the provider/model combination.
    Tries to keep the old heuristics intact.
    """
    key = provider.key
    lower_name = model_name.lower()

    if "claude" in lower_name:                         # Anthropic
        return {
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        }
    if "gemini" in lower_name:                         # Google
        return {"Content-Type": "application/json"}
    if "gpt" in lower_name or re.match(r"^o\d", model_name):
        return {                                       # OpenAI family
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }
    if "deepseek" in lower_name:                       # DeepSeek
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        }

    raise ValueError(f"Could not determine headers for model '{model_name}'")


def make_request(provider_cfg: ProviderConfig, model_cfg: ModelConfig, 
                model_name: str, payload: dict) -> requests.Response:
    """
    Make HTTP request to the appropriate provider endpoint.
    """
    headers = make_headers(provider_cfg, model_name)
    data_to_send: dict = payload

    if "claude" in model_name.lower():
        # For Anthropic the field is mandatory
        data_to_send = payload.copy()
        data_to_send["max_tokens"] = model_cfg.max_tokens

    elif "gemini" in model_name.lower():
        # Different endpoint & body structure
        url = (
            f"{provider_cfg.url}{model_name}:generateContent"
            f"?key={provider_cfg.key}"
        )
        gemini_contents = [
            {
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [{"text": m["content"]}],
            }
            for m in payload["messages"]
        ]
        data_to_send = {"contents": gemini_contents}
        return requests.post(
            url, headers=headers, json=data_to_send, timeout=model_cfg.timeout
        )

    # All "OpenAI-ish" endpoints (OpenAI, DeepSeek, …) go here
    return requests.post(
        provider_cfg.url,
        headers=headers,
        json=data_to_send,
        timeout=model_cfg.timeout,
    )
