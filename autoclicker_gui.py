"""
Ultra-Fast Autoclicker — GUI Edition
=====================================
Requires: Python 3.6+ on Windows (tkinter is built-in)
Package : pyinstaller autoclicker_gui.py --onefile --noconsole --name AutoClicker
"""

import ctypes
import ctypes.wintypes
import time
import threading
import tkinter as tk
from tkinter import font as tkfont

# ── Windows API ───────────────────────────────────────────────────────────────

user32 = ctypes.windll.user32

INPUT_MOUSE          = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004
VK_F6 = 0x75
VK_F7 = 0x76

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx",          ctypes.wintypes.LONG),
        ("dy",          ctypes.wintypes.LONG),
        ("mouseData",   ctypes.wintypes.DWORD),
        ("dwFlags",     ctypes.wintypes.DWORD),
        ("time",        ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class _INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.wintypes.DWORD), ("_input", _INPUT_UNION)]

_down             = INPUT(); _down.type = INPUT_MOUSE; _down._input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
_up               = INPUT(); _up.type   = INPUT_MOUSE; _up._input.mi.dwFlags   = MOUSEEVENTF_LEFTUP
_click_sequence   = (INPUT * 2)(_down, _up)
_sequence_ptr     = ctypes.cast(_click_sequence, ctypes.POINTER(INPUT))
_input_size       = ctypes.sizeof(INPUT)

def _send_click():
    user32.SendInput(2, _sequence_ptr, _input_size)

# ── Clicker engine ────────────────────────────────────────────────────────────

class Autoclicker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._active   = threading.Event()
        self._stopping = threading.Event()
        self._lock     = threading.Lock()
        self.cps       = 0.0
        self.total     = 0

    def start_clicking(self):  self._active.set()
    def stop_clicking(self):   self._active.clear()
    def shutdown(self):
        self._stopping.set()
        self._active.set()

    @property
    def running(self):
        return self._active.is_set()

    def run(self):
        while not self._stopping.is_set():
            self._active.wait()
            t0 = time.perf_counter(); n = 0
            while self._active.is_set() and not self._stopping.is_set():
                _send_click(); n += 1
                now = time.perf_counter()
                if now - t0 >= 0.25:          # update stats 4× per second
                    with self._lock:
                        self.cps    = n / (now - t0)
                        self.total += n
                    n = 0; t0 = now
            if n:
                with self._lock:
                    elapsed = time.perf_counter() - t0 or 1e-9
                    self.cps    = n / elapsed
                    self.total += n

# ── GUI ───────────────────────────────────────────────────────────────────────

