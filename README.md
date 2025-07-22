 # AI Advisor
 
 [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
 [![GitHub issues](https://img.shields.io/github/issues/MrRobot1370/ai-advisor?style=flat)](https://github.com/MrRobot1370/ai-advisor/issues)
 [![GitHub release](https://img.shields.io/github/v/release/MrRobot1370/ai-advisor?style=flat)](https://github.com/MrRobot1370/ai-advisor/releases)

 AI Advisor is a cross-platform desktop application that provides a unified chat interface to interact with multiple AI model providers (OpenAI, Claude, Gemini, DeepSeek). It supports text-based chat with efficient token usage and cost-effective pay-as-you-go pricing, and can be packaged as a portable executable for Windows.

 <img width="752" height="586" alt="ai-advisor-v0 2 0" src="https://github.com/user-attachments/assets/91031bdf-9a32-477c-ad52-237abdd93d34" />

 ## Features
 
 - 💬 Chat with OpenAI, Claude, Gemini, and DeepSeek.
 - 🚀 Super efficient token usage.
 - 🔍 Compare model prices on the fly to choose the most cost-efficient provider.
 - 💰 Pay-as-you-go pricing: only pay for tokens you use, no subscriptions.
 - ⚙️ Customizable via `config/config.xml`.
 - 📦 Portable executable via PyInstaller.
 - 🎤 Voice-to-text and text-to-speech capabilities.
 - 🏗️ Professional modular architecture for easy maintenance and extensibility.
 
 ## Architecture

 The application follows a modular architecture with clear separation of concerns:

    controllers/
    ├── application_controller.py      # Main orchestrator
    ├── base/                          # Base classes and common functionality
    ├── ai/                            # AI model management and services
    ├── media/                         # Speech-to-text and text-to-speech
    └── utils/                         # Utilities (logging, clipboard)

    includes/
    ├── config/                        # Configuration management
    ├── network/                       # HTTP request handling
    ├── speech_to_text.py              # Speech recognition
    └── text_to_speech.py              # Speech synthesis
 
 ### Key Components
 
 - **AIService**: Manages AI model interactions and conversation history
 - **ModelManager**: Handles model selection and provider configuration
 - **MediaService**: Processes voice input/output operations
 - **ConfigManager**: Centralized configuration parsing and management
 - **ChatLogger**: Handles conversation logging and session tracking
 - **ClipboardManager**: Manages clipboard operations
 
 ## Requirements
 
 - Python 3.7 or higher
 - PySide6
 - requests
 - speech_recognition
 - pyttsx3
 - (Optional, for packaging) PyInstaller
 
 Install dependencies:
 
 ```bash
 pip install -r requirements.txt
 ```
 
 ## Installation
 
 ### Download a release
 
 1. Visit the [Releases](https://github.com/MrRobot1370/ai-advisor/releases) page.
 2. Download the latest `AiAdvisor` executable for your platform.
 3. Extract/unzip and run `AiAdvisor` (e.g., `AiAdvisor.exe` on Windows).
 
 ### Build from source
 
 ```bash
 git clone https://github.com/MrRobot1370/ai-advisor.git
 cd ai-advisor
 pip install -r requirements.txt
 # Configure your API keys in config/config.xml
 python main.py
 # On Windows, you can also run:
 install.bat
 ```
 
 ## Configuration
 
 Edit `config/config.xml` to add your API keys, models, timeouts (optional) and max tokens (optional). Example:
 
 ```xml
 <config>
   <OpenAI>
     <URL>https://api.openai.com/v1/chat/completions</URL>
     <KEY>YOUR_OPENAI_API_KEY</KEY>
     <MODELS>
         <MODEL name="o4-mini" timeout="90" />
         <!-- Add other models as needed -->
     </MODELS>
   </OpenAI>
   <!-- Add other providers as needed -->
 </config>
 ```
 
 ### Configuration Options

 - **timeout**: Request timeout in seconds (default: 90)
 - **max_tokens**: Maximum tokens for response (required for Claude, optional for others)
 - **Custom attributes**: Add any provider-specific attributes for future extensibility
 
 ## Usage
 
 - Launch the application.
 - Select an AI model from the dropdown.
 - Enter your message.
 - View and copy responses.
 - View used tokens to manage usage.
 - Chat history will be saved in log.txt.
 
 ## Development

 ### Project Structure
 
 The application uses a service-oriented architecture:
 
 1. **Controllers Layer**: Manages UI interactions and coordinates services
 2. **Services Layer**: Handles business logic (AI, media processing)
 3. **Configuration Layer**: Manages application settings and provider configs
 4. **Network Layer**: Handles HTTP requests and provider-specific formatting
 5. **Utilities Layer**: Provides common functionality (logging, clipboard)
 
 ### Adding New Providers
 
 1. Add provider configuration to `config.xml`
 2. Update header logic in `includes/network/request_handler.py`
 3. Add response processing logic in `controllers/ai/ai_service.py`
 
 ### Extending Functionality
 
 - **New Services**: Add to appropriate controller directory
 - **New Utilities**: Add to `controllers/utils/`
 - **Configuration Changes**: Modify `includes/config/`
 - **Network Changes**: Update `includes/network/`
 
 ## Building Executable
 
 Use PyInstaller to create a standalone executable:
 
  ```bash
 pyinstaller --noconfirm --onefile --windowed --icon "ico\brain.ico" --add-data "includes;includes/" --add-data "controllers;controllers/" --add-data "controls;controls/" --add-data "icons;icons/" --add-data "Main.qml;." main.py
 ```
 
 ## Contributing
 
 Contributions are welcome! Feel free to:
 
 1. Fork the repository
 2. Create a feature branch
 3. Follow the existing architecture patterns
 4. Add appropriate error handling
 5. Update documentation
 6. Submit a pull request
 
 Check the [issues](https://github.com/MrRobot1370/ai-advisor/issues) page for suggested features to work on.
 
 ## License
 
 This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
 
 ---
 
 *© 2025 Masoud Ghasemi*
