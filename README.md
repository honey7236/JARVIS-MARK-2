# JARVIS Mark II - Advanced AI Desktop Assistant

JARVIS Mark II is a premium, voice-activated desktop assistant. Powered by a hybrid engine combining local automation systems, real-time web engines, and advanced language models (via the Groq API), it provides a responsive interface to control your desktop, automate daily workflows, and retrieve real-time information. It features a modern, real-time web UI powered by **Eel**, displaying telemetry data, settings panels, contact management, and interactive logs.

---

## 🚀 Core Features

### 🎙️ Voice & Speech Interface
- **Natural Speech Recognition**: Real-time voice listening with auto-calibration for ambient noise levels (dynamic energy threshold adjustments).
- **Universal Translation**: Support for multiple languages (e.g., Hindi) with automatic translation fallback into English.
- **Text-to-Speech (TTS)**: Clean, realistic neural voice generation using Microsoft Edge-TTS voices.
- **Visual Telemetry status updates**: Updates states like "Listening...", "Thinking...", "Translating..." dynamically to the UI.

### 💻 Desktop Automation & Control
- **App Management**: Open or close any local desktop application or web dashboard using fuzzy matching.
- **Smart Link Fallback**: Automatically queries Google search if an app opening fails, redirecting to the most relevant online result.
- **System Controls**: Perform system commands such as mute, unmute, volume up, volume down, and browser closures.
- **Screenshot Utility**: Instantly captures the screen and saves it straight to the user's Desktop.
- **Battery Diagnostics**: Alerts users on critical states (100% full charge, low battery warning below 20%).

### 📝 Content Writing Engine
- **Groq Integration**: Write letters, essays, notes, emails, songs, and code using high-performance models (such as `mixtral-8x7b-32768`).
- **Notepad Export**: Generated text content is saved automatically to the local disk and displayed instantly using Notepad.

### 🎨 Image Generation Subsystem
- **AI Image Creation**: Generates high-quality (4K, ultra detail) creative visuals using the Stable Diffusion XL model hosted on Hugging Face.
- **Multi-variant Output**: Automatically processes concurrent task requests, saving 4 distinct image variants and displaying them.

### 🌐 Real-Time Web Operations
- **Real-Time Search**: Search engine using fallback scraping strategies (DuckDuckGo, Google, Wikipedia) combined with Llama 3 models on Groq to present concise, fact-checked summaries.
- **YouTube Integration**: Searches for and plays specific music tracks or video links immediately using voice commands.
- **Weather Services**: Tracks weather descriptions, feels-like temperatures, humidity levels, and wind speeds using IP-based location services.
- **News Aggregation**: Fetches the latest global headlines from `gnews.io` in real time.
- **Network Speed Check**: Tracks current download speed, upload speed, latency (ping), and connectivity status in real time.

---

## 📂 Project Structure

```
JARVIS MARK 2/
├── app.py                     # Main Eel GUI controller and API endpoints
├── main.py                    # Core decision-making engine and query router
├── requirements.txt           # Python package dependencies
├── .env                       # Environment configuration file
├── backend/                   # Core business logic and integrations
│   ├── automation.py          # Main automation pipelines (system, apps, Groq)
│   ├── chat_bot.py            # Chatbot query handling (with conversation history)
│   ├── command_manager.py     # Decision-making model (DMM) for routing commands
│   ├── imagegeneration.py     # AI image generation subsystem (Stable Diffusion XL)
│   ├── realtime_search_engine.py # Scraping-based realtime search engine
│   ├── speech_to_text.py      # Voice listening and transcription
│   └── text_to_speech.py      # Neural Speech generation
├── data/                      # Data storage and configuration
│   ├── DLG_data.py            # Dialogues and pre-configured responses
│   ├── Web_Data.py            # Predefined website mappings
│   ├── contact_data.py        # Contacts data model
│   └── contacts.json          # Contacts database
├── frontend/                  # Web-based dashboard GUI (Eel / HTML / JS / CSS)
└── memory/                    # Short-term session logs and database storage
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your Windows system.

### 2. Install Dependencies
Run the command below in the project directory to install all required libraries:
```bash
pip install -r requirements.txt
```
*Note: For `SpeechRecognition` and system audio capture, ensure a working microphone and PyAudio are configured.*

### 3. Environment Configuration (`.env`)
Create a `.env` file in the root directory:
```ini
Username = User
Assistantname = JARVIS
InputLanguage = en
AssistantVoice = en-CA-LiamNeural

