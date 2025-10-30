import time
import mss
from pynput.mouse import Controller, Button

# ---------------- CONFIG ----------------
x, y = 126, 266                # pixel to monitor
idle_color = (34, 108, 168)    # idle color
target_color = (30, 151, 80)   # green trigger color
tolerance = 10                 # acceptable color variation
# ----------------------------------------

# Pre-initialize everything for maximum speed
mouse = Controller()
sct = mss.mss()
monitor = {"top": y, "left": x, "width": 1, "height": 1}

# Pre-set mouse position once to avoid repeated positioning
mouse.position = (x, y)

# Pre-calculate color bounds for faster comparison
idle_min = tuple(c - tolerance for c in idle_color)
idle_max = tuple(c + tolerance for c in idle_color)
target_min = tuple(c - tolerance for c in target_color)
target_max = tuple(c + tolerance for c in target_color)

# Optimized color comparison using bounds checking
def is_idle_color(pixel):
    return all(idle_min[i] <= pixel[i] <= idle_max[i] for i in range(3))

def is_target_color(pixel):
    return all(target_min[i] <= pixel[i] <= target_max[i] for i in range(3))

prev_state = None

# ✅ Ultra-fast main loop - removed all unnecessary delays
try:
    while True:
        # Direct pixel access - fastest method
        pixel = sct.grab(monitor).pixel(0, 0)

        # Fast state determination
        if is_idle_color(pixel):
            current_state = "idle"
        elif is_target_color(pixel):
            current_state = "green"
        else:
            current_state = "other"

        # Instant click on state change - no delays
        if current_state != prev_state and current_state in ["idle", "green"]:
            mouse.click(Button.left, 1)
            prev_state = current_state

except KeyboardInterrupt:
    pass  # Ctrl+C to exit

except Exception as e:
    print("Stopped:", e)