from typing import Dict, List, Tuple, Optional
import requests
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import Signal

from ..base import BaseController
from .model_manager import ModelManager
from includes.network import make_request


class AIService(BaseController):
    """Handles AI model interactions and conversation management"""
    
    # Signals
    responseReceived = Signal(str, str, object, str)  # response, question, tokens, model
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_manager = ModelManager(self)
        self.conversation_history: List[Dict[str, str]] = []
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    def send_question(self, question: str) -> Tuple[str, str, Optional[int], Optional[str]]:
        """Send question to AI model and get response"""
        if not self.model_manager.is_model_selected():
            return "No model is selected!", question, None, None
        
        # Add user question to history
        user_message = {"role": "user", "content": question}
        self.conversation_history.append(user_message)
        
        # Prepare payload
        payload = {
            "model": self.model_manager.current_model,
            "messages": self.conversation_history.copy()
        }
        
        try:
            provider_cfg, model_cfg = self.model_manager.get_provider_config(
                self.model_manager.current_model
            )
            
            response = make_request(
                provider_cfg, model_cfg, self.model_manager.current_model, payload
            )
            response.raise_for_status()
            
        except requests.exceptions.Timeout:
            self.conversation_history.pop()  # Remove failed question
            return "Request timed out!", question, None, None
        except requests.exceptions.RequestException as e:
            self.conversation_history.pop()
            try:
                if hasattr(response, 'json') and 'error' in response.json():
                    error_msg = response.json()['error']['message']
                else:
                    error_msg = f"A request error occurred: {e}"
            except:
                error_msg = f"A request error occurred: {e}"
            return error_msg, question, None, None
        except Exception as e:
            self.conversation_history.pop()
            return self.handle_error(e, "AI service error"), question, None, None
        
        return self._process_response(response, question)
    
    def _process_response(self, response: requests.Response, question: str) -> Tuple[str, str, Optional[int], Optional[str]]:
        """Process the API response based on provider type"""
        if response.status_code != 200:
            self.conversation_history.pop()
            return f"Error code: {response.status_code}", question, None, None
        
        try:
            json_data = response.json()
            
            # Handle different provider response formats
            if 'choices' in json_data:  # OpenAI/DeepSeek
                content = json_data['choices'][0]['message']['content']
                tokens = json_data['usage']['total_tokens']
                model = json_data['model']
                
            elif 'content' in json_data:  # Claude
                content = json_data['content'][0]['text']
                input_tokens = json_data['usage']['input_tokens']
                output_tokens = json_data['usage']['output_tokens']
                tokens = input_tokens + output_tokens
                model = json_data['model']
                
            elif 'candidates' in json_data:  # Gemini
                content = json_data['candidates'][0]['content']['parts'][0]['text']
                tokens = json_data.get('usageMetadata', {}).get('totalTokenCount', 0)
                model = json_data.get('model', 'gemini')
                
            elif 'error' in json_data:
                self.conversation_history.pop()
                return json_data['error']['message'], question, None, None
                
            else:
                self.conversation_history.pop()
                return "Unknown response format", question, None, None
            
            # Add assistant response to history
            assistant_message = {"role": "assistant", "content": content}
            self.conversation_history.append(assistant_message)
            
            return content, question, tokens, model
            
        except Exception as e:
            self.conversation_history.pop()
            return self.handle_error(e, "Failed to process response"), question, None, None
    
    def send_question_async(self, question: str, callback):
        """Send question asynchronously"""
        future = self.executor.submit(self.send_question, question)
        future.add_done_callback(callback)
        return future
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history.clear()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get current conversation history"""
        return self.conversation_history.copy()
