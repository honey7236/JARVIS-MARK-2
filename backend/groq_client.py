import os
import threading

# Global state to share key rotation across all client instances
_global_keys = []
_global_current_key_index = 0
_global_lock = threading.Lock()
_initialized = False

def _initialize_keys():
    """Manually parses the .env file to extract all values of GroqAPIKey, preserving duplicates."""
    global _global_keys, _initialized
    with _global_lock:
        if _initialized:
            return
        
        keys = []
        # Check potential paths for the .env file
        env_paths = [".env", "../.env", "../../.env", "backend/.env"]
        for path in env_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                parts = line.split("=", 1)
                                key_name = parts[0].strip()
                                key_val = parts[1].strip()
                                # Strip optional surrounding quotes
                                if (key_val.startswith('"') and key_val.endswith('"')) or \
                                   (key_val.startswith("'") and key_val.endswith("'")):
                                    key_val = key_val[1:-1].strip()
                                if key_name == "GroqAPIKey" and key_val:
                                    if key_val not in keys:
                                        keys.append(key_val)
                    # Stop searching once we successfully read a .env file containing keys
                    if keys:
                        break
                except Exception as e:
                    print(f"[GroqWrapper] Error reading {path} for Groq keys: {e}")
        
        # Fallback to the environment variable if no keys were found in the .env files
        env_key = os.environ.get("GroqAPIKey")
        if env_key and env_key not in keys:
            keys.append(env_key)
            
        _global_keys = keys
        _initialized = True
        
        if _global_keys:
            print(f"[GroqWrapper] Loaded {len(_global_keys)} Groq API keys.")
        else:
            print(f"[GroqWrapper] WARNING: No Groq API keys found in .env or environment variables.")

class Groq:
    """A wrapper around the Groq client that supports thread-safe key rotation and automatic retry."""
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self.last_sync_index = -1
        
        _initialize_keys()
        
        # If an api_key was explicitly passed and is not in our global list, register it
        passed_key = kwargs.get("api_key")
        if passed_key:
            with _global_lock:
                if passed_key not in _global_keys:
                    _global_keys.append(passed_key)

    def _ensure_sync(self):
        """Synchronizes this instance with the globally active API key index."""
        global _global_current_key_index
        if self.last_sync_index != _global_current_key_index:
            with _global_lock:
                if not _global_keys:
                    raise ValueError("No Groq API keys found in .env or environment variables.")
                
                if _global_current_key_index >= len(_global_keys):
                    _global_current_key_index = 0
                
                self.last_sync_index = _global_current_key_index
                key = _global_keys[self.last_sync_index]
                masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "..."
                print(f"[GroqWrapper] Synced client to key index {self.last_sync_index} ({masked_key})")
                
                kwargs = self._kwargs.copy()
                kwargs["api_key"] = key
                
                from groq import Groq as Groq_Original
                self.client = Groq_Original(*self._args, **kwargs)

    def rotate_key(self):
        """Rotates the active key index globally and syncs the current client instance."""
        global _global_current_key_index
        with _global_lock:
            if len(_global_keys) <= 1:
                print("[GroqWrapper] Only one API key available. Cannot rotate.")
                return False
            
            _global_current_key_index = (_global_current_key_index + 1) % len(_global_keys)
            
        self._ensure_sync()
        return True

    @property
    def chat(self):
        self._ensure_sync()
        return ChatWrapper(self)

    def __getattr__(self, name):
        self._ensure_sync()
        return getattr(self.client, name)

class ChatWrapper:
    def __init__(self, wrapper):
        self.wrapper = wrapper

    @property
    def completions(self):
        return CompletionsWrapper(self.wrapper)

    def __getattr__(self, name):
        return getattr(self.wrapper.client.chat, name)

class CompletionsWrapper:
    def __init__(self, wrapper):
        self.wrapper = wrapper

    def create(self, *args, **kwargs):
        """Wraps the creation of chat completions, adding retry and rotation logic."""
        global _global_keys
        with _global_lock:
            num_keys = len(_global_keys)
            
        last_error = None
        # Attempt to run the request. We allow up to num_keys attempts.
        for attempt in range(max(1, num_keys)):
            try:
                self.wrapper._ensure_sync()
                return self.wrapper.client.chat.completions.create(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Check for rate limits, quota issues, auth errors, or any Groq API exception
                is_key_error = any(
                    x in error_msg 
                    for x in ["rate_limit", "rate limit", "quota", "exhausted", "limit exceeded", "429", "401", "unauthorized", "invalid api key", "api_key", "forbidden", "403"]
                )
                is_groq_exception = "groq" in str(type(e)).lower()
                
                if is_key_error or is_groq_exception:
                    current_key = _global_keys[self.wrapper.last_sync_index] if self.wrapper.last_sync_index < len(_global_keys) else "unknown"
                    masked_key = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "..."
                    print(f"[GroqWrapper] API key error encountered with key index {self.wrapper.last_sync_index} ({masked_key}): {e}")
                    
                    if self.wrapper.rotate_key():
                        print(f"[GroqWrapper] Retrying request with the next key index {self.wrapper.last_sync_index}...")
                        continue
                    else:
                        raise e
                else:
                    # Raise immediately for user-side validation errors or unexpected errors
                    raise e
                    
        if last_error:
            raise last_error
        else:
            raise RuntimeError("All Groq API keys are exhausted.")
