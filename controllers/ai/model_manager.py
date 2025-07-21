from typing import Dict, List
from PySide6.QtCore import Signal

from ..base import BaseController
from includes.config import ConfigManager


class ModelManager(BaseController):
    """Manages AI model selection and configuration"""
    
    # Signals
    modelChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self._current_model = ""
        self._model_index = 0
    
    @property
    def available_models(self) -> List[str]:
        """Get list of available models"""
        return self.config_manager.get_available_models()
    
    @property
    def current_model(self) -> str:
        """Get currently selected model"""
        return self._current_model
    
    @property
    def model_index(self) -> int:
        """Get current model index"""
        return self._model_index
    
    def set_model_by_index(self, index: int) -> bool:
        """Set active model by index"""
        try:
            if 0 <= index < len(self.available_models):
                self._model_index = index
                self._current_model = self.available_models[index]
                self.modelChanged.emit(self._current_model)
                return True
            return False
        except Exception as e:
            self.handle_error(e, "Failed to set model")
            return False
    
    def get_provider_config(self, model_name: str):
        """Get provider configuration for a model"""
        return self.config_manager.find_provider(model_name)
    
    def is_model_selected(self) -> bool:
        """Check if a valid model is selected"""
        return self._model_index > 0
