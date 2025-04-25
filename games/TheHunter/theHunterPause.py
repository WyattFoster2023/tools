import os
import psutil
import ctypes
import keyboard
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

# Functions
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
        thread_ids = get_thread_ids(pid)
        for tid in thread_ids:
            h_thread = OpenThread(THREAD_SUSPEND_RESUME, False, tid)
            if h_thread:
                SuspendThread(h_thread)
                CloseHandle(h_thread)
        print(f"Process {pid} suspended.")
    except Exception as e:
        print(f"Failed to suspend process {pid}: {e}")

def resume_process(pid):
    try:
        thread_ids = get_thread_ids(pid)
        for tid in thread_ids:
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

if __name__ == "__main__":
    target = r"C:\Program Files (x86)\Steam\steamapps\common\theHunterCotW\theHunterCotW_F.exe"  # Replace with full path or process name
    pid = find_pid_by_path_or_name(target)
    if pid is None:
        print("Process not found.")
        exit()

    print(f"Monitoring process {pid}. Press Ctrl+Alt+S to suspend, Ctrl+Alt+R to resume.")

    keyboard.add_hotkey('ctrl+caps lock+s', lambda: toggle_process(pid))

    keyboard.wait('ctrl+alt+e')  # Keep the script running
    resume_process(pid)  # Ensure the process is resumed before exiting
