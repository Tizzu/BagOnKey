import keyboard
import logging
import pystray
from PIL import Image, ImageDraw
import threading
import sys
import win32gui
import win32process
import psutil
import time  # Add this import

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def create_icon():
    image = Image.new('RGB', (64, 64), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 64, 64], fill="black")
    return image

def on_exit(icon):
    icon.stop()
    keyboard.unhook_all()
    sys.exit()

def run_tray():
    icon = pystray.Icon("keyboard_listener", create_icon(), "Keyboard Listener", menu=pystray.Menu(
        pystray.MenuItem('Exit', on_exit)
    ))
    icon.run()

def get_foreground_process_name():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        process = psutil.Process(pid)
        return process.name()
    except psutil.Error:
        return "Unknown"

def monitor_foreground_process():
    last_process = None
    while True:
        process_name = get_foreground_process_name()
        if process_name != last_process:
            logging.info(f'Foreground process changed to {process_name}')
            last_process = process_name
        time.sleep(0.5)  # Adjust the sleep interval as needed

def on_key(event):
    if event.name in ['f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24']:
        process_name = get_foreground_process_name()
        keyboard.press_and_release('win')
        logging.info(f'Key {event.name.upper()} pressed in process {process_name}')

# Start the tray icon thread
threading.Thread(target=run_tray).start()

# Start monitoring the foreground process
threading.Thread(target=monitor_foreground_process, daemon=True).start()

keyboard.on_press(on_key)
keyboard.wait()