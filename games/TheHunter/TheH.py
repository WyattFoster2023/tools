import psutil
import keyboard
import os
import time
import threading

# === CONFIG ===
EXECUTABLE_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\theHunterCotW\theHunterCotW_F.exe"

# === STATE ===
target_proc = None

def find_process_by_path(path):
    for proc in psutil.process_iter(['exe']):
        try:
            if proc.info['exe'] and os.path.normcase(proc.info['exe']) == os.path.normcase(path):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def is_process_suspended(proc):
    try:
        return all(thread.status == psutil.STATUS_STOPPED for thread in proc.threads())
    except psutil.NoSuchProcess:
        return False

def toggle_process():
    global target_proc
    if not target_proc or not target_proc.is_running():
        print("Process exited.")
        return

    if is_process_suspended(target_proc):
        print("Resuming process...")
        target_proc.resume()
    else:
        print("Suspending process...")
        target_proc.suspend()

def main():
    global target_proc

    target_proc = find_process_by_path(EXECUTABLE_PATH)
    if not target_proc:
        print("Target process not found.")
        return

    print("Hook ready. Press Ctrl + Caps Lock + S to toggle. Esc to exit.")

    keyboard.add_hotkey('ctrl+caps lock+s', toggle_process)

    # Block until ESC is pressed
    keyboard.wait('esc')

    # Ensure it's resumed on exit
    if is_process_suspended(target_proc):
        print("Resuming process before exit...")
        try:
            target_proc.resume()
        except psutil.NoSuchProcess:
            pass

if __name__ == "__main__":
    main()
