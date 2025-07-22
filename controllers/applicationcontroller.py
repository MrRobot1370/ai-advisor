from PySide6.QtCore import QObject, Slot, Signal, Property
from concurrent.futures import ThreadPoolExecutor

from .base import BaseController
from .ai import AIService
from .media import MediaService
from .utils import ChatLogger, ClipboardManager


class ApplicationController(BaseController):
    """Main application controller that orchestrates all services"""

    # Define signals
    postAnswer = Signal(str)
    postQuestion = Signal(str)
    postNumTokens = Signal(int)
    postModelIndex = Signal(int)
    postAvailableModels = Signal(list)
    executionDone = Signal(bool)
    voiceProcessed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize services
        self.ai_service = AIService(self)
        self.media_service = MediaService(self)
        self.logger = ChatLogger()
        self.clipboard_manager = ClipboardManager()

        # Initialize properties - keep local copies for QML binding
        self._answerText = ""
        self._questionText = ""
        self._numTokens = 0
        self._modelIndex = self.ai_service.model_manager.model_index
        self._availableModels = self.ai_service.model_manager.available_models

        # Connect internal signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect internal service signals"""
        self.postModelIndex.connect(self._on_model_index_changed)
        self.ai_service.model_manager.modelChanged.connect(self._on_model_changed)

    # Slots for external QML interface
    @Slot(str)
    def getQuestion(self, question: str):
        """Handle question from UI"""
        self.executionDone.emit(False)
        future = self.ai_service.send_question_async(question, self._on_answer_received)

    @Slot()
    def convertVoiceToText(self):
        """Convert voice input to text"""
        self.executionDone.emit(False)
        future = self.media_service.process_voice_async(self._on_voice_converted)

    @Slot(str)
    def convertTextToVoice(self, text: str):
        """Convert text to speech"""
        self.executionDone.emit(False)
        future = self.media_service.process_speech_async(text, self._on_text_converted)

    @Slot(str)
    def setActiveModel(self, index_str: str):
        """Set active model by index"""
        try:
            index = int(index_str)
            if self.ai_service.model_manager.set_model_by_index(index):
                self.modelIndex = index  # This will trigger the setter and signal
        except ValueError:
            self.handle_error(ValueError("Invalid model index"), "Model selection")

    @Slot(str)
    def resetHistory(self, message: str):
        """Reset conversation history"""
        self.ai_service.clear_conversation_history()
        self.logger.log_event(message)

    @Slot(str)
    def copyToClipboard(self, text: str):
        """Copy text to clipboard"""
        self.clipboard_manager.copy_to_clipboard(text)

    # Callback methods
    def _on_answer_received(self, future):
        """Handle AI response"""
        try:
            response, question, tokens, model = future.result()
            self.answerText = response

            if tokens is not None and model is not None:
                self.numTokens = tokens
                self.logger.log_conversation(question, response, model, tokens)

        except Exception as e:
            self.answerText = self.handle_error(e, "Failed to process AI response")
        finally:
            self.executionDone.emit(True)

    def _on_voice_converted(self, future):
        """Handle voice-to-text conversion"""
        try:
            text = future.result()
            self.questionText = text
            self.postQuestion.emit(text)
        except Exception as e:
            self.handle_error(e, "Voice conversion failed")
        finally:
            self.executionDone.emit(True)

    def _on_text_converted(self, future):
        """Handle text-to-speech conversion"""
        try:
            future.result()  # Check for exceptions
            self.voiceProcessed.emit()
        except Exception as e:
            self.handle_error(e, "Speech synthesis failed")
        finally:
            self.executionDone.emit(True)

    def _on_model_index_changed(self, index: int):
        """Handle model index change from postModelIndex signal"""
        # Update the service when the signal is emitted
        self.ai_service.model_manager.set_model_by_index(index)

    def _on_model_changed(self, model_name: str):
        """Handle model change from service"""
        # Sync the local model index when service changes
        try:
            new_index = self._availableModels.index(model_name)
            if new_index != self._modelIndex:
                self._modelIndex = new_index
                self.postModelIndex.emit(new_index)
        except ValueError:
            pass  # Model name not found in list

    # Properties
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

    # Setters - restored the missing setters
    @answerText.setter
    def answerText(self, value):
        if self._answerText != value:
            self._answerText = value
            self.postAnswer.emit(value)

    @questionText.setter
    def questionText(self, value):
        if self._questionText != value:
            self._questionText = value
            self.postQuestion.emit(value)

    @numTokens.setter
    def numTokens(self, value):
        if self._numTokens != value:
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
