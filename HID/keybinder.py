import keyboard
from typing import Callable, Dict
import threading

class KeyBinder:
    def __init__(self, exit_key: str = 'shift+esc'):
        self.bindings: Dict[str, Callable] = {}
        self.running = False
        self.exit_key = exit_key
        
    def register(self, key: str, func: Callable, suppress: bool = False):
        """Bind a function to a key or hotkey string."""
        self.bindings[key] = func
        keyboard.add_hotkey(key, func, suppress=suppress)

    def unregister(self, key: str):
        if key in self.bindings:
            keyboard.remove_hotkey(key)
            del self.bindings[key]

    def run(self):
        self.running = True
        print(f"KeyBinder is running. Press {self.exit_key} to exit.")
        keyboard.wait(self.exit_key)
        self.running = False

if __name__ == '__main__':
    binder = KeyBinder()
    binder.register('f23', lambda: print('F23 pressed!'))
    binder.run() 