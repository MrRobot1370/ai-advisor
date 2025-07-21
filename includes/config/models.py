from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class ModelConfig:
    """
    Per-model run-time settings extracted from config.xml
    (timeout, max_tokens … may grow in the future).
    """
    name: str
    timeout: int
    max_tokens: int
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderConfig:
    """
    API provider definition (OpenAI / Claude / …) plus all of its models.
    """
    name: str
    url: str
    key: str
    models: Mapping[str, ModelConfig]
