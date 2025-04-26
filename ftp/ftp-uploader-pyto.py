# ftp-pyto.py

import os
import shutil
from ftplib import FTP, error_perm
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# ─── CONFIG ──────────────────────────────────────────────────────────────────
FTP_HOST = os.getenv('FTP_HOST', '192.168.0.170')
FTP_PORT = int(os.getenv('FTP_PORT', '2121'))
FTP_USER = os.getenv('FTP_USER', 'anonymous')
FTP_PASS = os.getenv('FTP_PASS', '')
FTP_REMOTE_DIR = os.getenv('FTP_REMOTE_DIR', '')
BUFFER_DIR = "file-buffer"
# ─────────────────────────────────────────────────────────────────────────────


def upload_stream(ftp: FTP, stream, filename: str):
    try:
        ftp.storbinary(f"STOR {filename}", stream)
        print(f"[SUCCESS] Uploaded {filename!r}")
    except error_perm as e:
        print(f"[ERROR] Permission denied for {filename!r}: {e}")
    except Exception as e:
        print(f"[ERROR] Upload failed for {filename!r}: {e}")

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
                f = open(path, "rb")
                items.append((f, fname))
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
    # 1) Gather files
    items = gather_buffered_files()
    if not items:
        print("[INFO] No files to upload. Exiting.")
        return

    # 2) Connect & login
    ftp = FTP()
    print(f"[INFO] Connecting to {FTP_HOST}:{FTP_PORT}…")
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(FTP_USER, FTP_PASS)
    print(f"[INFO] Logged in as {FTP_USER!r}")
    if FTP_REMOTE_DIR:
        ftp.cwd(FTP_REMOTE_DIR)
        print(f"[INFO] Changed to remote dir '{FTP_REMOTE_DIR}'")

    # 3) Upload each file
    for stream, name in items:
        upload_stream(ftp, stream, name)
        stream.close()

    # 4) Finish FTP session
    ftp.quit()
    print("[INFO] FTP session closed.")

    # 5) Clean buffer folder
    clean_buffer()

if __name__ == "__main__":
    main()
