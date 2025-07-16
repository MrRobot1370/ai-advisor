from includes import speechToText as stt
from includes import textToSpeech as tts

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple

import re
import requests
import xml.etree.ElementTree as ET
import sys

from PySide6.QtCore import QObject, Slot, Signal, Property, QDateTime, Qt
from PySide6.QtGui import QGuiApplication
from concurrent.futures import ThreadPoolExecutor

# Configuration handling
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


# Helpers
def _resource_root() -> Path:
    """
    Absolute path of the folder that contains our *resources* (config/, …).

    • When running from a PyInstaller bundle → <bundle>/config
    • When running from source                 → <project>/config
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _parse_config_xml(xml_path: Path) -> Tuple[Dict[str, ProviderConfig], List[str]]:
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

payload = {
    "model": "",
    "messages": []
}

CONFIG_FILE = _resource_root() / "config" / "config.xml"
PROVIDERS, AVAILABLE_MODELS = _parse_config_xml(CONFIG_FILE)


# Generic request helper
def _make_headers(provider: ProviderConfig, model_name: str) -> Dict[str, str]:
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


def _find_provider(model_name: str) -> Tuple[ProviderConfig, ModelConfig]:
    """
    Locate the provider and model configuration for *model_name*.
    """
    for provider in PROVIDERS.values():
        if model_name in provider.models:
            return provider, provider.models[model_name]
    raise KeyError(f"Model '{model_name}' not found in configuration.")


def postRequest(model_name: str, payload: dict) -> requests.Response:
    """
    One single entry point that dispatches the request to the right provider.

    • Uses the per-model timeout / max_tokens settings from config.xml
    • Converts Gemini payloads automatically
    """
    provider_cfg, model_cfg = _find_provider(model_name)
    headers = _make_headers(provider_cfg, model_name)

    # Provider specific preparation
    data_to_send: dict = payload

    """
    Hint about other future providers
       • If a new provider requires the max_tokens value, add another `elif` branch similar to the Claude block.
    """
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

    #print(f'data_to_send: {data_to_send}')
    # All “OpenAI-ish” endpoints (OpenAI, DeepSeek, …) go here
    return requests.post(
        provider_cfg.url,
        headers=headers,
        json=data_to_send,
        timeout=model_cfg.timeout,
    )

# Open file for writing chat history
filename = "log.txt"
# get the current date and time
now = QDateTime.currentDateTime()
# format the date and time to a readable string
date_time_str = now.toString(Qt.ISODate)
date_time_obj = QDateTime.fromString(date_time_str, Qt.ISODate)
readable_date_time_str = date_time_obj.toString("dd.MM.yyyy hh:mm:ss")
with open(filename, "a") as f:
    # Write initial string
    f.write("********************* New Session " + readable_date_time_str + " *********************\n")

class ApplicationController(QObject):
    def __init__(self, parent=None):
            super().__init__(parent)
            # initialize parameters
            self._answerText = ""
            self._questionText = ""
            self._numTokens = 0
            self._modelIndex = 0
            self._availableModels = AVAILABLE_MODELS
            # create connection
            self.postModelIndex.connect(self.setActiveModel)

    # Define tasks =============================================
    def sendQuestion(self, param):
        if self.modelIndex < 1:
            msg = "No model is selected!"
            #print(msg)
            return msg, param, None, None

        userQuestion = {"role": "user", "content": param}
        payload["messages"].append(userQuestion)
        #print(payload)

        try:
            currentModel = self.availableModels[self.modelIndex]
            response = postRequest(currentModel, payload)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            payload["messages"].pop()
            return "Request timed out!", param, None, None
        except requests.exceptions.RequestException as e:
            if 'error' in response.json():
                errMsg = response.json()['error']['message']
            else:
                errMsg = str(f"A request error occurred: {e}")
            payload["messages"].pop()
            return errMsg, param, None, None
        except ValueError as e:
            payload["messages"].pop()
            return str(f"A value error occurred: {e}"), param, None, None
        except KeyError as e:
            payload["messages"].pop()
            return str(f"A key error occurred: {e}"), param, None, None

        # json_data = response.json()
        # print(json.dumps(json_data, indent=4))
        numTokens = None
        selectedModel = None
        if response.status_code == 200:
            if 'choices' in response.json(): # gpt/deepseek answer
                context = response.json()['choices'][0]['message']['content']
                payload["messages"].append({"role": "assistant", "content": context})
                numTokens = response.json()['usage']['total_tokens']
                selectedModel = response.json()['model']
            elif 'content' in response.json(): # claude answer
                context = response.json()['content'][0]['text']
                payload["messages"].append({"role": "assistant", "content": context})
                inputTokens = response.json()['usage']['input_tokens']
                outputTokens = response.json()['usage']['output_tokens']
                numTokens = inputTokens + outputTokens
                selectedModel = response.json()['model']
            elif 'candidates' in response.json(): # gemini answer
                context = response.json()['candidates'][0]['content']['parts'][0]['text']
                payload["messages"].append({"role": "assistant", "content": context})
                # Check for usageMetadata which might not always be present
                if 'usageMetadata' in response.json():
                    numTokens = response.json()['usageMetadata']['totalTokenCount']
                else: # Fallback if usage metadata is not in response
                    numTokens = 0
                selectedModel = response.json().get('model', 'gemini')
            elif 'error' in response.json():
                context = response.json()['error']['message']
                # Remove the user question since there was an error
                payload["messages"].pop()
            else:
                context = "Unknown response received"
                payload["messages"].pop()
        else:
            context = f"Error code: {response.status_code}"
            payload["messages"].pop()

        return context, param, numTokens, selectedModel

    def answerReceived(self, future):
        context, param, numTokens, selectedModel = future.result()
        self.answerText = context

        if param is None or numTokens is None or selectedModel is None:
            self.executionDone.emit(True)
            return

        self.numTokens = numTokens
        with open(filename, "a", encoding="utf-8") as f:
            f.write("* User:\n" + param + "\n\n")
            f.write("* Advisor (" + selectedModel + ")" + ":\n" + context + "\n\n")
            f.write("* Total used tokens:\n" + str(numTokens) + "\n---------------------------------------\n")
        self.executionDone.emit(True)
        pass

    def processText(self, param):
        tts.textToSpeech(param)

    def textConverted(self, future):
        self.voiceProcessed.emit()
        self.executionDone.emit(True)
        pass

    def processVoice(self):
        param = stt.speechToText()[10:]

        return param

    def voiceConverted(self, future):
        param = future.result()
        self.postQuestion.emit(param)
        self.questionText = param
        self.executionDone.emit(True)
        pass

    # Define signals =============================================
    postAnswer = Signal(str)
    postQuestion = Signal(str)
    postNumTokens = Signal(int)
    postModelIndex = Signal(int)
    postAvailableModels = Signal(list)
    executionDone = Signal(bool)
    voiceProcessed = Signal()

    # Define slots =============================================
    @Slot(str)
    def getQuestion(self, param):
        self.executionDone.emit(False)
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.sendQuestion, param)
        future.add_done_callback(self.answerReceived)

    @Slot()
    def convertVoiceToText(self) :
        self.executionDone.emit(False)
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.processVoice)
        future.add_done_callback(self.voiceConverted)

    @Slot(str)
    def convertTextToVoice(self, param):
        self.executionDone.emit(False)
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.processText, param)
        future.add_done_callback(self.textConverted)

    @Slot(str)
    def setActiveModel(self, param):
        payload["model"] = self.availableModels[param]

    @Slot(str)
    def resetHistory(self, param):
        payload["messages"].clear()
        with open(filename, "a") as f:
            f.write("\n" + param + "\n\n")

    @Slot(str)
    def copyToClipboard(self, text):
        try:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(str(text))
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

    # Define properties =============================================
    @Property(str, notify=postAnswer)
    def answerText(self):
        return self._answerText

    @Property(str, notify=postQuestion)
    def questionText(self):
        return self._questionText

    @Property(int, notify=postNumTokens)
    def numTokens(self):
        return self._numTokens

    @Property(list, notify=postAvailableModels)
    def availableModels(self):
        return self._availableModels

    @Property(int, notify=postModelIndex)
    def modelIndex(self):
        return self._modelIndex

    # Define setters =============================================
    @answerText.setter
    def answerText(self, value):
        self._answerText = value
        self.postAnswer.emit(value)

    @questionText.setter
    def questionText(self, value):
        if self._questionText != value:
            self._questionText = value
            self.postQuestion.emit(value)

    @numTokens.setter
    def numTokens(self, value):
        self._numTokens = value
        self.postNumTokens.emit(value)

    @availableModels.setter
    def availableModels(self, value):
        if self._availableModels != value:
            self._availableModels = value
            self.postAvailableModels.emit(value)

    @modelIndex.setter
    def modelIndex(self, value):
        if self._modelIndex != value:
            self._modelIndex = value
            self.postModelIndex.emit(value)
