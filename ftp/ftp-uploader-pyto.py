# ftp-pyto.py

import os
import shutil
from ftplib import FTP, error_perm
from dotenv import load_dotenv

from ftp.ftp import FTPUploader

# Load environment variables from .env file
load_dotenv()

# Get FTP configuration from environment variables
FTP_HOST = os.getenv('FTP_HOST', '192.168.0.170')
FTP_PORT = int(os.getenv('FTP_PORT', '2121'))
FTP_USER = os.getenv('FTP_USER', 'anonymous')
FTP_PASS = os.getenv('FTP_PASS', '')
FTP_REMOTE_DIR = os.getenv('FTP_REMOTE_DIR', '')
FTP_BLOCK_SIZE = int(os.getenv('FTP_BLOCK_SIZE', '8192'))
FTP_RETRIES = int(os.getenv('FTP_RETRIES', '3'))
BUFFER_DIR = "file-buffer"


def gather_buffered_files():
    """
    Returns a list of (file-handle, filename) tuples
    for every file inside BUFFER_DIR.
    """
    items = []
    if not os.path.isdir(BUFFER_DIR):
        print(f"[WARN] Buffer dir '{BUFFER_DIR}' does not exist.")
        return items

    for fname in os.listdir(BUFFER_DIR):
        path = os.path.join(BUFFER_DIR, fname)
        if os.path.isfile(path):
            try:
                items.append(path)
            except Exception as e:
                print(f"[WARN] Couldn't open {fname!r}: {e}")
    return items

def clean_buffer():
    """Delete the entire BUFFER_DIR and recreate it empty."""
    if os.path.isdir(BUFFER_DIR):
        shutil.rmtree(BUFFER_DIR, ignore_errors=True)
    os.makedirs(BUFFER_DIR, exist_ok=True)
    print(f"[INFO] Emptied buffer dir '{BUFFER_DIR}'")

def main():
    try:
        uploader = FTPUploader(
            host=FTP_HOST,
            port=FTP_PORT,
            user=FTP_USER,
            passwd=FTP_PASS,    
            remote_dir=FTP_REMOTE_DIR,
            block_size=FTP_BLOCK_SIZE,
            retries=FTP_RETRIES
        )
        # 1) Gather files
        items = gather_buffered_files()
        if not items:
            print("[INFO] No files to upload. Exiting.")
            return
        
        # 2) Upload files
        uploader.upload_files(items)
        
        # 4) Finish FTP session
        uploader.disconnect()
        print("[INFO] FTP session closed.")

        # 5) Clean buffer folder
        clean_buffer()
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    main()
