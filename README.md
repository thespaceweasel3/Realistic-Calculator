# Seven-Segment Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

Small Tkinter calculator that renders digits in a seven-segment style on a Canvas to resemble a real calculator display.

Requirements
- Python 3.7+ (Tkinter included in standard library)

Run
```
python calculator.py
```

Usage
- Click buttons or use keyboard to type digits and operators.
- Supported: + - * / ( ) . %, clear (C), backspace, +/- toggle, and equals (= or Enter).

Notes
- The app draws its own seven-segment style digits; no external fonts required.
- The expression is evaluated using Python's eval in a restricted namespace; only digits, operators and parentheses are allowed.
