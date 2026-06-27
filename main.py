from backend.command_manager import FirstLayerDMM
from backend.realtime_search_engine import RealtimeSearchEngine
from backend.automation import process_automation
from backend.speech_to_text import listen
from backend.chat_bot import ChatBot
from backend.text_to_speech import speak
from dotenv import dotenv_values
from time import sleep
import subprocess
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "reminder"]

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    
    # Check if the query is a question and add a question mark if necessary.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Main Execution
def MainExecution():
    try:
        # speak("initializing jarvis. i am listening sir...")
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""
        
        print("Listening...")
        Query = listen()
        print(f"{Username} : {Query}")
        
        if not Query:
            return False
            
        print("Thinking...")
        
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
                    
        if ImageExecution == True:
            with open(r"Frontend\Files\ImageGeneration.data", "w", encoding='utf-8') as file:
                file.write(f"{ImageGenerationQuery},True")
                
            try:
                p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      stdin=subprocess.PIPE, shell=False)
                subprocesses.append(p1)
                
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")
                
        if G and R or R:
            print("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            print(f"{Assistantname} : {Answer}")
            speak(Answer)
            return True
        
        else:
            for Queries in Decision:
                if "general" in Queries:
                    QueryFinal = Queries.replace("general ","")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    print(f"{Assistantname} : {Answer}")
                    speak(Answer)
                    return True
                
                elif "realtime" in Queries:
                    print("Searching...")
                    QueryFinal = Queries.replace("realtime ","")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    print(f"{Assistantname} : {Answer}")
                    speak(Answer)
                    return True
                
                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    print(f"{Assistantname} : {Answer}")
                    speak(Answer)
                    os._exit(1)
    except Exception as e:
        err_msg = str(e).lower()
        if "getaddrinfo" in err_msg or "connection" in err_msg or "resolve" in err_msg or "offline" in err_msg:
            print(f"Network connection error in MainExecution: {e}. Retrying in 5 seconds...")
            sleep(5)
        else:
            print(f"Error in MainExecution: {e}")
        return False
            
if __name__ == "__main__":
    while True:
        MainExecution()