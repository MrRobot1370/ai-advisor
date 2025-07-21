from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import Signal

from ..base import BaseController
from includes import speechToText as stt
from includes import textToSpeech as tts


class MediaService(BaseController):
    """Handles speech-to-text and text-to-speech operations"""
    
    # Signals
    voiceProcessed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    def convert_speech_to_text(self) -> str:
        """Convert speech input to text"""
        try:
            result = stt.speechToText()
            # Remove the "You said: " prefix if present
            return result[10:] if result.startswith("You said: ") else result
        except Exception as e:
            return self.handle_error(e, "Speech to text conversion failed")
    
    def convert_text_to_speech(self, text: str):
        """Convert text to speech output"""
        try:
            tts.textToSpeech(text)
        except Exception as e:
            self.handle_error(e, "Text to speech conversion failed")
    
    def process_voice_async(self, callback):
        """Process voice input asynchronously"""
        future = self.executor.submit(self.convert_speech_to_text)
        future.add_done_callback(callback)
        return future
    
    def process_speech_async(self, text: str, callback):
        """Process text-to-speech asynchronously"""
        future = self.executor.submit(self.convert_text_to_speech, text)
        future.add_done_callback(callback)
        return future
