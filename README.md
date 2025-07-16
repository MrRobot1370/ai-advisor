 # AI Advisor
 
 [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
 [![GitHub issues](https://img.shields.io/github/issues/MrRobot1370/ai-advisor?style=flat)](https://github.com/MrRobot1370/ai-advisor/issues)
 [![GitHub release](https://img.shields.io/github/v/release/MrRobot1370/ai-advisor?style=flat)](https://github.com/MrRobot1370/ai-advisor/releases)

 AI Advisor is a cross-platform desktop application that provides a unified chat interface to interact with multiple AI model providers (OpenAI, Claude, Gemini, DeepSeek). It supports text-based chat with efficient token usage and cost-effective pay-as-you-go pricing, and can be packaged as a portable executable for Windows.

<img width="752" height="586" alt="ai-advisor-v0 1 0" src="https://github.com/user-attachments/assets/7f5f4ccf-3805-404a-8ce4-f6bb5a5c7665" />

 ## Features
 
 - 💬 Chat with OpenAI, Claude, Gemini, and DeepSeek.
 - 🚀 Super efficient token usage.
 - 🔍 Compare model prices on the fly to choose the most cost-efficient provider.
 - 💰 Pay-as-you-go pricing: only pay for tokens you use, no subscriptions.
 - ⚙️ Customizable via `config/config.xml`.
 - 📦 Portable executable via PyInstaller.
 
 ## Requirements
 
 - Python 3.7 or higher
 - PySide6
 - requests
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
 
 ## Usage
 
 - Launch the application.
 - Select an AI model from the dropdown.
 - Enter your message.
 - View and copy responses.
 - View used tokens to manage usage.
 - Chat history will be saved in log.txt.
 
 ## Contributing
 
 Contributions are welcome! Feel free to:
 
 - Open an issue to report bugs or request features.
 - Submit a pull request with improvements or new features.
 
 Check the [issues](https://github.com/MrRobot1370/ai-advisor/issues) page for suggested features to work on.
 
 ## License
 
 This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
 
 ---
 
 *© 2025 Masoud Ghasemi*
