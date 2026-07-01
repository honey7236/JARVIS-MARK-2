import os # Import os for file path handling
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Suppress pygame welcome message banner
import pygame # Import pygame library for handling audio playback
import random # Import random for generating random choices
import asyncio # Import asyncio for asynchronous operations
import edge_tts # Import edge_tts for text-to-speech functionality
from dotenv import dotenv_values # Import dotenv for reading environment variables from a .env file
try:
    from backend.speech_to_text import SetAssistantStatus
except ImportError:
    from speech_to_text import SetAssistantStatus

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice") or "en-CA-LiamNeural" # Get the AssistantVoice from the environment variables, with fallback.

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text, file_path) -> None:
    if os.path.exists(file_path): # Check if the file already exists.
        try:
            os.remove(file_path) # Attempt to remove old files if present.
        except Exception:
            pass
        
    # Create the communicate object to generate speech.
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path) # Save the generated speech as an MP3 file.
    
# Function to manage Text-to-Speech (TTS) functionality.
def TTS(Text, func=lambda r=None: True):
    SetAssistantStatus("Answering...")
    
    # Generate unique filename for this TTS cycle to prevent Windows PermissionError Locks
    os.makedirs("Data", exist_ok=True)
    file_path = rf"Data\speech_{random.randint(1000, 9999)}.mp3"
    
    retries = 3
    for attempt in range(retries):
        try:
            # Convert text to an audio file asynchronously.
            asyncio.run(TextToAudioFile(Text, file_path))
            
            # Initialize pygame mixer for audio playback.
            pygame.mixer.init()
            
            # Load the generated speech file into pygame mixer.
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play() # Play the audio file.
            
            # Loop until the audio is done playing or the function stops.
            while pygame.mixer.music.get_busy():
                if func() == False: #Check if the external function return False.
                    break
                pygame.time.Clock().tick(10)  # Limit the loop to 10 ticks per second.
                
            return True  # Return True if the audio played successfully.
        
        except Exception as e:  # Handle any exceptions during the process
            print(f"Error in TTS (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                from time import sleep
                sleep(1)
            else:
                return False
            
        finally:
            try:
                # Call the provided function with False to signal the end of TTS.
                func(False)
                pygame.mixer.music.stop()  # Stop the audio playback.
                pygame.mixer.music.unload()  # Release the file handle on the MP3.
                pygame.mixer.quit()  # Quit the pygame mixer.
                
                # Cleanup the generated speech file safely
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:  # Handle any exceptions during the cleanup
                print(f"Error in finally block: {e}")
            SetAssistantStatus("Active")
                
# Function to manage Text-to-Speech (TTS) functionality with additional responses for long texts.
def speak(Text, func=lambda r=None: True):
    Data = str(Text).split(".") # Split the text by periods into a list of sentences
    
    # List of predefined responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    
    # If the text is very long (more than 4 sentences and 250 characters), and a response messages
    if len(Data) > 4 and len(Text) > 250:
        TTS(" ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
        
    # Otherwise, just play the whole text.
    else:
        TTS(Text, func)
        
# Main execution loop
if __name__ == "__main__":
    while True:
        # Prompt user for input and pass it to speak function.
        speak(input("Enter Your Query: "))