# Palette
BG       = "#0d0d0d"
PANEL    = "#141414"
ACCENT   = "#00ff88"
ACCENT2  = "#00cc66"
DIM      = "#333333"
TEXT     = "#e8e8e8"
MUTED    = "#555555"
RED      = "#ff3355"
RED2     = "#cc2244"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoClicker")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.geometry("360x560")
        self.attributes("-topmost", True)

        # custom window chrome workaround — remove default titlebar on some themes
        try:
            self.overrideredirect(False)
        except Exception:
            pass

        self.clicker = Autoclicker()
        self.clicker.start()

        self._hotkey_prev_f6 = False
        self._hotkey_prev_f7 = False

        self._build_ui()
        self._poll_hotkeys()
        self._tick()

        self.protocol("WM_DELETE_WINDOW", self._quit)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        pad = dict(padx=20)

        # ── header ──
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(24, 0), **pad)

        tk.Label(header, text="AUTO", font=("Courier New", 28, "bold"),
                 fg=ACCENT, bg=BG, anchor="w").pack(side="left")
        tk.Label(header, text="CLICKER", font=("Courier New", 28, "bold"),
                 fg=TEXT, bg=BG, anchor="w").pack(side="left")

        tk.Label(self, text="HIGH-PERFORMANCE MOUSE INPUT ENGINE",
                 font=("Courier New", 7), fg=MUTED, bg=BG).pack(anchor="w", padx=20, pady=(0, 16))

        # ── separator ──
        tk.Frame(self, bg=DIM, height=1).pack(fill="x", padx=20)

        # ── CPS readout ──
        readout_frame = tk.Frame(self, bg=PANEL, bd=0)
        readout_frame.pack(fill="x", padx=20, pady=(16, 0))

        inner = tk.Frame(readout_frame, bg=PANEL)
        inner.pack(pady=18, padx=20, fill="x")

        tk.Label(inner, text="CLICKS / SEC", font=("Courier New", 8),
                 fg=MUTED, bg=PANEL).pack(anchor="w")

        self._cps_var = tk.StringVar(value="0")
        tk.Label(inner, textvariable=self._cps_var,
                 font=("Courier New", 52, "bold"),
                 fg=ACCENT, bg=PANEL, anchor="w").pack(anchor="w")

        tk.Label(inner, text="TOTAL CLICKS", font=("Courier New", 8),
                 fg=MUTED, bg=PANEL).pack(anchor="w", pady=(8, 0))

        self._total_var = tk.StringVar(value="0")
        tk.Label(inner, textvariable=self._total_var,
                 font=("Courier New", 16, "bold"),
                 fg=TEXT, bg=PANEL, anchor="w").pack(anchor="w")

        # ── status bar ──
        self._status_frame = tk.Frame(self, bg=DIM, height=3)
        self._status_frame.pack(fill="x", padx=20, pady=(0, 16))

        # ── big toggle button ──
        self._btn = tk.Button(
            self,
            text="▶  START CLICKING",
            font=("Courier New", 13, "bold"),
            fg=BG, bg=ACCENT, activebackground=ACCENT2, activeforeground=BG,
            bd=0, padx=0, pady=14,
            cursor="hand2",
            command=self._toggle,
        )
        self._btn.pack(fill="x", padx=20)

        # ── hotkey hint ──
        hint = tk.Frame(self, bg=BG)
        hint.pack(fill="x", padx=20, pady=(10, 0))

        for key, label in [("F6", "START / STOP"), ("F7", "QUIT")]:
            cell = tk.Frame(hint, bg=BG)
            cell.pack(side="left", padx=(0, 16))
            tk.Label(cell, text=key, font=("Courier New", 9, "bold"),
                     fg=BG, bg=MUTED, padx=5, pady=1).pack(side="left")
            tk.Label(cell, text=f"  {label}", font=("Courier New", 8),
                     fg=MUTED, bg=BG).pack(side="left")

        # ── reset button ──
        tk.Button(
            self,
            text="RESET COUNTER",
            font=("Courier New", 8),
            fg=MUTED, bg=BG, activebackground=DIM, activeforeground=TEXT,
            bd=0, pady=4, cursor="hand2",
            command=self._reset_counter,
        ).pack(pady=(12, 0))

        # ── footer ──
        tk.Frame(self, bg=BG).pack(expand=True)
        tk.Label(self, text="SendInput · Windows API · no admin required",
                 font=("Courier New", 7), fg=MUTED, bg=BG).pack(pady=(0, 12))

    # ── logic ─────────────────────────────────────────────────────────────────

    def _toggle(self):
        if self.clicker.running:
            self.clicker.stop_clicking()
        else:
            self.clicker.start_clicking()
        self._refresh_btn()

    def _refresh_btn(self):
        if self.clicker.running:
            self._btn.config(text="■  STOP CLICKING", bg=RED, activebackground=RED2)
            self._status_frame.config(bg=ACCENT)
        else:
            self._btn.config(text="▶  START CLICKING", bg=ACCENT, activebackground=ACCENT2)
            self._status_frame.config(bg=DIM)

    def _reset_counter(self):
        with self.clicker._lock:
            self.clicker.total = 0
            self.clicker.cps   = 0.0

    def _tick(self):
        """Refresh stats display every 100 ms."""
        with self.clicker._lock:
            cps   = self.clicker.cps
            total = self.clicker.total

        self._cps_var.set(f"{cps:,.0f}")
        self._total_var.set(f"{total:,}")
        self._refresh_btn()
        self.after(100, self._tick)

    def _poll_hotkeys(self):
        """Poll F6/F7 every 15 ms — rising-edge detection."""
        f6 = bool(user32.GetAsyncKeyState(VK_F6) & 0x8000)
        f7 = bool(user32.GetAsyncKeyState(VK_F7) & 0x8000)

        if f6 and not self._hotkey_prev_f6:
            self._toggle()
        if f7 and not self._hotkey_prev_f7:
            self._quit()

        self._hotkey_prev_f6 = f6
        self._hotkey_prev_f7 = f7
        self.after(15, self._poll_hotkeys)

    def _quit(self):
        self.clicker.shutdown()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()