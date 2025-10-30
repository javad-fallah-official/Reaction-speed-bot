import ctypes
from ctypes import wintypes

# ---------------- CONFIG ----------------
x, y = 126, 266                # pixel to monitor
idle_color = (34, 108, 168)    # idle color
target_color = (30, 151, 80)   # green trigger color
tolerance = 10                 # acceptable color variation
# ----------------------------------------

# Pre-calculate color bounds (avoids function calls in hot path)
idle_min = (idle_color[0] - tolerance, idle_color[1] - tolerance, idle_color[2] - tolerance)
idle_max = (idle_color[0] + tolerance, idle_color[1] + tolerance, idle_color[2] + tolerance)
target_min = (target_color[0] - tolerance, target_color[1] - tolerance, target_color[2] - tolerance)
target_max = (target_color[0] + tolerance, target_color[1] + tolerance, target_color[2] + tolerance)

# ---- Windows API bindings (ctypes, zero external deps) ----
user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

# Fallback for missing wintypes.ULONG_PTR on some Python builds
try:
    ULONG_PTR = wintypes.ULONG_PTR
except AttributeError:
    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

# Elevate process/thread priority and pin to one CPU to reduce scheduling jitter
HIGH_PRIORITY_CLASS = 0x00000080
THREAD_PRIORITY_TIME_CRITICAL = 15
kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), HIGH_PRIORITY_CLASS)
kernel32.SetThreadPriority(kernel32.GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)
kernel32.SetThreadAffinityMask(kernel32.GetCurrentThread(), 0x00000001)  # CPU 0

# Position cursor once to the target pixel to avoid SetCursorPos calls in loop
user32.SetCursorPos(x, y)

# Acquire screen DC once
hdc = user32.GetDC(None)
GetPixel = gdi32.GetPixel

# Prepare SendInput structures for ultra-fast click injection
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]

class _INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", ctypes.c_ulong), ("u", _INPUT_UNION)]

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004

down = INPUT(type=INPUT_MOUSE, u=_INPUT_UNION(mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, 0)))
up   = INPUT(type=INPUT_MOUSE, u=_INPUT_UNION(mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP,   0, 0)))

SendInput = user32.SendInput
sizeof_INPUT = ctypes.sizeof(INPUT)

def click_fast():
    SendInput(1, ctypes.byref(down), sizeof_INPUT)
    SendInput(1, ctypes.byref(up), sizeof_INPUT)

prev_state = 2  # 0=idle, 1=green, 2=other

try:
    while True:
        # Read pixel via GDI (single call, minimal overhead)
        colorref = GetPixel(hdc, x, y)
        r = colorref & 0xFF
        g = (colorref >> 8) & 0xFF
        b = (colorref >> 16) & 0xFF

        # Bounds check without function calls
        if (idle_min[0] <= r <= idle_max[0] and
            idle_min[1] <= g <= idle_max[1] and
            idle_min[2] <= b <= idle_max[2]):
            state = 0
        elif (target_min[0] <= r <= target_max[0] and
              target_min[1] <= g <= target_max[1] and
              target_min[2] <= b <= target_max[2]):
            state = 1
        else:
            state = 2

        # Instant click only on state transition into actionable states
        if state != prev_state and state != 2:
            click_fast()
            prev_state = state

except KeyboardInterrupt:
    pass
except Exception as e:
    # Minimal error surface; avoid prints in hot path
    try:
        print("Stopped:", e)
    except Exception:
        pass
