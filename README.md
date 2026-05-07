# ⚡ FastAutoClicker

A high-performance Windows autoclicker built with Python. Uses direct Windows API calls via `ctypes` to achieve **1,000–3,000+ clicks per second** — no third-party clicking libraries required.

---

## 📋 Requirements

- Windows 10 / 11
- Python 3.6+
- No admin rights required

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install pyinstaller
```

### 2. Run directly with Python

```bash
python autoclicker_gui.py
```

### 3. Or build a standalone `.exe`

Double-click `build.bat` — the finished executable will be at:

```
dist\AutoClicker.exe
```

No Python installation needed to run the `.exe`.

---

## 🖥️ GUI Overview

| Element | Description |
|---|---|
| **CPS display** | Live clicks-per-second readout, updates 10× per second |
| **Total clicks** | Running total since last reset |
| **START / STOP button** | Toggles clicking on/off — turns red while active |
| **Reset Counter** | Resets the total click counter to zero |
| **Status bar** | Green = running, grey = stopped |

---

## ⌨️ Hotkeys

| Key | Action |
|---|---|
| `F6` | Start / Stop clicking |
| `F7` | Quit the application |

Hotkeys work **globally** — even when the AutoClicker window is not focused.

---

## 📁 Project Files

```
autoclicker_gui.py   # Main application (GUI + click engine)
package.bat            # One-click build script → dist\AutoClicker.exe
README.md            # This file
```

---

## ⚙️ How It Works

- Calls `SendInput` directly via the Windows API — the lowest-overhead clicking method available without a kernel driver
- Mouse down + up are sent in a **single `SendInput(2, ...)` call** (one syscall per click)
- Input structs are **pre-allocated at startup** and reused every iteration — zero allocation overhead in the hot loop
- The click engine runs on a **dedicated thread**, keeping the GUI fully responsive

---

## 🔨 Building the Exe

`build.bat` runs the following command:

```bash
python -m PyInstaller autoclicker_gui.py --onefile --noconsole --name AutoClicker --clean
```

| Flag | Effect |
|---|---|
| `--onefile` | Bundles everything into a single portable `.exe` |
| `--noconsole` | No terminal window appears when launched |
| `--clean` | Clears PyInstaller cache before building |

Build output is in the `dist\` folder. The `build\` folder and `AutoClicker.spec` file are intermediates and can be deleted after building.

---

## ⚠️ Notes

- The AutoClicker window stays **always on top** so it remains visible while clicking in other applications.
- Actual CPS depends on your CPU speed and Windows scheduler — typical range is 1,000–3,000 clicks/sec.
- Some anti-cheat systems may detect high-frequency `SendInput` calls. Use responsibly.