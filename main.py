import logging
import os
import sys
import threading
from time import sleep

import backend.config_manager as config_manager
import backend.data_manager as data_manager

from backend.automation import process_automation
from backend.chat_bot import ChatBot
from backend.command_manager import FirstLayerDMM
from backend.realtime_search_engine import RealtimeSearchEngine
from backend.speech_to_text import listen, SetAssistantStatus, QueryModifier
from backend.text_to_speech import speak

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

Username = config_manager.get_setting("Username", "User")
Assistantname = config_manager.get_setting("Assistantname", "JARVIS")
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "reminder", "weather", "news"]


# Global state to track state transition print
last_print_was_listening = False

def MainExecution():
    global last_print_was_listening
    try:
        SetAssistantStatus("Listening...")
        try:
            TaskExecution = False
            ImageExecution = False
            ImageGenerationQuery = ""
            
            if not last_print_was_listening:
                print("Listening...")
                last_print_was_listening = True
            Query = listen()
            if not Query:
                return False
            last_print_was_listening = False
            print(f"{Username} : {Query}")
                
            print("Thinking...")
            SetAssistantStatus("Thinking...")
            
            Decision = FirstLayerDMM(Query)
            print(f"Decision : {Decision}")
            
            G = any([i for i in Decision if i.startswith("general")])
            R = any([i for i in Decision if i.startswith("realtime")])
            
            Merged_query = " and ".join(
                [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
            )
            
            for queries in Decision:
                if "generate " in queries:
                    ImageGenerationQuery = str(queries)
                    ImageExecution = True
                      
            for queries in Decision:
                if any(queries.startswith(func) for func in Functions):
                    response = process_automation(queries)
                    if response:
                        print(f"{Assistantname} : {response}")
                        speak(response)
                    TaskExecution = True
                        
            if ImageExecution:
                try:
                    from backend.image_generation import GenerateImages
                    t = threading.Thread(target=GenerateImages, args=(ImageGenerationQuery,), daemon=True)
                    t.start()
                except Exception as e:
                    logger.error(f"Error starting image generation thread: {e}", exc_info=True)
                    
            if R:
                print("Searching...")
                SetAssistantStatus("Thinking...")
                Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
                print(f"{Assistantname} : {Answer}")
                speak(Answer)
                return True
            
            else:
                for Queries in Decision:
                    if "general" in Queries:
                        QueryFinal = Queries.replace("general ","")
                        SetAssistantStatus("Thinking...")
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        print(f"{Assistantname} : {Answer}")
                        speak(Answer)
                        return True
                    
                    elif "realtime" in Queries:
                        print("Searching...")
                        SetAssistantStatus("Thinking...")
                        QueryFinal = Queries.replace("realtime ","")
                        Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                        print(f"{Assistantname} : {Answer}")
                        speak(Answer)
                        return True
                    
                    elif "exit" in Queries:
                        QueryFinal = "Okay, Bye!"
                        SetAssistantStatus("Thinking...")
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        print(f"{Assistantname} : {Answer}")
                        speak(Answer)
                        os._exit(1)
        finally:
            SetAssistantStatus("Active")
    except Exception as e:
        err_msg = str(e).lower()
        if any(keyword in err_msg for keyword in ["getaddrinfo", "connection", "resolve", "offline"]):
            logger.warning(f"Network connection error in MainExecution: {e}. Retrying in 5 seconds...")
            sleep(5)
        else:
            logger.error(f"Error in MainExecution: {e}. Retrying in 2 seconds...", exc_info=True)
            sleep(2)
        return False
            
if __name__ == "__main__":
    while True:
        MainExecution()