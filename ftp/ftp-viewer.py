import os
import tkinter as tk
from tkinter import filedialog
from ftplib import FTP, error_perm
from tqdm import tqdm

class FTPUploader:
    """
    A class to manage FTP connection and file uploads with retries and progress bars.
    """
    def __init__(
        self,
        host: str,
        port: int = 21,
        user: str = 'anonymous',
        passwd: str = '',
        remote_dir: str = '',
        block_size: int = 8192,
        retries: int = 3,
        timeout: int = 10
    ):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.remote_dir = remote_dir
        self.block_size = block_size
        self.retries = retries
        self.timeout = timeout
        self.ftp = None

    def ftp_connect(self):
        """Establishes FTP connection and logs in."""
        print(f"[INFO] Connecting to {self.host}:{self.port}...")
        self.ftp = FTP()
        self.ftp.connect(self.host, self.port, timeout=self.timeout)
        self.ftp.login(self.user, self.passwd)
        print(f"[INFO] Logged in as '{self.user}'.")
        if self.remote_dir:
            self.ftp.cwd(self.remote_dir)
            print(f"[INFO] Changed remote directory to '{self.remote_dir}'.")

    def disconnect(self):
        """Closes FTP connection."""
        if self.ftp:
            try:
                self.ftp.quit()
                print("[INFO] FTP connection closed.")
            except Exception as e:
                print(f"[WARNING] Error closing connection: {e}")
            finally:
                self.ftp = None

    def reconnect(self):
        """Reconnects by closing existing connection and establishing a new one."""
        print("[INFO] Reconnecting FTP...")
        self.disconnect()
        self.ftp_connect()

    def upload_file(self, file_path: str):
        """Uploads a single file with progress bar and retry logic."""
        if not os.path.isfile(file_path):
            print(f"[ERROR] '{file_path}' is not a file. Skipping.")
            return

        filename = os.path.basename(file_path)
        size = os.path.getsize(file_path)

        with tqdm(
            total=size,
            unit='B',
            unit_scale=True,
            desc=f"Uploading {filename}",
            leave=True,
            ascii=True
        ) as pbar:

            def callback(chunk: bytes):
                pbar.update(len(chunk))

            for attempt in range(1, self.retries + 1):
                try:
                    with open(file_path, 'rb') as f:
                        self.ftp.storbinary(f'STOR {filename}', f, self.block_size, callback)
                    print(f"[SUCCESS] Uploaded '{filename}'.")
                    return

                except error_perm as e:
                    print(f"[ERROR] Permission denied uploading '{filename}': {e}")
                    return

                except Exception as e:
                    print(f"[ERROR] Attempt {attempt}/{self.retries} failed for '{filename}': {e}")
                    if attempt < self.retries:
                        self.reconnect()
                    else:
                        print(f"[WARNING] Failed to upload '{filename}' after {self.retries} attempts.")

    def upload_files(self, file_paths):
        """Uploads multiple files in sequence."""
        for path in file_paths:
            self.upload_file(path)


def main():
    uploader = FTPUploader(
        host='192.168.0.170',
        port=2121,
        user='anonymous',
        passwd='',
        remote_dir='',
        block_size=8192,
        retries=3
    )

    try:
        uploader.ftp_connect()
    except Exception as e:
        print(f"[FATAL] Could not connect: {e}")
        return

    # File selection dialog
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select file(s) to upload")
    root.destroy()

    if not file_paths:
        print("[INFO] No files selected. Exiting.")
        uploader.disconnect()
        return

    # Perform uploads
    uploader.upload_files(file_paths)
    uploader.disconnect()
    print("[INFO] All done.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] Upload canceled by user.")
    except Exception as e:
        print(f"[FATAL] Unexpected error: {e}")
