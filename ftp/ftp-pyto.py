# ftp-pyto.py

import datetime
import hashlib
import os
import io
import shutil
import pasteboard
import photos
from ftplib import FTP, error_perm

# ─── CONFIGURE THESE ──────────────────────────────────────────────────────────
HOST       = "192.168.1.170"
PORT       = 2121
USER       = "anonymous"
PASSWD     = ""
REMOTE_DIR = ""   # e.g. "uploads/photos"

BUFFER_DIR = "file-buffer"
# ─────────────────────────────────────────────────────────────────────────────

os.makedirs(BUFFER_DIR, exist_ok=True)

def upload_stream(ftp: FTP, stream, filename: str):
    """
    Upload a file-like object to the FTP server.
    """
    try:
        ftp.storbinary(f"STOR {filename}", stream)
        print(f"[SUCCESS] Uploaded {filename!r}")
    except error_perm as e:
        print(f"[ERROR] Permission denied for {filename!r}: {e}")
    except Exception as e:
        print(f"[ERROR] Upload failed for {filename!r}: {e}")

def gather_items():
    """
    Return a list of (file-like, filename) tuples from either
    Shortcuts attachments or the photo picker.
    """
    items = []
    providers = pasteboard.shortcuts_attachments()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if providers:
        print(f"[INFO] Found {len(providers)} attachment(s) from Shortcuts")
        for i, provider in enumerate(providers, 1):
            name = provider.get_suggested_name() or f"attachment_{i}"
            path = provider.get_file_path()

            if path:
                try:
                    f = open(path, "rb")
                    items.append((f, name))
                    continue
                except FileNotFoundError:
                    print(f"[WARNING] Path not accessible for {name!r}, falling back to streaming and buffering.")

            # Fallback: read from stream and write to disk
            with provider.open() as source:
                local_path = os.path.join(BUFFER_DIR, name)
                with open(local_path, "wb") as target:
                    while True:
                        chunk = source.read(8192)
                        if not chunk:
                            break
                        target.write(chunk)

            f = open(local_path, "rb")
            items.append((f, name))
    else:
        # Fallback: pick a single photo
        print("[INFO] No Shortcut attachments; opening photo picker…")
        img = photos.pick_photo()
        if img is None:
            print("[ERROR] No photo selected; exiting.")
            return []

        # Generate unique filename
        img_bytes = img.tobytes()
        short_hash = hashlib.md5(img_bytes).hexdigest()[:3]
        filename = f"photo_{timestamp}_{short_hash}.jpg"

        # Serialize to an in-memory JPEG
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        items.append((buf, filename))

    return items


def clean_buffer():
    if os.path.exists(BUFFER_DIR):
        shutil.rmtree(BUFFER_DIR)
        print(f"[INFO] Cleaned up '{BUFFER_DIR}' directory.")


def main():
    items = gather_items()
    if not items:
        return

    ftp = FTP()
    print(f"[INFO] Connecting to {HOST}:{PORT}…")
    ftp.connect(HOST, PORT)
    ftp.login(USER, PASSWD)
    if REMOTE_DIR:
        ftp.cwd(REMOTE_DIR)

    for stream, name in items:
        upload_stream(ftp, stream, name)
        stream.close()

    ftp.quit()
    print("[INFO] FTP session closed.")

    # Cleanup
    clean_buffer()


if __name__ == "__main__":
    main()
