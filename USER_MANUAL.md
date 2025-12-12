Seven Segment Calculator — User Manual
=====================================

Overview
--------
Seven Segment Calculator is a compact, single-file Python/Tkinter desktop calculator that uses polygon-based seven-segment style digits, mechanical click sounds, and a small preferences dialog. This manual explains installation, usage, preferences, packaging and where to find support.

Contents
- Installation (Windows EXE)
- Running the application
- Using the calculator (buttons, keyboard)
- Preferences
- History
- Packaging & distribution (PyInstaller)
- Troubleshooting

Installation (Windows EXE)
--------------------------
If you have the EXE (recommended):
1. Download `calculator.exe` (for example from the `dist` folder or the GitHub Release).
2. Place it in a folder you prefer and run it (double-click). No Python install is required.

Running from source (developer)
--------------------------------
Requirements: Python 3.10+ and optional Pillow for keycap images. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python calculator.py
```

Usage
-----
- Buttons: Click on-screen buttons for digits, operators, percent, backspace and evaluate (`=`).
- Keyboard: The app listens for normal numeric and operator keys and maps them to calculator buttons. Press Enter to evaluate and Backspace to delete.
- Decimal entry: The calculator prevents entering more than one decimal point in a single number token.
- Sign toggle: Use `+/-` to toggle the sign of the current numeric token (works as a unary toggle; does not alter earlier operators).
- Memory: `MC`, `M+`, `M-`, `MR` implement simple memory clear/add/subtract/recall.

Display behavior
----------------
- The seven-segment display shows only the current numeric token (the number you are actively editing), preserving a leading unary minus.
- Evaluation results are trimmed to remove trailing `.0` for integral floats and otherwise formatted with up to 12 significant digits to avoid float noise.

Preferences
-----------
Open `Settings -> Preferences...` to change:
- Number of display digits (4–12).
- Segment On color, Segment Off color, Decimal point color: there are presets and you can paste a hex value (e.g. `#6ef06e`).
- Click sound: choose between `Thock`, `Balanced`, and `Snap`. The application generates WAV variants automatically and persists your selection to `~/.calculator_prefs.json`.
- Restore Defaults: Preferences includes a button to restore the original color defaults.

History
-------
- A top-level `History` menu toggles a history panel showing recent evaluated expressions and results. Double-click an entry to restore the expression to the input state.

Packaging & Distribution
------------------------
- A PyInstaller-friendly `resource_path()` helper is included in the code so that assets (click WAVs) are found when running a `--onefile` EXE.
- To build an EXE using PyInstaller (Windows PowerShell):

```powershell
pyinstaller --onefile --windowed --add-data "click_snap.wav;." --add-data "click_thock.wav;." --add-data "click_balanced.wav;." calculator.py
```

Troubleshooting
---------------
- If the app crashes with a missing display attribute, ensure `calculator.py` is the latest version – the application constructs the display early in `__init__` to avoid that error.
- If audio does not sound: Windows `winsound` is used for playback. Ensure audio device is usable and that antivirus is not blocking the EXE.
- If the EXE is not running on another machine, check Windows Defender/AV blocking for unsigned executables. Use a zip or GitHub Release link if mail attachments get blocked.

Support & Source
----------------
- Source code and packaging instructions are included in this repository. If you want me to create a GitHub Release with the EXE attached, I can add that workflow.

License
-------
- Add a LICENSE file appropriate to your intent before distributing broadly.
