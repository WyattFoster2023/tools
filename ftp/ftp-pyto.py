# ftp-pyto.py

import os
import io
import pasteboard
import photos
from ftplib import FTP, error_perm

# ─── CONFIGURE THESE ──────────────────────────────────────────────────────────
HOST       = "192.168.1.17"
PORT       = 2121
USER       = "anonymous"
PASSWD     = ""
REMOTE_DIR = ""   # e.g. "uploads/photos"
# ─────────────────────────────────────────────────────────────────────────────

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

    if providers:
        print(f"[INFO] Found {len(providers)} attachment(s) from Shortcuts")
        for i, provider in enumerate(providers, 1):
            name = provider.get_suggested_name() or f"attachment_{i}"
            path = provider.get_file_path()

            if path:
                # Physical file on disk — stream it
                f = open(path, "rb")
            else:
                # Stream via the provider API
                f = provider.open()

            items.append((f, name))
    else:
        # Fallback: pick a single photo
        print("[INFO] No Shortcut attachments; opening photo picker…")
        img = photos.pick_photo()
        if img is None:
            print("[ERROR] No photo selected; exiting.")
            return []

        # Serialize to an in-memory JPEG
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        items.append((buf, "photo.jpg"))

    return items

def main():
    # 1) Gather items
    items = gather_items()
    if not items:
        return

    # 2) Connect to FTP
    ftp = FTP()
    print(f"[INFO] Connecting to {HOST}:{PORT}…")
    ftp.connect(HOST, PORT)
    ftp.login(USER, PASSWD)
    print(f"[INFO] Logged in as {USER!r}")
    if REMOTE_DIR:
        ftp.cwd(REMOTE_DIR)
        print(f"[INFO] Changed directory to {REMOTE_DIR!r}")

    # 3) Upload each
    for stream, name in items:
        upload_stream(ftp, stream, name)
        stream.close()

    # 4) Cleanup
    ftp.quit()
    print("[INFO] FTP session closed.")

if __name__ == "__main__":
    main()
