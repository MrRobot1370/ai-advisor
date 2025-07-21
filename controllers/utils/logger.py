from pathlib import Path
from PySide6.QtCore import QDateTime, Qt


class ChatLogger:
    """Handles chat history logging"""
    
    def __init__(self, log_file: str = "log.txt"):
        self.log_file = log_file
        self._initialize_log()
    
    def _initialize_log(self):
        """Initialize log file with session header"""
        now = QDateTime.currentDateTime()
        date_time_str = now.toString(Qt.ISODate)
        date_time_obj = QDateTime.fromString(date_time_str, Qt.ISODate)
        readable_date_time_str = date_time_obj.toString("dd.MM.yyyy hh:mm:ss")
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"********************* New Session {readable_date_time_str} *********************\n")
    
    def log_conversation(self, user_input: str, ai_response: str, 
                        model_name: str, token_count: int):
        """Log a complete conversation exchange"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("* User:\n" + user_input + "\n\n")
            f.write("* Advisor (" + model_name + ")" + ":\n" + ai_response + "\n\n")
            f.write("* Total used tokens:\n" + str(token_count) + "\n---------------------------------------\n")
    
    def log_event(self, message: str):
        """Log a general event"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n" + message + "\n\n")
