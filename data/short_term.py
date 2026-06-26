conversation = []

def add_message(role, content):
    conversation.append({"role": role, "content": content})
    
    # keep last 10 messages
    if len(conversation) > 10:
        conversation.pop(0)

def get_conversation():
    return conversation

import json

FILE = "memory/session.json"

def save_session():
    with open(FILE, "w") as f:
        json.dump(conversation, f, indent=4)

def load_session():
    global conversation
    try:
        with open(FILE, "r") as f:
            conversation = json.load(f)
    except:
        conversation = []