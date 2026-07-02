import datetime
import logging
import os
import backend.config_manager as config_manager
import backend.data_manager as data_manager

try:
    from backend.groq_client import Groq
except ImportError:
    from groq_client import Groq

# Initialize logger
logger = logging.getLogger(__name__)

# Retrieve specific settings via Config Manager.
Username = config_manager.get_setting("Username", "User")
Assistantname = config_manager.get_setting("Assistantname", "JARVIS")
# Get the first Groq API key (or default) for initialization.
groq_keys = config_manager.get_groq_api_keys()
GroqAPIKey = groq_keys[0] if groq_keys else None

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define a system message that provides context to the AI chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

# Path to the chat log JSON file.
chat_log_path = os.path.join("data", "chatlog.json")

# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now() # Get the current date and time.
    day = current_date_time.strftime("%A") # Day of the week.
    date = current_date_time.strftime("%d") # Day of the month.
    month = current_date_time.strftime("%B") # Full month name.
    year = current_date_time.strftime("%Y") # Year.
    hour = current_date_time.strftime("%H") # Hour in 24-hour format.
    minute = current_date_time.strftime("%M") # Minute.
    second = current_date_time.strftime("%S") # Second.

    # Format the information into a string.
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    lines = Answer.split('\n')  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines)  # Join the cleaned lines back together.
    return modified_answer

# Main chatbot function to handle user queries.
def ChatBot(Query, retries=1):
    """ This function sends the user's query to the chatbot and returns the AI's response. """
    if not Query or not Query.strip():
        return "I didn't catch that, could you please repeat?"

    try:
        # Load the existing chat log from the JSON file.
        local_messages = data_manager.load_json(chat_log_path, default=[])

        # Append the user's query to the messages list.
        local_messages.append({"role": "user", "content": f"{Query}"})

        # Make a request to the Groq API for a response.
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Specify the AI model to use.
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + local_messages,
            max_tokens=1024,  # Limit the maximum tokens in the response.
            temperature=0.7,  # Adjust response randomness (higher means more random).
            top_p=1,  # Use nucleus sampling to control diversity.
            stream=True,  # Enable streaming response.
            stop=None  # Allow the model to determine when to stop.
        )

        Answer = ""  # Initialize an empty string to store the AI's response.

        # Process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check if there's content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Append the content to the answer.

        Answer = Answer.replace("</s>", "")  # Clean up any unwanted tokens from the response.

        # Append the chatbot's response to the messages list.
        local_messages.append({"role": "assistant", "content": Answer})
        # Save the updated chat log to the JSON file.
        data_manager.save_json(chat_log_path, local_messages)

        # Return the formatted response.
        return AnswerModifier(Answer=Answer)

    except Exception as e:
        # Handle errors by logging the exception and resetting the chat log.
        logger.error(f"Error in ChatBot: {e}", exc_info=True)
        if retries > 0:
            data_manager.save_json(chat_log_path, [])
            return ChatBot(Query, retries=retries - 1)  # Retry the query after resetting the log.
        else:
            raise e

# Main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")  # Prompt the user for a question.
        print(ChatBot(user_input))  # Call the chatbot function and print its response.