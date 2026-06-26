import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import eel
import threading
from main import MainExecution
from backend.automation import display_system_info,display_weather,get_news

def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)

eel.init(resource_path("frontend"))

# Decorate functions to expose them to Eel
@eel.expose
def get_network_status():
    from backend.automation import get_cached_status
    return get_cached_status()

@eel.expose
def display_weather_data():
    try:
        return display_weather()
    except Exception as e:
        print("Weather fetch error:", e)
        return "Weather unavailable"

@eel.expose
def get_weather_data():
    return display_weather_data()

@eel.expose
def get_news_data():
    try:
        return get_news()
    except Exception as e:
        print("News fetch error:", e)
        return "News unavailable"

@eel.expose
def get_system_data():
    try:
        return display_system_info()
    except Exception as e:
        print("System data fetch error:", e)
        return {"cpu": "N/A", "ram_percent": "N/A", "ram_details": "N/A", "disk_percent": "N/A", "disk_details": "N/A"}

@eel.expose
def display_system_info_data():
    return get_system_data()

@eel.expose
def get_last_session_messages():
    try:
        from data.short_term import FILE
        import json
        if os.path.exists(FILE):
            with open(FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print("Error getting last session messages:", e)
    return []

# Contact management APIs
from data.contact_data import contacts
import json

CONTACTS_JSON_FILE = "data/contacts.json"

def save_contacts_to_file():
    os.makedirs("data", exist_ok=True)
    try:
        with open(CONTACTS_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=4)
    except Exception as e:
        print("Error saving contacts.json:", e)

def load_contacts():
    os.makedirs("data", exist_ok=True)
    os.makedirs("memory", exist_ok=True)
    if os.path.exists(CONTACTS_JSON_FILE):
        try:
            with open(CONTACTS_JSON_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                contacts.clear()
                contacts.update(loaded)
        except Exception as e:
            print("Error loading contacts.json:", e)
    else:
        save_contacts_to_file()

load_contacts()

@eel.expose
def get_contacts():
    return contacts

@eel.expose
def save_contact(name, phone):
    try:
        if not name or not phone:
            return {"success": False, "error": "Name and phone number cannot be empty."}
        
        name_lower = name.strip().lower()
        phone_clean = phone.strip()
        
        contacts[name_lower] = phone_clean
        save_contacts_to_file()
        return {"success": True, "contacts": contacts}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def delete_contact(name):
    try:
        name_lower = name.strip().lower()
        if name_lower in contacts:
            del contacts[name_lower]
            save_contacts_to_file()
            return {"success": True, "contacts": contacts}
        else:
            return {"success": False, "error": "Contact not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Run network status loop in background
from backend.automation import start_network_monitoring
start_network_monitoring()

# Run jarvis in background with a delay of 8 seconds to match the frontend intro video
def delayed_jarvis():
    import time
    import ctypes
    
    # Path to the startup audio
    mp3_path = resource_path(os.path.join("frontend", "assets", "jarvis audio.mp3"))
    abs_mp3_path = os.path.abspath(mp3_path)
    
    if os.path.exists(abs_mp3_path):
        try:
            # Play mp3 using Windows Multimedia API (MCI) natively without installing any packages
            ctypes.windll.winmm.mciSendStringW(f'open "{abs_mp3_path}" type mpegvideo alias jarvis_audio', None, 0, None)
            ctypes.windll.winmm.mciSendStringW('play jarvis_audio', None, 0, None)
        except Exception as e:
            print("Error playing startup audio:", e)
            
    time.sleep(8)
    
    # Close audio device to release resources
    try:
        ctypes.windll.winmm.mciSendStringW('close jarvis_audio', None, 0, None)
    except:
        pass
        
    while True:
        MainExecution()

threading.Thread(target=delayed_jarvis, daemon=True).start()

eel.start('index.html', mode='edge', host='localhost', port=0, size=(1280, 720), cmdline_args=['--start-maximized']) 
