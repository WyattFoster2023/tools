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
    items = []
    providers = pasteboard.shortcuts_attachments()
    
    if providers:
        print(f"[INFO] Found {len(providers)} attachment(s)")
        
        for idx, provider in enumerate(providers, 1):
            # Determine a safe filename
            name = provider.get_suggested_name() or f"attachment_{idx}"
            local_path = os.path.join(BUFFER_DIR, name)
            
            # 1) Try copying directly from the iOS temp path
            path = provider.get_file_path()
            if path:
                try:
                    shutil.copy(path, local_path)
                    items.append((open(local_path, "rb"), name))
                    continue
                except Exception as e:
                    print(f"[WARN] Couldn’t copy {name} from '{path}': {e}")
            
            # 2) Try the documented .open() context manager
            try:
                with provider.open() as src:
                    with open(local_path, "wb") as dst:
                        # Stream-copy in 8K chunks
                        while True:
                            chunk = src.read(8192)
                            if not chunk:
                                break
                            dst.write(chunk)
                items.append((open(local_path, "rb"), name))
                continue
            except Exception as e:
                print(f"[WARN] provider.open() failed for {name}: {e}")
            
            # 3) Fallback: use .data(uti) for each supported UTI
            for uti in provider.get_type_identifiers():
                try:
                    data = provider.data(uti)     # may be large, but we write it out immediately
                    with open(local_path, "wb") as dst:
                        dst.write(data)
                    items.append((open(local_path, "rb"), name))
                    print(f"[INFO] Used .data({uti}) for {name}")
                    break
                except Exception:
                    continue
            else:
                print(f"[ERROR] Couldn’t buffer {name}; skipping.")
    
    else:
        # No attachments: pick one photo
        print("[INFO] No Shortcut attachments; opening photo picker…")
        img = photos.pick_photo()
        if not img:
            print("[ERROR] No photo selected.")
            return []
        
        # Photo → in-memory buffer → disk
        name = photos.get_last_photo_metadata().get("filename", "photo.jpg")
        local_path = os.path.join(BUFFER_DIR, name)
        with open(local_path, "wb") as dst:
            img.save(dst, format="JPEG")
        items.append((open(local_path, "rb"), name))
    
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
