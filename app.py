import ctypes
import json
import logging
import os
import sys
import threading
import time

# Ensure parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import eel
import backend.config_manager as config_manager
import backend.data_manager as data_manager
import backend.updater

from backend.automation import (
    display_system_info,
    display_weather,
    get_cached_status,
    get_news,
    start_network_monitoring
)
import backend.chat_bot
import backend.groq_client
import backend.realtime_search_engine
from data.contact_data import contacts
import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)

eel.init(resource_path("frontend"))

# Decorate functions to expose them to Eel
@eel.expose
def get_network_status():
    try:
        return get_cached_status()
    except Exception as e:
        logger.error(f"Error getting network status: {e}", exc_info=True)
        return {
            "status": "Offline",
            "ping": "N/A",
            "download": "N/A",
            "upload": "N/A"
        }

@eel.expose
def display_weather_data():
    try:
        return display_weather()
    except Exception as e:
        logger.error(f"Weather fetch error: {e}", exc_info=True)
        return "Weather unavailable"

@eel.expose
def get_weather_data():
    return display_weather_data()

@eel.expose
def get_news_data():
    try:
        return get_news()
    except Exception as e:
        logger.error(f"News fetch error: {e}", exc_info=True)
        return "News unavailable"

@eel.expose
def get_system_data():
    try:
        return display_system_info()
    except Exception as e:
        logger.error(f"System data fetch error: {e}", exc_info=True)
        return {"cpu": "N/A", "ram_percent": "N/A", "ram_details": "N/A", "disk_percent": "N/A", "disk_details": "N/A"}

@eel.expose
def display_system_info_data():
    return get_system_data()

# Contact management
CONTACTS_JSON_FILE = "data/contacts.json"

def load_contacts():
    loaded = data_manager.load_json(CONTACTS_JSON_FILE, default={})
    contacts.clear()
    contacts.update(loaded)

load_contacts()


@eel.expose
def get_api_keys():
    """Reads keys via config_manager and returns them."""
    return {
        "GroqAPIKeys": config_manager.get_groq_api_keys(),
        "cohere": config_manager.get_api_key("cohere") or config_manager.get_api_key("CohereAPIKey") or "",
        "HuggingFaceAPIKey": config_manager.get_api_key("HuggingFaceAPIKey") or "",
        "OpenWeatherAPIKey": config_manager.get_api_key("OpenWeatherAPIKey") or "",
        "GNewsAPIKey": config_manager.get_api_key("GNewsAPIKey") or ""
    }


@eel.expose
def save_api_keys(updated_keys):
    """Saves the updated API keys back to the .env file using config_manager."""
    success = config_manager.save_api_keys(updated_keys)
    if success:
        # Re-initialize Groq client keys in memory
        try:
            with backend.groq_client._global_lock:
                backend.groq_client._initialized = False
                backend.groq_client._global_keys = []
                backend.groq_client._global_current_key_index = 0
            logger.info("[Eel] Groq API keys reloaded in memory successfully.")
        except Exception as re_err:
            logger.error(f"Error reloading Groq keys in memory: {re_err}", exc_info=True)
        return {"success": True}
    else:
        return {"success": False, "error": "Failed to save API keys to .env"}


@eel.expose
def get_personal_info():
    """Reads Username and Assistantname from config_manager."""
    return {
        "Username": config_manager.get_setting("Username", ""),
        "Assistantname": config_manager.get_setting("Assistantname", "")
    }


@eel.expose
def save_personal_info(info):
    """Saves Username and Assistantname to .env and updates them in memory."""
    new_username = info.get("Username", "").strip()
    new_assistantname = info.get("Assistantname", "").strip()
    
    if not new_username or not new_assistantname:
        return {"success": False, "error": "Username and Assistant name cannot be empty."}
        
    success = config_manager.save_personal_info(new_username, new_assistantname)
    if success:
        return {"success": True}
    else:
        return {"success": False, "error": "Failed to save personal info to .env"}


@eel.expose
def get_chat_log():
    """Reads Data/ChatLog.json and returns the list of messages."""
    chat_log_path = os.path.join("data", "chatlog.json")
    return data_manager.load_json(chat_log_path, default=[])


@eel.expose
def check_login_status():
    """Checks if the user has completed onboarding (Username, Assistantname, and GroqAPIKey are set)."""
    try:
        username = config_manager.get_setting("Username")
        assistantname = config_manager.get_setting("Assistantname")
        groq_keys = config_manager.get_groq_api_keys()
        
        if username and assistantname and groq_keys:
            username_clean = username.strip()
            assistant_clean = assistantname.strip()
            groq_clean = groq_keys[0].strip() if groq_keys else ""
            if username_clean and assistant_clean and groq_clean:
                # Ensure they are not placeholder values
                if "your_groq_api_key" not in groq_clean and "your_" not in username_clean:
                    return {"logged_in": True}
    except Exception as e:
        logger.error(f"Error checking login status: {e}", exc_info=True)
        
    return {"logged_in": False}


# Run network status loop in background
start_network_monitoring()

# Run jarvis in background with a delay of 8 seconds to match the frontend intro video
def delayed_jarvis():
    # Path to the startup audio
    mp3_path = resource_path(os.path.join("frontend", "assets", "jarvis audio.mp3"))
    abs_mp3_path = os.path.abspath(mp3_path)
    
    if os.path.exists(abs_mp3_path):
        try:
            # Play mp3 using Windows Multimedia API (MCI) natively without installing any packages
            ctypes.windll.winmm.mciSendStringW(f'open "{abs_mp3_path}" type mpegvideo alias jarvis_audio', None, 0, None)
            ctypes.windll.winmm.mciSendStringW('play jarvis_audio', None, 0, None)
        except Exception as e:
            logger.error(f"Error playing startup audio: {e}", exc_info=True)
    else:
        logger.warning(f"Startup audio file not found at: {abs_mp3_path}. Skipping startup audio playback.")
            
    time.sleep(8)
    
    # Close audio device to release resources
    try:
        ctypes.windll.winmm.mciSendStringW('close jarvis_audio', None, 0, None)
    except Exception:
        pass
        
    while True:
        MainExecution()

threading.Thread(target=delayed_jarvis, daemon=True).start()

eel.start('index.html', mode='edge', host='localhost', port=0, size=(1280, 720), cmdline_args=['--start-maximized']) 
