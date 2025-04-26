import tkinter as tk
from tkinter import filedialog
from ftp import FTPUploader
import os

import os
from dotenv import load_dotenv

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


def get_ui_files():
    # File selection dialog
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select file(s) to upload")
    root.destroy()

    if not file_paths:
        print("[INFO] No files selected. Exiting.")
        uploader.disconnect()
        return tuple([])
    return file_paths

    # Perform uploads
    uploader.upload_files(file_paths)
    uploader.disconnect()
    print("[INFO] All done.")

if __name__ == '__main__':
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

        file_paths = get_ui_files()
        uploader.upload_files(file_paths)
        uploader.disconnect()
        print("[INFO] All done.")
        
    except KeyboardInterrupt:
        print("[INFO] Upload canceled by user.")
    except Exception as e:
        print(f"[FATAL] Unexpected error: {e}")
