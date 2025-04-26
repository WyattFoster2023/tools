import os
import shutil
import sys
import zipfile
from urllib.request import urlopen
from io import BytesIO
import json
from dotenv import load_dotenv

import subprocess

load_dotenv()

# === CONFIGURATION ===
REPO_OWNER = os.getenv('REPO_OWNER', 'WyattFoster2023')
REPO_NAME = os.getenv('REPO_NAME', 'tools')
BRANCH = os.getenv('BRANCH', 'main')
STATE_FILE = os.getenv('STATE_FILE', '.update_state.json')

# Dynamic URLs
API_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{BRANCH}'
ZIP_URL = f'https://github.com/{REPO_OWNER}/{REPO_NAME}/archive/refs/heads/{BRANCH}.zip'

def get_latest_commit():
    try:
        with urlopen(API_URL, timeout=6) as response:
            data = json.loads(response.read())
            return data['sha']
    except Exception as e:
        print(f"[WARN] Could not fetch latest commit: {e}")
        return None

def load_last_commit():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f).get('last_commit')
    return None

def save_last_commit(commit_hash):
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_commit': commit_hash}, f)

def download_and_extract_repo():
    print(f"[INFO] Downloading latest version from {BRANCH} branch...")
    with urlopen(ZIP_URL) as response:
        with zipfile.ZipFile(BytesIO(response.read())) as zip_file:
            temp_dir = '__temp_update__'
            zip_file.extractall(temp_dir)
            extracted_folder = os.path.join(temp_dir, f'{REPO_NAME}-{BRANCH}')

            for item in os.listdir(extracted_folder):
                if item == STATE_FILE:
                    continue  # Don't overwrite state (we want to update this script)
                s = os.path.join(extracted_folder, item)
                d = os.path.join('.', item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            shutil.rmtree(temp_dir)
    print("[INFO] Update complete.")

def self_update():
    latest_commit = get_latest_commit()
    if not latest_commit:
        return  # Skip update if API fails
    last_commit = load_last_commit()

    if latest_commit != last_commit:
        print("[UPDATE] New version detected. Updating...")
        download_and_extract_repo()
        save_last_commit(latest_commit)
        print("[INFO] Restarting to load updates...\n")
        # Restart the script in the same terminal session
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        print("[INFO] Already up to date.")

if __name__ == '__main__':
    self_update()
    # === Place your tool logic here ===
    while True:
        cmd = input("tools> ").strip()
        if cmd == 'exit':
            break
        self_update()   # Check for updates before each command
        
        try:
            if cmd == 'ftp':
                subprocess.run(['python', 'ftp/ftp-uploader-ui.py'])
        except Exception as e:
            print(f"[ERROR] Failed to run FTP uploader: {e}")
