import socket
import ctypes
import time
import sys
import asyncio
from ctypes import wintypes
from fastapi import FastAPI, Query
import uvicorn

app = FastAPI()

# Windows virtual key codes for media keys
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_STOP = 0xB2
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_LEFT = 0x25
VK_RIGHT = 0x27

# Windows API functions
keybd_event = ctypes.windll.user32.keybd_event

# Default skip duration per arrow key press (in seconds)
DEFAULT_SKIP_SECONDS_PER_PRESS = 5

def press_key(vk_code, delay=0.05):
    """Press and release a key with optional delay"""
    # Press key
    keybd_event(vk_code, 0, 0, 0)
    time.sleep(delay)
    # Release key
    keybd_event(vk_code, 0, 2, 0)  # 2 = KEYEVENTF_KEYUP

def toggle_play_pause():
    """Press and release a media key"""
    press_key(VK_MEDIA_PLAY_PAUSE)

def skip_backward(count: int = 1):
    """Skip backward by pressing left arrow key"""
    print(f"Skipping backward {count} times")
    for _ in range(count):
        press_key(VK_LEFT)
        time.sleep(0.1)  # Small delay between presses

def skip_forward(count: int = 1):
    """Skip forward by pressing right arrow key"""
    for _ in range(count):
        press_key(VK_RIGHT)
        time.sleep(0.1)  # Small delay between presses

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def exception_handler(loop, context):
    """Custom exception handler to suppress Windows socket shutdown errors"""
    exception = context.get('exception')
    if exception:
        # Suppress socket shutdown errors that are common on Windows ProactorEventLoop
        error_msg = str(exception).lower()
        if any(keyword in error_msg for keyword in ['shutdown', 'broken pipe', 'connection reset', 'an established connection was aborted']):
            # These are harmless connection cleanup errors on Windows
            return
    # Let other exceptions be handled normally
    loop.default_exception_handler(context)

@app.on_event("startup")
async def setup_exception_handler():
    """Set up exception handler on the event loop after uvicorn starts"""
    if sys.platform == 'win32':
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(exception_handler)

@app.post("/pause-play")
async def pause_play():
    """Toggle play/pause (Windows typically has one button for both)"""
    toggle_play_pause()
    return {"status": "ok", "action": "pause-play"}


@app.post("/back")
async def back(
    count: int = Query(None, description="Number of left arrow presses")
):
    """Skip backward (left arrow key presses)"""
    if count is not None:
        skip_backward(count)
        return {"status": "ok", "action": "back", "presses": count}
    else:
        # Default to 1 press
        skip_backward(1)
        return {"status": "ok", "action": "back", "presses": 1}

@app.post("/forward")
async def forward(
    count: int = Query(None, description="Number of right arrow presses")
):
    """Skip forward (right arrow key presses)"""
    if count is not None:
        skip_forward(count)
        return {"status": "ok", "action": "forward", "presses": count}
    else:
        # Default to 1 press
        skip_forward(1)
        return {"status": "ok", "action": "forward", "presses": 1}

@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "message": "TV Remote Server"}

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    local_ip = get_local_ip()
    
    print(f"TV Remote Server starting...")
    print(f"Server address: http://{local_ip}:{port}")
    print(f"Endpoints:")
    print(f"  POST http://{local_ip}:{port}/pause-play - Toggle play/pause")
    print(f"  POST http://{local_ip}:{port}/back?count=N - Skip backward N presses")
    print(f"  POST http://{local_ip}:{port}/forward?count=N - Skip forward N presses")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="warning",  # Reduce log noise
        access_log=False  # Disable access logs to reduce noise
    )

