# JARVIS Mark II - Advanced AI Desktop Assistant

JARVIS Mark II is a premium, voice-activated desktop assistant. Powered by a hybrid engine combining local automation systems, real-time web engines, and advanced language models (via the Groq API), it provides a responsive interface to control your desktop, automate daily workflows, and retrieve real-time information.

---

## 🚀 Core Features

### 🎙️ Voice & Speech Interface
- **Natural Speech Recognition**: Listens to user inputs in real-time.
- **Text-to-Speech (TTS)**: Realistic voice output powered by high-quality neural voices.
- **Dynamic Greeting**: Automatically greets you based on the current time of day.

### 💻 Desktop Automation
- **App Opener/Closer**: Launch or close any desktop application or website with fuzzy name matching.
- **Smart Link Resolver**: If an app opening fails, JARVIS automatically queries Google and opens the first relevant search result.
- **System Controls**: Perform system commands such as mute, unmute, volume up, and volume down.
- **Screenshot Utility**: Instantly capture your screen and save the image to your Desktop.

### 📝 Content Writing Engine
- **Groq Integration**: Write letters, essays, notes, emails, songs, and code using the high-performance `mixtral-8x7b-32768` model.
- **Automatic Export**: Generated content is automatically saved to a text file and opened in Notepad for immediate review.

### 🌐 Real-Time Web Operations
- **Fuzzy Search & Navigation**: Direct search queries on Google and YouTube.
- **YouTube Playback**: Instantly play music or videos using voice commands.
- **Weather & Location**: Track current weather, temperature, and wind speed dynamically based on your IP location.
- **Top Headlines**: Speak or list top general news headlines in real-time.
- **Speed Test**: Monitored via Cloudflare speed test to measure download/upload bandwidth and ping.

### 📅 Productivity & Organization
- **Smart Reminders**: Set time-based reminders. JARVIS will speak the reminder and send an instant notification to your registered WhatsApp number when the timer expires.
- **WhatsApp Integration**: Dictate messages and send them instantly to your contacts.
- **Contact Manager**: A custom JSON-based database to store and retrieve your contacts.

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
│   ├── chat_bot.py            # Chatbot query handling
│   ├── command_manager.py     # Decision-making model (DMM) for routing
│   ├── imagegeneration.py     # AI image generation subsystem
│   ├── realtime_search_engine.py # Scraping-based realtime search engine
│   ├── speech_to_text.py      # Voice listening and transcription
│   └── text_to_speech.py      # Speech generation
├── data/                      # Data storage and configuration
│   ├── DLG_data.py            # Dialogues and pre-configured responses
│   ├── Web_Data.py            # Predefined website mappings
│   ├── contact_data.py        # Contacts data model
│   └── contacts.json          # Contacts database
├── frontend/                  # Web-based dashboard GUI (Eel)
└── memory/                    # SQLite or JSON short-term session logs
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your Windows system.

### 2. Clone and Install Dependencies
Install all required libraries using `pip`:
```bash
pip install -r requirements.txt
```

*Note: For SpeechRecognition and system audio functionality, PyAudio is required. Ensure you have the appropriate build tools or pre-compiled wheels if needed.*

### 3. Environment Configuration
Create a `.env` file in the root directory (or update the existing one) with your credentials:
```ini
Username=YourName
Assistantname=JARVIS
GroqAPIKey=your_groq_api_key_here
InputLanguage=en
AssistantVoice=en-CA-LiamNeural
cohere=your_cohere_key_here
HuggingFaceAPIKey=your_hf_key_here
```

### 4. Running the Assistant
Start the application using:
```bash
python app.py
```
This will initialize the backend and launch the modern Eel web interface.

---

## 🎙️ Sample Commands

- **Open/Close Apps**: `"open Chrome"`, `"close Notepad"`, `"open Facebook"`
- **Searches**: `"google search quantum physics"`, `"youtube search python tutorial"`
- **Music**: `"play lo-fi beats"`
- **Writing**: `"content write a sick leave application"`
- **System**: `"system volume up"`, `"system mute"`
- **Information**: `"weather"`, `"news"`, `"check system stats"`
- **Reminders**: `"reminder drink water at 4:30 pm"`
- **WhatsApp**: `"send message on whatsapp"`

---

## 🔒 License
This project is open-source and available under the MIT License.
