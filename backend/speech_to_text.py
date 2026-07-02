import logging
import os
import threading
import time

import backend.config_manager as config_manager
import backend.data_manager as data_manager
import mtranslate as mt
import speech_recognition as sr

# Initialize logger
logger = logging.getLogger(__name__)

# Get the input language setting via Config Manager.
InputLanguage = config_manager.get_setting("InputLanguage") or "en"

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Optimize sensitivity and noise thresholds
recognizer.energy_threshold = 600      # Initial threshold slightly higher for static protection
recognizer.dynamic_energy_threshold = True  # Dynamically adapt to room noise levels
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5

# Set path for assistant status telemetry files
TempDirPath = os.path.join("frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

# Calibrate microphone for ambient noise floor once on startup in a background thread
def _calibrate_mic():
    logger.info("[SpeechToText] Calibrating microphone for ambient noise floor in background...")
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
        logger.info(f"[SpeechToText] Background calibration complete. Energy threshold set to: {recognizer.energy_threshold}")
    except Exception as e:
        logger.warning(f"[SpeechToText] Microphone calibration skipped: {e}")

threading.Thread(target=_calibrate_mic, daemon=True).start()

# Function to set the assistant's status by writing it to a file and updating Eel.
def SetAssistantStatus(Status):
    status_file_path = os.path.join(TempDirPath, "Status.data")
    data_manager.write_text(status_file_path, Status)

    try:
        import eel
        eel.updateStatus(Status)
    except Exception:
        pass

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    if not query_words:
        return ""
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]
    
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

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, 'en', "auto")
    return english_translation.capitalize()

# Function to perform speech recognition using the microphone.
def listen():
    SetAssistantStatus("Listening...")
    
    # Map input language to standard locale strings
    recognize_language = InputLanguage
    if recognize_language == "en":
        recognize_language = "en-IN"
    elif recognize_language == "hi":
        recognize_language = "hi-IN"

    try:
        with sr.Microphone() as source:
            try:
                # Capture speech natively without timing out (blocks until input is detected)
                audio = recognizer.listen(source)
            except Exception as mic_err:
                logger.error(f"[SpeechToText] Microphone listen error: {mic_err}", exc_info=True)
                SetAssistantStatus("Active")
                time.sleep(1.0)  # Sleep on hardware/mic errors to prevent busy-looping
                return ""
    except Exception as mic_init_err:
        logger.error(f"[SpeechToText] Microphone initialization failed (is it connected?): {mic_init_err}", exc_info=True)
        SetAssistantStatus("Active")
        time.sleep(2.0)
        return ""

    SetAssistantStatus("Thinking...")
    try:
        # Recognize speech using Google Web Speech API
        text = recognizer.recognize_google(audio, language=recognize_language)
        print("You:", text)
        
        if not text:
            SetAssistantStatus("Active")
            return ""
            
        # If the input language is English, return the modified query.
        if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
            return QueryModifier(text)
        else:
            # If the input language is not English, translate the text and return it.
            SetAssistantStatus("Translating...")
            try:
                return QueryModifier(UniversalTranslator(text))
            except Exception as trans_err:
                logger.error(f"Translation network error: {trans_err}", exc_info=True)
                return QueryModifier(text)
                
    except Exception as e:
        logger.warning(f"Google speech recognition failed or did not hear anything: {e}")
        SetAssistantStatus("Active")
        time.sleep(0.2)  # Short cooldown on recognition failures
        return ""

# Main Execution Block.
if __name__ == "__main__":
    while True:
        # Continuously perform speech recognition and print the recognized text.
        Text = listen()