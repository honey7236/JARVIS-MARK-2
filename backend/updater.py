import asyncio
import logging
import os
import re
import subprocess
import tempfile
import threading
import urllib.request
import json
import sys

logger = logging.getLogger(__name__)

CURRENT_VERSION = "2.0.0"
GITHUB_REPO = "honey7236/JARVIS-MARK-2"

# Global download state variables
download_progress = 0
download_status = "idle"
download_thread = None

def parse_version(version_str):
    """
    Parses version string like 'v2.0.0' or '2.0.1-beta' into a tuple of integers for comparison.
    """
    version_str = version_str.lower().strip().lstrip('v')
    parts = []
    for p in re.split(r'[-.]', version_str):
        digits = ''.join(c for c in p if c.isdigit())
        if digits:
            parts.append(int(digits))
        else:
            break  # Stop parsing at suffix (e.g. beta) for safe digit comparison
    return tuple(parts)

def check_for_updates_sync():
    """
    Queries the GitHub Releases API synchronously to fetch the latest release metadata.
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'JARVIS-Mark-II-Updater'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            latest_tag = data.get("tag_name", "0.0.0")
            changelog = data.get("body", "No changelog provided.")
            assets = data.get("assets", [])
            
            # Find the first executable asset
            download_url = None
            for asset in assets:
                name = asset.get("name", "")
                if name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    break
            
            # Fallback to html_url if no direct .exe asset is found
            if not download_url:
                download_url = data.get("html_url")
                
            latest_v = parse_version(latest_tag)
            current_v = parse_version(CURRENT_VERSION)
            
            update_available = latest_v > current_v
            
            return {
                "success": True,
                "update_available": update_available,
                "current_version": CURRENT_VERSION,
                "latest_version": latest_tag,
                "changelog": changelog,
                "download_url": download_url
            }
    except Exception as e:
        logger.error(f"[Updater] Network error while checking for updates: {e}")
        return {
            "success": False,
            "error": str(e),
            "current_version": CURRENT_VERSION
        }

def _download_worker(download_url):
    global download_progress, download_status
    download_status = "downloading"
    download_progress = 0
    
    try:
        temp_dir = tempfile.gettempdir()
        dest_path = os.path.join(temp_dir, "JarvisSetup_Update.exe")
        
        req = urllib.request.Request(
            download_url,
            headers={'User-Agent': 'JARVIS-Mark-II-Updater'}
        )
        
        with urllib.request.urlopen(req) as response:
            total_size = int(response.info().get('Content-Length', 0))
            bytes_downloaded = 0
            block_size = 1024 * 64  # 64KB chunks
            
            with open(dest_path, 'wb') as out_file:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    out_file.write(buffer)
                    bytes_downloaded += len(buffer)
                    if total_size:
                        download_progress = int((bytes_downloaded / total_size) * 100)
                    else:
                        download_progress = 50
                        
        download_status = "ready"
        download_progress = 100
        logger.info(f"[Updater] Downloaded update installer to {dest_path}. Spawning installer...")
        
        # Spawn the installer in a detached process and terminate current session
        subprocess.Popen([dest_path], shell=False)
        os._exit(0)
        
    except Exception as e:
        logger.error(f"[Updater] Download failed: {e}", exc_info=True)
        download_status = "failed"
        download_progress = 0

def start_download_async(download_url):
    global download_thread, download_status, download_progress
    if download_status == "downloading":
        return False
        
    download_status = "downloading"
    download_progress = 0
    download_thread = threading.Thread(target=_download_worker, args=(download_url,), daemon=True)
    download_thread.start()
    return True

# Expose functions to Eel
try:
    import eel
    @eel.expose
    def check_for_updates():
        return check_for_updates_sync()

    @eel.expose
    def start_update_download(download_url):
        return start_download_async(download_url)

    @eel.expose
    def get_update_progress():
        global download_status, download_progress
        return {
            "status": download_status,
            "progress": download_progress
        }
except ImportError:
    pass
