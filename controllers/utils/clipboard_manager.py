from PySide6.QtGui import QGuiApplication


class ClipboardManager:
    """Handles clipboard operations"""
    
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """Copy text to clipboard. Returns True if successful."""
        try:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(str(text))
            return True
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False
