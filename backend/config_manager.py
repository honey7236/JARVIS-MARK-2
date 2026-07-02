import logging
import os
import threading

logger = logging.getLogger(__name__)

_lock = threading.RLock()
_config = {}
_groq_keys = []
_initialized = False

def _get_env_path():
    # In production/packaged mode (running from a write-protected directory or compiled executable),
    # configuration must reside in the user's Local AppData directory for read/write access.
    appdata_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "JARVIS_Mark_II")
    prod_path = os.path.join(appdata_dir, ".env")
    
    # If the AppData .env exists, use it
    if os.path.exists(prod_path):
        return prod_path
        
    # Check for local developer .env files
    env_paths = [
        ".env",
        os.path.join("..", ".env"),
        os.path.join("..", "..", ".env"),
        os.path.join("backend", ".env")
    ]
    for path in env_paths:
        if os.path.exists(path):
            # If the local .env is writable, use it (development mode)
            try:
                with open(path, "a"):
                    pass
                return path
            except IOError:
                pass
                
    # Otherwise, default to AppData .env (and ensure directory exists)
    os.makedirs(appdata_dir, exist_ok=True)
    return prod_path

def _load_config():
    global _config, _groq_keys, _initialized
    with _lock:
        _config = {}
        _groq_keys = []
        env_path = _get_env_path()
        
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            parts = line.split("=", 1)
                            name = parts[0].strip()
                            val = parts[1].strip()
                            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                val = val[1:-1].strip()
                            
                            if name == "GroqAPIKey":
                                if val and val not in _groq_keys:
                                    _groq_keys.append(val)
                            else:
                                _config[name] = val
            except Exception as e:
                logger.error(f"[ConfigManager] Error reading config file {env_path}: {e}", exc_info=True)
        else:
            logger.warning(f"[ConfigManager] No .env file found at {env_path}")

        # Fallback to os.environ
        for k, v in os.environ.items():
            if k == "GroqAPIKey":
                if v and v not in _groq_keys:
                    _groq_keys.append(v)
            elif k not in _config:
                _config[k] = v
        
        # If GroqAPIKey ended up in _config, synchronize it
        if "GroqAPIKey" in _config:
            val = _config["GroqAPIKey"]
            if val and val not in _groq_keys:
                _groq_keys.append(val)

        _initialized = True
        validate_required_keys()

def validate_required_keys():
    username = _config.get("Username")
    assistant = _config.get("Assistantname")
    
    if not username or "your_" in username.lower():
        logger.warning("[ConfigManager] WARNING: 'Username' is not configured or is set to a placeholder.")
    if not assistant or "your_" in assistant.lower():
        logger.warning("[ConfigManager] WARNING: 'Assistantname' is not configured or is set to a placeholder.")
    if not _groq_keys or any("your_groq" in k.lower() for k in _groq_keys):
        logger.warning("[ConfigManager] WARNING: No valid 'GroqAPIKey' is configured. Groq LLM calls will fail.")

def get_setting(name, fallback=None):
    if not _initialized:
        _load_config()
    with _lock:
        return _config.get(name, fallback)

def get_api_key(name):
    return get_setting(name)

def get_groq_api_keys():
    if not _initialized:
        _load_config()
    with _lock:
        return list(_groq_keys)

def reload_config():
    global _initialized
    with _lock:
        _initialized = False
        _load_config()

def _write_env(lines):
    path = _get_env_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        reload_config()
        return True
    except Exception as e:
        logger.error(f"[ConfigManager] Error writing to .env at {path}: {e}", exc_info=True)
        return False

def save_api_keys(updated_keys):
    with _lock:
        env_path = _get_env_path()
        lines = []
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if not stripped or stripped.startswith("#"):
                            lines.append(line)
                            continue
                        if "=" in line:
                            parts = stripped.split("=", 1)
                            name = parts[0].strip()
                            if name not in ["GroqAPIKey", "cohere", "HuggingFaceAPIKey", "OpenWeatherAPIKey", "GNewsAPIKey"] and name.lower() != "cohere":
                                lines.append(line)
            except Exception as e:
                logger.error(f"[ConfigManager] Error reading during save_api_keys: {e}", exc_info=True)
                
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
            
        groq_keys = updated_keys.get("GroqAPIKeys", [])
        for gk in groq_keys:
            gk_clean = gk.strip()
            if gk_clean:
                lines.append(f"GroqAPIKey = {gk_clean}\n")
                
        other_keys = {
            "cohere": "cohere",
            "HuggingFaceAPIKey": "HuggingFaceAPIKey",
            "OpenWeatherAPIKey": "OpenWeatherAPIKey",
            "GNewsAPIKey": "GNewsAPIKey"
        }
        for key, env_name in other_keys.items():
            val = updated_keys.get(key, "").strip()
            if val:
                lines.append(f"{env_name} = {val}\n")
                
        return _write_env(lines)

def save_personal_info(username, assistantname):
    with _lock:
        env_path = _get_env_path()
        lines = []
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if not stripped or stripped.startswith("#"):
                            lines.append(line)
                            continue
                        if "=" in line:
                            parts = stripped.split("=", 1)
                            name = parts[0].strip()
                            if name not in ["Username", "Assistantname"]:
                                lines.append(line)
            except Exception as e:
                logger.error(f"[ConfigManager] Error reading during save_personal_info: {e}", exc_info=True)
                
        if lines and not lines[-1].endswith("\n"):
            lines.append("\n")
            
        lines.append(f"Username = {username}\n")
        lines.append(f"Assistantname = {assistantname}\n")
        
        success = _write_env(lines)
        if success:
            _sync_modules_in_memory(username, assistantname)
        return success

def _sync_modules_in_memory(username, assistantname):
    try:
        import main
        main.Username = username
        main.Assistantname = assistantname
    except Exception:
        pass

    try:
        import backend.chat_bot
        backend.chat_bot.Username = username
        backend.chat_bot.Assistantname = assistantname
        backend.chat_bot.System = (
            f"Hello, I am {username}, You are a very accurate and advanced AI chatbot named {assistantname} "
            f"which also has real-time up-to-date information from the internet.\n"
            f"*** Do not tell time until I ask, do not talk too much, just answer the question.***\n"
            f"*** Reply in only English, even if the question is in Hindi, reply in English.***\n"
            f"*** Do not provide notes in the output, just answer the question and never mention your training data. ***\n"
        )
        backend.chat_bot.SystemChatBot = [{"role": "system", "content": backend.chat_bot.System}]
    except Exception:
        pass

    try:
        import backend.realtime_search_engine
        backend.realtime_search_engine.Username = username
        backend.realtime_search_engine.Assistantname = assistantname
        backend.realtime_search_engine.System = (
            f"Hello, I am {username}, You are a very accurate and advanced AI chatbot named {assistantname} "
            f"which has real-time up-to-date information from the internet.\n"
            f"*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***\n"
            f"*** Just answer the question from the provided data in a professional way. ***"
        )
        backend.realtime_search_engine.SystemChatBot = [
            {"role": "system", "content": backend.realtime_search_engine.System},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": f"Hello {username}! Sir. How can I help you?"},
        ]
    except Exception:
        pass
