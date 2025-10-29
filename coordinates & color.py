import pyautogui
import keyboard
import time
from datetime import datetime

FILE_PATH = "saved_points.txt"

print("Move your mouse to any point.")
print("Press Ctrl+F12 to save coordinate & color.")
print("Press Esc to quit.\n")

def get_pixel_info():
    x, y = pyautogui.position()
    pixel = pyautogui.screenshot().getpixel((x, y))
    return x, y, pixel

def save_to_file(x, y, color):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | x={x}, y={y}, RGB={color}\n"
    with open(FILE_PATH, "a") as f:  # "a" = append
        f.write(entry)
    print(f"Saved: {entry.strip()}")

try:
    while True:
        if keyboard.is_pressed("ctrl+f12"):
            x, y, pixel = get_pixel_info()
            save_to_file(x, y, pixel)
            time.sleep(0.5)  # prevent double trigger
        if keyboard.is_pressed("esc"):
            print("Exiting.")
            break
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nStopped manually.")
