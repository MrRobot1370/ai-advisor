from PySide6.QtCore import QObject


class BaseController(QObject):
    """Base class for all controllers with common functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def handle_error(self, error: Exception, context: str = "") -> str:
        """Common error handling logic"""
        error_msg = f"{context}: {str(error)}" if context else str(error)
        print(f"Error - {error_msg}")
        return error_msg
