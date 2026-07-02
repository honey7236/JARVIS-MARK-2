import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
try:
    from backend.groq_client import Groq
except ImportError:
    from groq_client import Groq
from json import load, dump # Importing functions to read and write JSON files.
import datetime # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client with the provided API Key.
client = Groq(api_key=GroqAPIKey)

#Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***
*** Keep the answer clean, very short, and highly accurate. Summarize the answer in 2-3 concise, direct sentences. ***
*** Avoid bullet points, lists, introductory phrases (such as "According to the search results..."), and conversational filler. Just state the facts directly. ***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn't exist.
messages = []
os.makedirs("Data", exist_ok=True)
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except Exception:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

class SearchResult:
    def __init__(self, title, description, url):
        self.title = title
        self.description = description
        self.url = url

# Function to perform a search and format the results.
def GoogleSearch(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    results = []
    
    # STAGE 1: DuckDuckGo HTML (Very standard, highly reliable)
    try:
        url = "https://html.duckduckgo.com/html/"
        resp = requests.post(url, headers=headers, data={"q": query}, timeout=6)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("#links .result")
            for item in items:
                title_el = item.select_one(".result__a")
                snippet_el = item.select_one(".result__snippet")
                if title_el:
                    title = title_el.get_text(strip=True)
                    href = title_el.get("href")
                    
                    # Clean redirect wrapper
                    if "/l/?uddg=" in href:
                        href = href.split("uddg=")[1].split("&")[0]
                        href = unquote(href)
                    elif href.startswith("//"):
                        href = "https:" + href
                        
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                    results.append(SearchResult(title, snippet, href))
                    if len(results) >= 5:
                        break
    except Exception as e:
        print(f"[SearchEngine] DuckDuckGo HTML POST failed: {e}")

    # STAGE 1b: DuckDuckGo HTML via GET (as fallback to POST)
    if not results:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                items = soup.select("#links .result")
                for item in items:
                    title_el = item.select_one(".result__a")
                    snippet_el = item.select_one(".result__snippet")
                    if title_el:
                        title = title_el.get_text(strip=True)
                        href = title_el.get("href")
                        if "/l/?uddg=" in href:
                            href = href.split("uddg=")[1].split("&")[0]
                            href = unquote(href)
                        elif href.startswith("//"):
                            href = "https:" + href
                        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                        results.append(SearchResult(title, snippet, href))
                        if len(results) >= 5:
                            break
        except Exception as e:
            print(f"[SearchEngine] DuckDuckGo HTML GET failed: {e}")

    # STAGE 2: DuckDuckGo Lite (POST request)
    if not results:
        try:
            url = "https://lite.duckduckgo.com/lite/"
            resp = requests.post(url, headers=headers, data={"q": query}, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Check for standard result-link classes first
                links = soup.find_all("a", class_="result-link")
                for link in links:
                    title = link.text.strip()
                    href = link.get("href")
                    
                    snippet = ""
                    parent_tr = link.find_parent("tr")
                    if parent_tr:
                        next_tr = parent_tr.find_next_sibling("tr")
                        if next_tr:
                            snippet_td = next_tr.find("td", class_="result-snippet")
                            if snippet_td:
                                snippet = snippet_td.text.strip()
                    
                    if "/l/?uddg=" in href:
                        href = href.split("uddg=")[1].split("&")[0]
                        href = unquote(href)
                    
                    results.append(SearchResult(title, snippet, href))
                    if len(results) >= 5:
                        break
                        
                # Fallback to tag-based scraping if classes changed
                if not results:
                    all_links = soup.find_all("a", href=True)
                    for link in all_links:
                        href = link["href"]
                        if "duckduckgo.com" in href and not "/l/?uddg=" in href:
                            continue
                        if href.startswith("/") and not href.startswith("//") and not href.startswith("/l/?uddg="):
                            continue
                        title = link.text.strip()
                        if not title or len(title) < 3:
                            continue
                        if "/l/?uddg=" in href:
                            href = href.split("uddg=")[1].split("&")[0]
                            href = unquote(href)
                        
                        snippet = ""
                        parent_tr = link.find_parent("tr")
                        if parent_tr:
                            next_tr = parent_tr.find_next_sibling("tr")
                            if next_tr:
                                snippet = next_tr.text.strip()
                        
                        results.append(SearchResult(title, snippet, href))
                        if len(results) >= 5:
                            break
        except Exception as e:
            print(f"[SearchEngine] DuckDuckGo Lite failed: {e}")

    # STAGE 3: Mojeek (Robust Fallback)
    if not results:
        try:
            url = f"https://www.mojeek.com/search?q={quote(query)}"
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                li_items = soup.find_all("li")
                for li in li_items:
                    title_a = li.find("a", class_="title") or li.find("a")
                    if title_a:
                        title = title_a.text.strip()
                        href = title_a.get("href")
                        if not href or href.startswith("/") or "mojeek.com" in href:
                            continue
                        
                        snippet_p = li.find("p", class_="s") or li.find("p")
                        snippet = snippet_p.text.strip() if snippet_p else ""
                        if snippet_p and snippet_p.find("span", class_="url"):
                            url_span = snippet_p.find("span", class_="url")
                            snippet = snippet.replace(url_span.text, "").strip()
                            
                        results.append(SearchResult(title, snippet, href))
                        if len(results) >= 5:
                            break
        except Exception as e:
            print(f"[SearchEngine] Mojeek failed: {e}")

    # STAGE 4: Google Mobile Search (Ultimate Fail-Safe)
    if not results:
        try:
            url = f"https://www.google.com/search?q={quote(query)}"
            google_headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
            }
            resp = requests.get(url, headers=google_headers, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                divs = soup.find_all("div", class_="xpd") or soup.find_all("div", class_="g")
                for div in divs:
                    a_tag = div.find("a", href=True)
                    if a_tag:
                        href = a_tag["href"]
                        if href.startswith("/url?q="):
                            href = href.split("/url?q=")[1].split("&")[0]
                            href = unquote(href)
                        elif href.startswith("/"):
                            continue
                        
                        h3 = div.find("h3")
                        title = h3.get_text(strip=True) if h3 else (a_tag.get_text(strip=True) or "Search Result")
                        
                        snippet_div = div.find(class_="BNeawe") or div.find(class_="VwiC3b")
                        snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                        
                        results.append(SearchResult(title, snippet, href))
                        if len(results) >= 5:
                            break
        except Exception as e:
            print(f"[SearchEngine] Google Mobile fallback failed: {e}")

    Answer = f"The Search results for '{query}' are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\nLink: {i.url}\n\n"
    Answer += "[end]"
    return Answer

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')  # Split the response into lines.
    non_empty_lines = [line for line in lines if line.strip()]  # Remove empty lines.
    modified_answer = '\n'.join(non_empty_lines)  # Join the cleaned lines back together.
    return modified_answer

# Predefined chatbot conversation system message and an initial user messages.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": f"Hello {Username}! Sir. How can I help you?"},
]

# Function to get the real-time information like the current date and time.
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")        
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed: \n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global messages
    if not prompt or not prompt.strip():
        return "I didn't catch that, could you please repeat?"
    
    # Load the chat log from the JSON file.
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)
    except Exception:
        messages = []
    messages.append({"role": "user", "content": f"{prompt}"})
    
    # Combine system prompt, search results, and real-time info without mutating global state.
    search_results = GoogleSearch(prompt)
    messages_to_send = (
        SystemChatBot 
        + [{"role": "system", "content": search_results}] 
        + [{"role": "system", "content": Information()}] 
        + messages
    )
    
    # Genrate a response using the Groq client.
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages_to_send,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None
    )
    
    Answer = ""
    
    # Concatenate response chunks from the streaming output.
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
                    
    # Clean up the response.
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})
    
    # Save the updated chat log back to the JSON file.
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)
        
    return AnswerModifier(Answer=Answer)

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query Sir: ")
        print(RealtimeSearchEngine(prompt))