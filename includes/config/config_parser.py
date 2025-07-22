from pathlib import Path
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET
import sys

from .models import ModelConfig, ProviderConfig


def get_resource_root() -> Path:
    """
    Absolute path of the folder that contains our *resources* (config/, …).

    • When running from a PyInstaller bundle → <bundle>/config
    • When running from source                 → <project>/config
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def parse_config_xml(xml_path: Path) -> Tuple[Dict[str, ProviderConfig], List[str]]:
    """
    Parse config.xml and create an index that maps …

        provider-name → ProviderConfig
                     ↳ model-name    → ModelConfig
    """
    if not xml_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {xml_path}")

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        raise RuntimeError(f"Failed to parse {xml_path}: {exc}") from exc

    providers: Dict[str, ProviderConfig] = {}
    model_dropdown: List[str] = ["select model"]     # GUI helper

    for provider_el in tree.getroot():
        provider_name = provider_el.tag

        url = (provider_el.findtext("URL") or "").strip()
        key = (provider_el.findtext("KEY") or "").strip()
        if not url or not key:
            raise ValueError(f"<{provider_name}> needs <URL> and <KEY> tags")

        models_el = provider_el.find("MODELS")
        if models_el is None:
            raise ValueError(f"<{provider_name}> is missing the <MODELS> section")

        model_cfgs: Dict[str, ModelConfig] = {}
        for model_el in models_el.findall("MODEL"):
            model_name = (model_el.get("name") or "").strip()
            if not model_name:
                raise ValueError(
                    f"A <MODEL> entry under <{provider_name}> has no name"
                )

            # mandatory attributes with sane fallbacks
            try:
                timeout = int(model_el.get("timeout", 90))
                max_tokens = int(model_el.get("max_tokens", 4096))
            except ValueError as exc:
                raise ValueError(
                    f'Non-integer attribute in <MODEL name="{model_name}">'
                ) from exc

            # collect any additional attributes (future proof)
            extras: Dict[str, str] = {
                k: v for k, v in model_el.attrib.items()
                if k not in {"name", "timeout", "max_tokens"}
            }

            cfg = ModelConfig(
                name=model_name,
                timeout=timeout,
                max_tokens=max_tokens,
                extra=extras,
            )
            model_cfgs[model_name] = cfg
            model_dropdown.append(model_name)

        providers[provider_name] = ProviderConfig(
            name=provider_name,
            url=url,
            key=key,
            models=model_cfgs,
        )

    return providers, model_dropdown


class ConfigManager:
    """Central configuration manager"""
    
    def __init__(self):
        self.config_file = get_resource_root() / "config" / "config.xml"
        self.providers, self.available_models = parse_config_xml(self.config_file)
    
    def get_providers(self) -> Dict[str, ProviderConfig]:
        return self.providers
    
    def get_available_models(self) -> List[str]:
        return self.available_models
    
    def find_provider(self, model_name: str) -> Tuple[ProviderConfig, ModelConfig]:
        """Locate the provider and model configuration for *model_name*."""
        for provider in self.providers.values():
            if model_name in provider.models:
                return provider, provider.models[model_name]
        raise KeyError(f"Model '{model_name}' not found in configuration.")
