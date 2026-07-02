import json
import logging
import os
import tempfile
import threading

logger = logging.getLogger(__name__)
_lock = threading.RLock()

def _resolve_path(path):
    """
    Redirects relative paths (like 'data/contacts.json') to a writable directory
    inside the user's Local AppData to prevent PermissionError when installed in Program Files.
    """
    if not os.path.isabs(path):
        appdata_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "JARVIS_Mark_II")
        return os.path.join(appdata_dir, path)
    return path

def load_json(file_path, default=None):
    """
    Safely loads a JSON file. If the file is missing, empty, or corrupted,
    recreates it with the default value (after taking a backup of corrupted data).
    """
    file_path = _resolve_path(file_path)
    if default is None:
        default = []
        
    with _lock:
        if not os.path.exists(file_path):
            save_json(file_path, default)
            return default
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"[DataManager] JSON file {file_path} is empty. Overwriting with default.")
                    save_json(file_path, default)
                    return default
                return json.loads(content)
        except (json.JSONDecodeError, ValueError) as je:
            logger.error(f"[DataManager] JSON file {file_path} is corrupted: {je}", exc_info=True)
            bak_path = f"{file_path}.bak"
            try:
                if os.path.exists(file_path):
                    os.replace(file_path, bak_path)
                    logger.info(f"[DataManager] Backed up corrupted JSON to {bak_path}")
            except Exception as be:
                logger.error(f"[DataManager] Failed to back up corrupted file: {be}", exc_info=True)
                
            save_json(file_path, default)
            return default
        except Exception as e:
            logger.error(f"[DataManager] Error loading JSON file {file_path}: {e}", exc_info=True)
            return default

def save_json(file_path, data, indent=4):
    """
    Saves data to a JSON file atomically using a temporary file and os.replace.
    """
    file_path = _resolve_path(file_path)
    with _lock:
        try:
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
                
            tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name if dir_name else ".", suffix=".tmp", text=True)
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as tmp_file:
                    json.dump(data, tmp_file, indent=indent, ensure_ascii=False)
                os.replace(tmp_path, file_path)
                return True
            except Exception as write_err:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise write_err
        except Exception as e:
            logger.error(f"[DataManager] Failed to write JSON to {file_path} atomically: {e}", exc_info=True)
            return False

def read_text(file_path, default=""):
    """
    Safely reads a text file. Returns the default value if the file does not exist.
    """
    file_path = _resolve_path(file_path)
    with _lock:
        if not os.path.exists(file_path):
            return default
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"[DataManager] Error reading text file {file_path}: {e}", exc_info=True)
            return default

def write_text(file_path, content):
    """
    Writes content to a text file atomically using a temporary file.
    """
    file_path = _resolve_path(file_path)
    with _lock:
        try:
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
                
            tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name if dir_name else ".", suffix=".tmp", text=True)
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as tmp_file:
                    tmp_file.write(content)
                os.replace(tmp_path, file_path)
                return True
            except Exception as write_err:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise write_err
        except Exception as e:
            logger.error(f"[DataManager] Failed to write text to {file_path} atomically: {e}", exc_info=True)
            return False
