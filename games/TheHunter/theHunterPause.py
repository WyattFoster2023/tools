import os
import psutil
import ctypes
import keyboard
import time
from ctypes import wintypes

# Constants
TH32CS_SNAPTHREAD = 0x00000004
THREAD_SUSPEND_RESUME = 0x0002

# Structures
class THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ThreadID", wintypes.DWORD),
        ("th32OwnerProcessID", wintypes.DWORD),
        ("tpBasePri", wintypes.LONG),
        ("tpDeltaPri", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
    ]

# Function declarations from kernel32
CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
Thread32First = ctypes.windll.kernel32.Thread32First
Thread32Next = ctypes.windll.kernel32.Thread32Next
OpenThread = ctypes.windll.kernel32.OpenThread
SuspendThread = ctypes.windll.kernel32.SuspendThread
ResumeThread = ctypes.windll.kernel32.ResumeThread
CloseHandle = ctypes.windll.kernel32.CloseHandle

def get_thread_ids(pid):
    thread_ids = []
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snapshot == -1:
        return thread_ids

    te32 = THREADENTRY32()
    te32.dwSize = ctypes.sizeof(THREADENTRY32)
    success = Thread32First(snapshot, ctypes.byref(te32))
    while success:
        if te32.th32OwnerProcessID == pid:
            thread_ids.append(te32.th32ThreadID)
        success = Thread32Next(snapshot, ctypes.byref(te32))
    CloseHandle(snapshot)
    return thread_ids

def suspend_process(pid):
    try:
        for tid in get_thread_ids(pid):
            h_thread = OpenThread(THREAD_SUSPEND_RESUME, False, tid)
            if h_thread:
                SuspendThread(h_thread)
                CloseHandle(h_thread)
        print(f"Process {pid} suspended.")
    except Exception as e:
        print(f"Failed to suspend process {pid}: {e}")

def resume_process(pid):
    try:
        for tid in get_thread_ids(pid):
            h_thread = OpenThread(THREAD_SUSPEND_RESUME, False, tid)
            if h_thread:
                while ResumeThread(h_thread) > 0:
                    pass
                CloseHandle(h_thread)
        print(f"Process {pid} resumed.")
    except Exception as e:
        print(f"Failed to resume process {pid}: {e}")

def find_pid_by_path_or_name(name_or_path):
    for proc in psutil.process_iter(['pid', 'exe', 'name']):
        try:
            if name_or_path.lower() in (proc.info['name'] or '').lower() or \
               os.path.abspath(name_or_path).lower() == os.path.abspath(proc.info['exe'] or '').lower():
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def get_process_state(pid):
    try:
        proc = psutil.Process(pid)
        return proc.status()
    except psutil.NoSuchProcess:
        return None

def toggle_process(pid):
    state = get_process_state(pid)
    if state == psutil.STATUS_STOPPED:
        resume_process(pid)
    else:
        suspend_process(pid)

# Debug/debounce mechanism to prevent multiple toggles on a single keypress
last_toggle_time = 0
last_autorun_time = 0
DEBOUNCE_DELAY = 0.5  # seconds

# Global variable to track autorun state
autorun_active = False

def toggle_process_callback():
    global last_toggle_time
    current_time = time.time()
    # Check if enough time has passed to consider this a new key event
    if current_time - last_toggle_time < DEBOUNCE_DELAY:
        print("Toggle process call debounced.")
        return
    last_toggle_time = current_time
    print("Toggling process state...")
    toggle_process(pid)

def toggle_autorun_callback():
    global last_autorun_time, autorun_active
    current_time = time.time()
    if current_time - last_autorun_time < DEBOUNCE_DELAY:
        print("Toggle autorun call debounced.")
        return
    last_autorun_time = current_time
    if autorun_active:
        keyboard.release('w')
        print("Autorun deactivated.")
    else:
        keyboard.press('w')
        print("Autorun activated.")
    autorun_active = not autorun_active

if __name__ == "__main__":
    target = r"C:\Program Files (x86)\Steam\steamapps\common\theHunterCotW\theHunterCotW_F.exe"
    pid = find_pid_by_path_or_name(target)
    if pid is None:
        print("Process not found.")
        exit()

    print(f"Monitoring process {pid}.")
    print("Press Ctrl+Caps Lock+S to toggle process state.")
    print("Press Ctrl+Caps Lock+W to toggle autorun (hold/release 'w').")
    print("Press Ctrl+Alt+E to exit.")

    # Hotkeys without trigger_on_release can fire repeatedly if keys are held down.
    # The debounce callbacks help to prevent multiple toggles.
    keyboard.add_hotkey('-', toggle_process_callback)
    keyboard.add_hotkey('=', toggle_autorun_callback)

    keyboard.wait('ctrl+alt+e')
    if autorun_active:
        keyboard.release('w')
    resume_process(pid)