# API Credentials
GroqAPIKey = your_groq_api_key_here
cohere = your_cohere_key_here
HuggingFaceAPIKey = your_huggingface_api_key_here
OpenWeatherAPIKey = your_openweathermap_api_key_here
GNewsAPIKey = your_gnews_api_key_here
```

### 4. Running the Assistant
Start the application:
```bash
python app.py
```
This launches the backend systems, starts real-time network and telemetry threads, and opens the modern GUI dashboard.

---

## ⚙️ Module API & Core Functions

Here is a list of the core Python modules and their key function definitions:

### 🎮 Main Application GUI
* File: [app.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/app.py)
* **`display_weather_data()` / `get_weather_data()`**: Fetches and returns weather metrics.
* **`get_news_data()`**: Pulls general news headlines.
* **`get_system_data()` / `display_system_info_data()`**: Reads real-time hardware status metrics.
* **`get_contacts()` / `save_contact()` / `delete_contact()`**: On-screen Contact CRUD controller.
* **`get_api_keys()` / `save_api_keys()`**: Dynamically updates the `.env` settings directly from the UI settings panel.
* **`get_personal_info()` / `save_personal_info()`**: Updates Username and Assistant name configs.
* **`check_login_status()`**: Validates if the initial setup onboarding has been completed.

### 🧠 Core Execution Engine
* File: [main.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/main.py)
* **`MainExecution()`**: Runs in a loop, calls speech-to-text, queries the command manager, and executes automation, chat, or image generation tasks.
* **`QueryModifier(Query)`**: Cleans, parses, and standardizes query punctuation.

### 🎙️ Speech Processing
* File: [speech_to_text.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/speech_to_text.py)
  * **`listen()`**: Captures user microphone inputs, handles dynamic energy thresholding, and returns parsed text.
  * **`SetAssistantStatus(Status)`**: Writes telemetry status (e.g. "Listening...", "Thinking...") to disk and updates the GUI.
  * **`UniversalTranslator(Text)`**: Translates foreign speech to English.
* File: [text_to_speech.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/text_to_speech.py)
  * **`speak(Text)`**: Synthesizes and plays back neural audio responses.

### 💻 Desktop Automation & Command Router
* File: [automation.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/automation.py)
  * **`process_automation(c)`**: Routes incoming voice commands (like weather, screenshots, reminders, volume, news).
  * **`open_app(app)` / `OpenApp(app)`**: Opens local software or falls back to web searches.
  * **`CloseApp(app)`**: Closes running application windows.
  * **`play_music_on_youtube(song_name)`**: Launches YouTube query playback.
  * **`take_screenshot()`**: Captures screenshots and saves to the Desktop.
  * **`save_reminder(task, time_input)`**: Creates task notification reminders.
  * **`display_system_info()` / `get_system_stats()`**: Returns diagnostic CPU, RAM, and Disk metrics.
  * **`display_weather()` / `get_weather()`**: Pulls IP-based location and weather info.
  * **`send_whatsapp_instant(receiver, message)`**: Generates and sends WhatsApp messages via web interface.
  * **`Content(Topic)`**: Automated AI text writer that launches Notepad.
  * **`System(command)`**: Virtual keyboard simulator for system-level controls.

### 🤖 Chat & AI Engine
* File: [chat_bot.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/chat_bot.py)
  * **`ChatBot(Query)`**: Communicates with Groq (`llama-3.3-70b-versatile`) to generate conversational replies with short-term context.
* File: [realtime_search_engine.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/realtime_search_engine.py)
  * **`RealtimeSearchEngine(query)`**: Summarizes duckduckgo/google search results into brief sentences using LLMs.
* File: [imagegeneration.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/imagegeneration.py)
  * **`GenerateImages(prompt)`**: Dispatches tasks to generate and display stable diffusion AI images.

---

## 🎙️ Sample Commands

- **Applications**: `"open Chrome"`, `"close Notepad"`, `"open Facebook"`
- **Web Queries**: `"google search quantum computing"`, `"youtube search how to learn python"`
- **Entertainment**: `"play lo-fi study beats"`
- **AI Content**: `"content write a sick leave request email"`
- **System**: `"system volume up"`, `"system mute"`, `"take a screenshot"`, `"check system"`
- **Reminders**: `"reminder drink water at 6:00 pm"`
- **WhatsApp**: `"send message on whatsapp"`
- **Environment**: `"weather"`, `"news"`, `"battery status"`

---

## 🔒 License
This project is open-source and available under the MIT License.
