import time
import mss
from pynput.mouse import Controller, Button

# ---------------- CONFIG ----------------
x, y = 126, 266                # pixel to monitor
idle_color = (34, 108, 168)    # idle color
target_color = (30, 151, 80)   # green trigger color
tolerance = 10                 # acceptable color variation
poll_delay = 0.0001             # 1 ms polling
click_delay = 0.01             # tiny delay after click to prevent double clicks
# ----------------------------------------

mouse = Controller()
sct = mss.mss()
monitor = {"top": y, "left": x, "width": 1, "height": 1}

def color_is_close(c1, c2, tol):
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))

prev_state = None

# ✅ Main loop
try:
    while True:
        pixel = sct.grab(monitor).pixel(0, 0)

        if color_is_close(pixel, idle_color, tolerance):
            current_state = "idle"
        elif color_is_close(pixel, target_color, tolerance):
            current_state = "green"
        else:
            current_state = "other"

        # Toggle click when state changes between idle <-> green
        if current_state != prev_state:
            if current_state in ["idle", "green"]:
                mouse.position = (x, y)
                mouse.click(Button.left, 1)
                # optional tiny sleep to prevent double click
                time.sleep(click_delay)
            prev_state = current_state

        # minimal delay to reduce CPU usage
        time.sleep(poll_delay)

except KeyboardInterrupt:
    pass  # Ctrl+C to exit

except Exception as e:
    print("Stopped:", e)
