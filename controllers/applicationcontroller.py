from includes import speechToText as stt
from includes import textToSpeech as tts

import re
import requests
import xml.etree.ElementTree as ET
import sys, os

from PySide6.QtCore import QObject, Slot, Signal, Property, QDateTime, Qt
from PySide6.QtGui import QGuiApplication
from concurrent.futures import ThreadPoolExecutor

def get_base_path():
    """
    Return the folder where our EXE or script actually lives.
    - When running under PyInstaller (frozen), __file__ lives in a temp
      directory.  sys.executable is the real EXE path.
    - When running as a normal script, __file__ shows you your source
      tree.  We go one level up to find the config/ folder.
    """
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running in IDE / plain python
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to config.xml
base = get_base_path()
config_path = os.path.join(base, 'config', 'config.xml')
if not os.path.exists(config_path):
    raise Exception(f"Configuration file not found at: {config_path}")

# Parse the XML file
try:
    tree = ET.parse(config_path)
except ET.ParseError as e:
    raise Exception(f"Failed to parse XML ({config_path}): {e}")

root = tree.getroot()
configurations = {}
available_models = []
for element in root:
    name = element.tag
    try:
        url_node     = element.find('URL')
        key_node     = element.find('KEY')
        model_node   = element.find('MODEL')
        timeout_node = element.find('TIMEOUT')

        if None in (url_node, key_node, model_node, timeout_node):
            missing = [t for t,n in
                       (('URL',url_node),('KEY',key_node),
                        ('MODEL',model_node),('TIMEOUT',timeout_node))
                       if n is None]
            raise Exception(f"Missing tag(s) {missing} under <{name}>")

        url     = url_node.text.strip()
        key     = key_node.text.strip()
        models  = [m.strip() for m in model_node.text.split(',') if m.strip()]
        timeout = int(timeout_node.text) # may ValueError

    except ValueError:
        raise Exception(f"Invalid TIMEOUT value under <{name}>; must be an integer")
    except Exception as e:
        raise Exception(f"Error processing <{name}>: {e}")

    available_models.extend(models)
    configurations[name] = {
        'URL':     url,
        'KEY':     key,
        'MODEL':   models,
        'TIMEOUT': timeout
    }

payload = {
    "model": "",
    "messages": []
}

# Open file for writing chat history
filename = "history.txt"

# get the current date and time
now = QDateTime.currentDateTime()
# format the date and time to a readable string
date_time_str = now.toString(Qt.ISODate)
date_time_obj = QDateTime.fromString(date_time_str, Qt.ISODate)
readable_date_time_str = date_time_obj.toString("dd.MM.yyyy hh:mm:ss")
with open(filename, "a") as f:
    # Write initial string
    f.write("********************* " + readable_date_time_str + " *********************\n")

AVAILABLE_MODELS = ['select model']
for config in configurations.values():
    AVAILABLE_MODELS.extend(config['MODEL'])

    def check_model(model_name):
        pattern = r'^o\d'
        return bool(re.match(pattern, models))

def postRequest(model, payload):
    for name, config in configurations.items():
        if model in config['MODEL']:
            oModelsPattern = r'^o\d'
            if "gpt" in model or bool(re.match(oModelsPattern, model)):
                if "max_tokens" in payload:
                    del payload["max_tokens"]
                headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['KEY']}"
                }
            elif "claude" in model:
                if "sonnet" in model.lower() or "opus" in model.lower():
                    payload['max_tokens'] = 8192
                else:
                    payload['max_tokens'] = 4096
                headers = {
                "Content-Type": "application/json",
                "x-api-key": config['KEY'],
                "anthropic-version": "2023-06-01"
                }
            elif "deepseek" in model:
                headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['KEY']}"
                }
            elif "gemini" in model:
                headers = {
                    "Content-Type": "application/json"
                }
                # Gemini requires a different payload structure ("contents")
                # We need to transform the "messages" history to "contents"
                gemini_contents = []
                for message in payload["messages"]:
                    # Map roles: 'assistant' becomes 'model'
                    role = "model" if message["role"] == "assistant" else "user"
                    gemini_contents.append({
                        "role": role,
                        "parts": [{"text": message["content"]}]
                    })
                gemini_payload = {"contents": gemini_contents}
                # Gemini API URL includes the model and action
                url = f"{config['URL']}{model}:generateContent?key={config['KEY']}"
                return requests.post(url=url, headers=headers, json=gemini_payload, timeout=config['TIMEOUT'])
            else:
                raise ValueError(f"Selected model is invalid: {model}")

            return requests.post(url=config['URL'], headers=headers, json=payload, timeout=config['TIMEOUT'])

    raise KeyError(f"No configuration was found for the selected model: {model}")

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
            payload["messages"].pop()
            return str(f"A request error occurred: {e}"), param, None, None
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
