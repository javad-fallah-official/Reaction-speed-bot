import time
import mss
import numpy as np
import pyautogui

# ---------------- CONFIG ----------------
x, y = 126, 266                # position to monitor
idle_color = (34, 108, 168)    # blueish normal color
target_color = (30, 151, 80)   # green color
tolerance = 15                 # acceptable color difference
poll_delay = 0.01              # how often to check (lower = faster)
click_delay = 0.1              # delay after each click
# ----------------------------------------

pyautogui.FAILSAFE = True  # move mouse to top-left corner to stop safely

def color_is_close(c1, c2, tol):
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))

def get_pixel_color(sct, x, y):
    img = sct.grab({"top": y, "left": x, "width": 1, "height": 1})
    return img.pixel(0, 0)  # returns (r, g, b)

def main():
    sct = mss.mss()
    prev_state = None
    print(f"Watching pixel ({x}, {y}) for state changes...")
    print("Move mouse to top-left corner to abort.\n")

    try:
        while True:
            pixel = get_pixel_color(sct, x, y)

            if color_is_close(pixel, idle_color, tolerance):
                current_state = "idle"
            elif color_is_close(pixel, target_color, tolerance):
                current_state = "green"
            else:
                current_state = "other"

            # Click only when state switches between idle and green
            if current_state != prev_state:
                if current_state in ["idle", "green"]:
                    print(f"{time.strftime('%H:%M:%S')} Detected {current_state} → click")
                    pyautogui.click(x, y)
                    time.sleep(click_delay)
                prev_state = current_state

            time.sleep(poll_delay)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except pyautogui.FailSafeException:
        print("\nStopped by moving mouse to top-left corner.")

if __name__ == "__main__":
    main()
