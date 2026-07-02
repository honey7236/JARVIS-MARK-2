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
├── .env                       # Environment configuration file (automatically generated or user-configured)
├── JARVIS_Mark_II.spec        # PyInstaller specification file for compilation
├── installer.iss              # Inno Setup packaging script for creating a Windows Installer
├── backend/                   # Core business logic and integrations
│   ├── automation.py          # Main automation pipelines (system, apps, Groq)
│   ├── chat_bot.py            # Chatbot query handling (with conversation history)
│   ├── command_manager.py     # Decision-making model (DMM) for routing commands
│   ├── config_manager.py      # Thread-safe configuration loader with Local AppData write fallback
│   ├── data_manager.py        # Safe atomic JSON/text file I/O operations and Local AppData path resolver
│   ├── groq_client.py         # Groq API client wrapper supporting transparent API key rotation
│   ├── image_generation.py    # AI image generation subsystem (Stable Diffusion XL via Hugging Face)
│   ├── realtime_search_engine.py # Scraping-based realtime search engine using Llama 3 on Groq
│   ├── speech_to_text.py      # Voice listening, energy thresholding, and transcription
│   ├── text_to_speech.py      # Neural speech generation using Edge-TTS
│   └── updater.py             # Automatic update subsystem integrating with GitHub Releases API
├── data/                      # Data storage and configuration
│   ├── chatlog.json           # Local chat history log
│   ├── contact_data.py        # Contacts data structure model
│   ├── contacts.json          # Contacts database
│   ├── dlg_data.py            # Custom dialog patterns and voice line structures
│   ├── music_library.py       # Predefined local and YouTube music routes
│   └── web_data.py            # Custom website shortcuts and query structures
└── frontend/                  # Web-based dashboard GUI (Eel / HTML / JS / CSS)
```

---

## 🛠️ Setup & Installation

### Option 1: Developer Setup (Running from Source)

#### 1. Prerequisites
- **OS**: Windows (Required for desktop automation hooks and system APIs).
- **Python**: Python 3.9 or higher.
- **Hardware**: Working microphone and audio output.

#### 2. Clone the Repository
```bash
git clone https://github.com/honey7236/JARVIS-MARK-2.git
cd "JARVIS MARK 2"
```

#### 3. Set Up Virtual Environment (Recommended)
Set up a clean virtual environment using PowerShell or Command Prompt:
```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### 4. Install Dependencies
Run the command below to install all required libraries:
```powershell
pip install -r requirements.txt
```
> [!NOTE]
> PyAudio compilation might require Visual Studio Build Tools with C++ desktop workload on Windows if precompiled wheels are not cached.

#### 5. Environment Configuration
Create a `.env` file in the root directory (or let the onboarding interface generate it automatically on your first run).
A sample configuration is shown below:
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
> [!TIP]
> You can input multiple Groq API keys separated by commas (or multiple `GroqAPIKey` entries) to enable key rotation and avoid API rate limits.

#### 6. Run the Application
Start the assistant in development mode:
```powershell
python app.py
```
This launches the backend threads (telemetry, network monitoring) and starts the Eel-based web frontend in an Edge application window.

---

### Option 2: Building & Packaging (For Distribution)

If you wish to compile JARVIS Mark II into a standalone executable and package it as a Windows installer:

#### 1. Build Standalone Executable
Compile the project using PyInstaller and the provided `.spec` configuration:
```powershell
pyinstaller JARVIS_Mark_II.spec
```
This packages the source code, libraries, and assets (static `frontend` files) into a single standalone binary directory. The executable will be created at `dist/Jarvis.exe`.

#### 2. Create Windows Installer (Inno Setup)
To build a professional installer wizard for end users:
1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php).
2. Open `installer.iss` in the Inno Setup Compiler GUI (or run the command-line compiler: `iscc installer.iss`).
3. The build process compiles a setup package at `dist/JarvisSetup.exe`.

> [!IMPORTANT]
> **Production AppData Redirection**: When packaged and installed (e.g. inside `C:\Program Files\`), files inside the installation directory are write-protected. To prevent permission errors, the app automatically redirects all user files (`.env`, `contacts.json`, `chatlog.json`, generated image downloads) to the safe user directory:
> `%LOCALAPPDATA%\JARVIS_Mark_II\`

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
* File: [image_generation.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/image_generation.py)
  * **`GenerateImages(prompt)`**: Dispatches tasks to generate and display stable diffusion AI images.

### ⚙️ Configuration & Data Managers
* File: [config_manager.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/config_manager.py)
  * **`get_setting(name, fallback)`**: Fetches a setting from configuration keys.
  * **`save_api_keys(updated_keys)`**: Safely updates external API credentials in `.env`.
  * **`get_groq_api_keys()`**: Retrieves list of registered keys.
  * **`save_personal_info(username, assistantname)`**: Updates customization preferences.
* File: [data_manager.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/data_manager.py)
  * **`load_json(file_path, default)`**: Atomic read function resolving local appdata targets.
  * **`save_json(file_path, data)`**: Atomic write function utilizing temporary swapping.
  * **`read_text(file_path, default)`** / **`write_text(file_path, content)`**: Atomic utilities for logging system telemetry.
* File: [groq_client.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/groq_client.py)
  * Class **`Groq`**: Intercepts LLM calls, providing thread-safe load balancing and active API key rotation.

### 🔄 Auto-Update Subsystem
* File: [updater.py](file:///c:/Users/shrik/OneDrive/Desktop/JARVIS%20MARK%202/backend/updater.py)
  * **`check_for_updates_sync()`**: Fetches latest release version and changelog from GitHub Releases API.
  * **`start_download_async(download_url)`**: Initiates background update installation and handles application self-restart.

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
