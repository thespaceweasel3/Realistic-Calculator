"""Seven-segment calculator — Option B UI.

Authentic seven-segment polygons, improved layout and keyboard support.
"""
from __future__ import annotations

import json
import math
import os
import time
import wave
import struct
import random
try:
    import winsound
except Exception:
    winsound = None

# optional Pillow for rasterizing keycap art and generating PNG keycaps
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except Exception:
    Image = ImageDraw = ImageFont = ImageTk = None
import tkinter as tk
from tkinter import ttk, messagebox
import sys

PREFS_PATH = os.path.join(os.path.expanduser("~"), ".calculator_prefs.json")


def resource_path(fname: str = '') -> str:
    """Return an absolute path to a resource, supporting PyInstaller onefile (_MEIPASS).

    If `fname` is empty this returns the resource directory. When running as a
    PyInstaller onefile bundle the runtime extracts files to `sys._MEIPASS`.
    """
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    if fname:
        return os.path.join(base, fname)
    return base

# Segment patterns for 7-seg display: a,b,c,d,e,f,g (g is middle), where 1=on
SEGMENTS = {
    '0': (1,1,1,1,1,1,0), '1': (0,1,1,0,0,0,0), '2': (1,1,0,1,1,0,1),
    '3': (1,1,1,1,0,0,1), '4': (0,1,1,0,0,1,1), '5': (1,0,1,1,0,1,1),
    '6': (1,0,1,1,1,1,1), '7': (1,1,1,0,0,0,0), '8': (1,1,1,1,1,1,1),
    '9': (1,1,1,1,0,1,1), '-': (0,0,0,0,0,0,1), ' ': (0,0,0,0,0,0,0)
}


class SevenSegment(tk.Canvas):
    """Polygon-based seven-segment display that scales to available width."""

    def __init__(self, master, digits=10, seg_len=24, seg_thick=6, pad=6, on='#6ef06e', off='#022202', dp='#ffcc00', **kw):
        super().__init__(master, highlightthickness=0, bg='#001100', **kw)
        self.digits = digits
        self.s = seg_len
        self.t = seg_thick
        self.pad = pad
        self.on = on
        self.off = off
        self.dp_color = dp
        self.slots = []  # list of (segments_ids, dp_id)
        self._last_text = ''
        self._create_geometry()
        self.bind('<Configure>', lambda e: self._apply_resize())

    def _create_geometry(self):
        # compute canvas size based on per-digit slot
        w = (self.s + self.t*2 + self.pad) * self.digits + self.pad
        h = self.s*2 + self.t*3 + self.pad*2
        self.config(width=w, height=h)
        self._create_slots()
        # restore the last text after recreating geometry so digits persist
        if getattr(self, '_last_text', None):
            try:
                self.set_text(self._last_text)
            except Exception:
                pass

    def _create_slots(self):
        self.delete('all')
        self.slots.clear()
        x = self.pad
        for _ in range(self.digits):
            seg_ids = []
            s, t = self.s, self.t
            # top horizontal (a)
            a = self.create_polygon(x+t, self.pad, x+t+s, self.pad, x+t+s-t, self.pad+t, x+t+t, self.pad+t, fill=self.off, outline=self.off)
            # top-right vertical (b)
            b = self.create_polygon(x+t+s, self.pad, x+t+s+t, self.pad+t, x+t+s+t, self.pad+t+s, x+t+s, self.pad+t+s-t, fill=self.off, outline=self.off)
            # bottom-right vertical (c)
            c = self.create_polygon(x+t+s, self.pad+t+s, x+t+s+t, self.pad+t+s+t, x+t+s+t, self.pad+t+s+t+s, x+t+s, self.pad+t+s+t+s-t, fill=self.off, outline=self.off)
            # bottom horizontal (d)
            d = self.create_polygon(x+t, self.pad+t+s+t+s, x+t+s, self.pad+t+s+t+s, x+t+s-t, self.pad+t+s+t+s-t, x+t+t, self.pad+t+s+t+s-t, fill=self.off, outline=self.off)
            # bottom-left vertical (e)
            e = self.create_polygon(x, self.pad+t+s, x+t, self.pad+t+s+t, x+t, self.pad+t+s+t+s-t, x, self.pad+t+s+t+s-t, fill=self.off, outline=self.off)
            # top-left vertical (f)
            f = self.create_polygon(x, self.pad, x+t, self.pad+t, x+t, self.pad+t+s-t, x, self.pad+t+s, fill=self.off, outline=self.off)
            # middle horizontal (g)
            g = self.create_polygon(x+t+t, self.pad+t+s, x+t+s-t, self.pad+t+s, x+t+s-t-t, self.pad+t+s+t, x+t+t+t, self.pad+t+s+t, fill=self.off, outline=self.off)
            # decimal point
            dp_r = max(2, t//1 + 2)
            dp_x = x+t+s+t
            dp_y = self.pad+t+s+t+s - dp_r*2
            dp = self.create_oval(dp_x, dp_y, dp_x+dp_r*2, dp_y+dp_r*2, fill=self.off, outline=self.off)
            seg_ids.extend([a,b,c,d,e,f,g])
            self.slots.append((seg_ids, dp))
            x += self.s + self.t*2 + self.pad

    def _apply_resize(self):
        # adjust geometry to widget width
        try:
            w = int(self.winfo_width())
        except Exception:
            return
        min_total = (self.digits * 10) + (self.pad * (self.digits + 1))
        if not w or w < min_total:
            return
        total_pad = (self.digits + 1) * self.pad
        usable = max(20, w - total_pad)
        per_digit = usable / max(1, self.digits)
        new_t = max(3, int(per_digit * 0.12))
        new_s = max(8, int(per_digit - new_t * 2 - 2))
        if abs(new_s - self.s) < 2 and abs(new_t - self.t) < 1:
            return
        self.s = new_s
        self.t = new_t
        self._create_geometry()
        # ensure displayed text is reapplied after resize
        try:
            if getattr(self, '_last_text', None) is not None:
                self.set_text(self._last_text)
        except Exception:
            pass

    def set_text(self, text: str) -> None:
        text = str(text)
        self._last_text = text
        # split into characters respecting decimal points
        chars = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == '.':
                if chars:
                    chars[-1] += '.'
                else:
                    chars.append('.')
                i += 1
                continue
            chars.append(ch)
            i += 1
        if len(chars) > self.digits:
            # keep the most-significant characters (left side) instead of the tail
            chars = chars[:self.digits]
        else:
            chars = [' ']*(self.digits-len(chars)) + chars
        for idx, ch in enumerate(chars):
            segs, dp = self.slots[idx]
            has_dp = ch.endswith('.')
            base = ch[0] if ch else ' '
            pattern = SEGMENTS.get(base, SEGMENTS[' '])
            for seg_id, on in zip(segs, pattern):
                color = self.on if on else self.off
                try:
                    self.itemconfig(seg_id, fill=color, outline=color)
                except Exception:
                    pass
            dp_color = self.dp_color if has_dp else self.off
            try:
                self.itemconfig(dp, fill=dp_color, outline=dp_color)
            except Exception:
                pass


class Calculator(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Calculator')
        # reasonable min height so display and buttons don't overlap; adjust slightly
        # set to 560 as requested
        self.minsize(420, 554)
        # prevent maximizing the window
        try:
            self.resizable(False, False)
        except Exception:
            pass
        # style
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Calc.TButton', font=('Segoe UI', 11, 'bold'), padding=(6,4), background='#2b2b2b', foreground='#fff')
        style.configure('CalcPressed.TButton', font=('Segoe UI', 11, 'bold'), padding=(4,2), background='#444', foreground='#fff')
        # keycap color palette for mechanical look
        KEYCAP_TOP = '#3f3f3f'
        KEYCAP_INNER = '#2f2f2f'
        KEYCAP_SHADOW = '#070707'
        KEYCAP_HOVER = '#515151'
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'))
        # state
        self.current = ''
        self.last_eval = False
        self.memory = 0.0
        # prefs
        self.pref_on = '#6ef06e'
        self.pref_off = '#022202'
        self.pref_dp = '#ffcc00'
        self._prefs_path = PREFS_PATH

        # main layout: display top, grid left, history right
        main = ttk.Frame(self)
        # remember display parent so we always recreate the display in the same place
        self._display_parent = main
        main.pack(fill='both', expand=True, padx=8, pady=8)

        # Display holder draws an angled, raised background beneath the display
        display_holder = tk.Frame(main, bg='#0b0b0b')
        display_holder.pack(fill='x', pady=(4,8))
        # remember display parent so prefs recreate the display in the same holder
        self._display_parent = display_holder

        # background canvas that draws a skewed/trapezoid panel to simulate angled raised display
        disp_h = 92
        disp_bg = tk.Canvas(display_holder, height=disp_h, bg=display_holder['bg'], highlightthickness=0)
        disp_bg.pack(fill='x', expand=True)

        def _draw_display_bg(event=None):
            w = disp_bg.winfo_width() or 420
            h = disp_h
            disp_bg.delete('all')
            skew = max(6, int(w * 0.02))
            # trapezoid points (slightly narrower at the top to imply perspective)
            pts = (skew, 8, w - skew, 8, w - 8, h - 12, 8, h - 12)
            disp_bg.create_polygon(pts, fill='#141414', outline='#000000')
            # subtle top highlight
            disp_bg.create_line(skew + 8, 10, w - skew - 8, 10, fill='#2a2a2a', width=2)

        disp_bg.bind('<Configure>', _draw_display_bg)

        # create the seven-segment display so `self.display` always exists
        try:
            # default to 12 digits; prefs will recreate this later if necessary
            self.display = SevenSegment(display_holder, digits=12, on=self.pref_on, off=self.pref_off, dp=self.pref_dp)
            try:
                self.display.place(relx=0.5, y=10, anchor='n', relwidth=0.98)
            except Exception:
                self.display.pack(fill='x', pady=(4,8))
        except Exception:
            # if creation fails, leave callers to handle absence
            pass

        # try to create and set a small calculator-style window icon
        try:
            icon = self._make_window_icon()
            try:
                self.iconphoto(False, icon)
                self._icon_image = icon  # keep reference
            except Exception:
                pass
        except Exception:
            pass

        # ensure the display sits visually above the angled panel
        try:
            self.display.lift()
        except Exception:
            pass

        content = ttk.Frame(main)
        content.pack(fill='both', expand=True)

        # Ensure the seven-seg display stays above other widgets when window resizes
        try:
            def _on_configure(event=None):
                disp = getattr(self, 'display', None)
                if not disp:
                    return
                try:
                    disp.lift()
                except Exception:
                    # swallow intermittent errors during startup/resizing
                    return

            self.bind('<Configure>', _on_configure)
        except Exception:
            pass

        grid_frame = ttk.Frame(content)
        grid_frame.pack(side='left', fill='both', expand=True)

        # prepare keycap images early so buttons can use them when created
        try:
            self._prepare_keycap_images()
        except Exception:
            pass

        # history storage (UI removed for now) -- keep a listbox object in memory so history functions work
        self.hist_visible = False
        # create a hidden history frame that can be packed from the menu
        self.hist_frame = ttk.Frame(content)
        # create a non-packed listbox to hold history entries (not shown)
        self.hist_list = tk.Listbox(self.hist_frame, width=1, height=12, activestyle='none')
        # keep bindings in case user opens history via shortcuts later
        try:
            self.hist_list.bind('<Motion>', self._on_hist_motion)
            self.hist_list.bind('<Leave>', lambda e: self.hist_list.selection_clear(0, 'end'))
            self.hist_list.bind('<Double-Button-1>', self._on_history_double)
        except Exception:
            pass

        # buttons (larger)
        buttons = [
            ('MC', self._mem_clear), ('M+', self._mem_add), ('M-', self._mem_sub), ('MR', self._mem_recall),
            ('C', self._clear), ('+/-', self._negate), ('%', self._percent), ('←', self._backspace),
            ('7', lambda: self._append('7')), ('8', lambda: self._append('8')), ('9', lambda: self._append('9')), ('/', lambda: self._append('/')),
            ('4', lambda: self._append('4')), ('5', lambda: self._append('5')), ('6', lambda: self._append('6')), ('*', lambda: self._append('*')),
            ('1', lambda: self._append('1')), ('2', lambda: self._append('2')), ('3', lambda: self._append('3')), ('-', lambda: self._append('-')),
            ('0', lambda: self._append('0')), ('.', lambda: self._append('.')), ('=', self._evaluate), ('+', lambda: self._append('+')),
        ]

        r = 0
        c = 0
        for label, cmd in buttons:
            # nested frames to produce a raised 3D effect: outer (shadow) + inner (highlight)
            # flat key style: collapse outer shadow into same top color to remove grey edge
            outer_bg = KEYCAP_TOP
            inner_bg = KEYCAP_TOP
            bf_outer = tk.Frame(grid_frame, bg=outer_bg, highlightthickness=0)
            bf_outer.grid(row=r, column=c, padx=0, pady=0, sticky='nsew')
            # inner frame provides a subtle inset; keep padding minimal for a flat look
            bf_inner = tk.Frame(bf_outer, bg=inner_bg, highlightthickness=0)
            bf_inner.pack(fill='both', expand=True, padx=0, pady=0)
            # the ttk.Button is the keycap top; if keycap image exists use it
            img = None
            try:
                img = getattr(self, 'keycap_images', {}).get(label)
            except Exception:
                img = None
            # Use a flat, borderless tk.Button so there's no white border from the native ttk
            btn_font = ('Segoe UI', 11, 'bold')
            if img:
                b = tk.Button(
                    bf_inner, image=img, command=cmd,
                    bd=0, highlightthickness=0, relief='flat',
                    bg=inner_bg, activebackground=KEYCAP_HOVER,
                    fg='#ffffff', activeforeground='#ffffff',
                    font=btn_font, takefocus=False, compound='center'
                )
            else:
                b = tk.Button(
                    bf_inner, text=label, command=cmd,
                    bd=0, highlightthickness=0, relief='flat',
                    bg=inner_bg, activebackground=KEYCAP_HOVER,
                    fg='#ffffff', activeforeground='#ffffff',
                    font=btn_font, takefocus=False
                )
            # replace raw command with a debounced safe invoker to prevent double-activation
            try:
                # store last click timestamps dict on self
                if not hasattr(self, '_last_click_times'):
                    self._last_click_times = {}
                # wrap the original command so rapid repeated clicks are ignored
                def _make_cmd(fn, lbl, widget):
                    return lambda f=fn, L=lbl, w=widget: self._safe_invoke(f, L, w)
                b.config(command=_make_cmd(cmd, label, b))
            except Exception:
                # if wrapping fails, leave the original command
                pass
            # reduce extra padding so label/image sits centered in the lighter rectangle
            b.pack(fill='both', expand=True, padx=0, pady=2)
            # store reference for keyboard-triggered flashes and animations
            if not hasattr(self, 'buttons'):
                self.buttons = {}
            self.buttons[label] = b
            # press/release handlers (swap style and change frame bg for 3D sink)
            b.bind('<ButtonPress-1>', lambda e, btn=b: self._on_button_press(btn))
            b.bind('<ButtonRelease-1>', lambda e, btn=b: self._on_button_release(btn))
            # hover to slightly brighten the keycap top
            b.bind('<Enter>', lambda e, btn=b: self._on_button_hover(btn, True))
            b.bind('<Leave>', lambda e, btn=b: self._on_button_hover(btn, False))
            c += 1
            if c > 3:
                c = 0
                r += 1

        for i in range(4):
            grid_frame.columnconfigure(i, weight=1)

        # menu
        menubar = tk.Menu(self)
        settings = tk.Menu(menubar, tearoff=0)
        settings.add_command(label='Preferences...', command=self.open_prefs)
        menubar.add_cascade(label='Settings', menu=settings)
        # view menu: history toggle
        view = tk.Menu(menubar, tearoff=0)
        view.add_command(label='Toggle History', accelerator='Ctrl+H', command=self._toggle_history)
        menubar.add_cascade(label='View', menu=view)
        # put History as the right-most top-level command by adding it last
        menubar.add_command(label='History', command=self._toggle_history)
        self.config(menu=menubar)

        # bindings
        self.bind_all('<Key>', self._on_key)
        # keyboard shortcuts
        self.bind_all('<Control-m>', lambda e: (self._flash_button_for_label('MR'), self._mem_recall()))
        self.bind_all('<Control-h>', lambda e: self._toggle_history())
        self._load_prefs()
        # prepare click sound (written next to this script)
        try:
            self._ensure_click_sound()
        except Exception:
            pass
        self._update_display('0')

    def _update_display(self, text: str) -> None:
        # Show only the current numeric token (the part after the last binary operator).
        # Preserve a leading unary minus (e.g. '-5') and ignore exponent signs (e.g. '1e-3').
        try:
            expr = text or ''
            # find the last binary operator position (not a leading unary sign or exponent sign)
            last_op = -1
            i = len(expr) - 1
            while i >= 0:
                ch = expr[i]
                if ch in '+-*/':
                    # skip signs that are part of exponent (e.g. '1e-3')
                    if ch in '+-' and i > 0 and expr[i-1] in 'eE':
                        i -= 1
                        continue
                    # skip leading unary sign at position 0
                    if i == 0:
                        i -= 1
                        continue
                    last_op = i
                    break
                i -= 1
            token = expr[last_op+1:] if last_op != -1 else expr
            # if token is empty, show 0; otherwise preserve token (including leading '-')
            self.display.set_text(token or '0')
        except Exception:
            try:
                self.display.set_text(text)
            except Exception:
                pass

    def _append(self, ch: str) -> None:
        # Operator handling: when an operator is pressed, append or replace
        if ch in '+-*/':
            if not self.current:
                # allow unary minus to start a negative number
                if ch == '-':
                    self.current = '-'
                    self._update_display(self.current)
                return
            # replace trailing operator if present
            if self.current[-1] in '+-*/':
                self.current = self.current[:-1] + ch
            else:
                self.current += ch
            self.last_eval = False
            # clear the visible numeric token so user sees an empty entry for the next operand
            self._update_display('')
            return

        # If the last action produced a result, start a new number on digit
        if self.last_eval:
            if ch.isdigit():
                self.current = ch
            elif ch == '.':
                # user typed decimal after an evaluation -> start '0.'
                self.current = '0.'
                self.last_eval = False
                self._update_display(self.current)
                return
            else:
                # other characters start from empty
                self.current = ''

        # Prevent entering more than one decimal point in the current numeric token
        if ch == '.':
            token = self.current
            # find last operator to determine current numeric token
            idxs = [token.rfind(op) for op in ('+', '-', '*', '/')] if token else [-1]
            split_idx = max(idxs)
            last_tok = token[split_idx+1:] if split_idx != -1 else token
            if '.' in last_tok:
                # already has a decimal point -> ignore
                return
            # if starting a new token or token is just a lone '-', prepend 0
            if last_tok == '' or last_tok == '-':
                self.current += '0.'
                self.last_eval = False
                self._update_display(self.current)
                return

        self.current += ch
        self.last_eval = False
        self._update_display(self.current or '0')

    def _clear(self) -> None:
        self.current = ''
        self._update_display('0')

    def _backspace(self) -> None:
        self.current = self.current[:-1]
        self._update_display(self.current or '0')

    def _negate(self) -> None:
        # Toggle the sign of the current numeric token (the substring after the last operator).
        s = self.current or ''
        # find split point: last operator that is not part of an exponent sign
        def _split_prefix_token(expr: str) -> tuple[str, str]:
            if not expr:
                return ('', '')
            i = len(expr) - 1
            while i >= 0:
                ch = expr[i]
                if ch in '+-*/':
                    # skip if this '+'/'-' is an exponent sign (e.g., '1e-3')
                    if ch in '+-' and i > 0 and expr[i-1] in 'eE':
                        i -= 1
                        continue
                    return (expr[:i+1], expr[i+1:])
                i -= 1
            return ('', expr)

        prefix, token = _split_prefix_token(s)
        if token.startswith('-'):
            token = token[1:]
        else:
            # if token is empty, start a negative token
            if token == '':
                token = '-'
            else:
                token = '-' + token
        self.current = prefix + token
        # display only the current token so the user sees the sign change immediately
        self._update_display(token or '0')

    def _percent(self) -> None:
        try:
            v = float(self.current or '0') / 100.0
            self.current = str(v)
            self._update_display(self.current)
        except Exception:
            messagebox.showerror('Error', 'Invalid percent')

    def _evaluate(self) -> None:
        expr = (self.current or '').strip()
        if not expr:
            return
        allowed = set('0123456789.+-*/() %eE')
        if any(ch not in allowed for ch in expr):
            messagebox.showerror('Error', 'Invalid characters in expression')
            return
        try:
            result = eval(expr, {'__builtins__': {}}, {})
            if isinstance(result, float) and (math.isinf(result) or math.isnan(result)):
                raise ValueError('Invalid numeric result')
            # Format the result for display/history:
            # - If a float is mathematically integral, show as an integer (no trailing .0)
            # - Otherwise show a compact representation to avoid long floating-point artifacts
            if isinstance(result, float):
                if float(result).is_integer():
                    result_str = str(int(result))
                else:
                    # limit to 12 significant digits to avoid long tails
                    result_str = f"{result:.12g}"
            else:
                result_str = str(result)
            entry = f"{expr} = {result_str}"
            self.hist_list.insert(0, entry)
            self.current = result_str
            self.last_eval = True
            self._update_display(self.current)
        except Exception:
            messagebox.showerror('Error', 'Failed to evaluate expression')

    # memory
    def _mem_clear(self) -> None:
        self.memory = 0.0

    def _mem_add(self) -> None:
        try:
            self.memory += float(self.current or '0')
        except Exception:
            pass

    def _mem_sub(self) -> None:
        try:
            self.memory -= float(self.current or '0')
        except Exception:
            pass

    def _mem_recall(self) -> None:
        self.current = str(self.memory)
        self._update_display(self.current)

    def _on_history_double(self, event=None) -> None:
        sel = self.hist_list.curselection()
        if not sel:
            return
        text = self.hist_list.get(sel[0])
        if ' = ' in text:
            expr, _ = text.split(' = ', 1)
            self.current = expr
            self._update_display(self.current)

    def _on_hist_motion(self, event) -> None:
        try:
            idx = self.hist_list.nearest(event.y)
            if idx is not None:
                self.hist_list.selection_clear(0, 'end')
                self.hist_list.selection_set(idx)
                self.hist_list.activate(idx)
        except Exception:
            pass

    def _save_prefs(self, extra: dict | None = None) -> None:
        try:
            prefs = {}
            if os.path.exists(self._prefs_path):
                with open(self._prefs_path, 'r', encoding='utf-8') as fh:
                    prefs = json.load(fh)
            if extra:
                prefs.update(extra)
            with open(self._prefs_path, 'w', encoding='utf-8') as fh:
                json.dump(prefs, fh)
        except Exception:
            pass

    def _prepare_keycap_images(self) -> None:
        """Generate or load PNG keycap images for all keypad labels and store PhotoImage objects.
        Requires Pillow. If Pillow isn't available this is a no-op.
        """
        if Image is None or ImageDraw is None or ImageTk is None:
            return
        # labels used on the keypad in the same order as `buttons` definition
        labels = ['MC','M+','M-','MR','C','+/-','%','←',
                  '7','8','9','/','4','5','6','*','1','2','3','-','0','.','=','+']
        # write keycaps and log to a user-accessible folder (under the home directory)
        base = os.path.join(os.path.expanduser('~'), 'keycaps')
        os.makedirs(base, exist_ok=True)
        log_path = os.path.join(base, 'generator.log')
        # also write a copy into the workspace for the assistant to read
        workspace_log = os.path.join('C:\\workspace', 'keycaps_generator.log')
        def log(msg: str) -> None:
            try:
                with open(log_path, 'a', encoding='utf-8') as lf:
                    lf.write(msg + '\n')
            except Exception:
                pass
            try:
                with open(workspace_log, 'a', encoding='utf-8') as wf:
                    wf.write(msg + '\n')
            except Exception:
                pass
        log(f'[keycap] base dir: {base}')
        self.keycap_images = {}
        # choose sizes
        img_w = 88
        img_h = 64
        try:
            # try to get a TTF font; fallback to default if not found
            font = ImageFont.truetype('seguisb.ttf', 32)
        except Exception:
            try:
                font = ImageFont.truetype('arial.ttf', 32)
            except Exception:
                font = ImageFont.load_default()

        for lbl in labels:
            # create an image for this label
            # sanitize label for filename (replace or name-map unsafe characters)
            safe_map = {
                '+/-': 'plusminus', '/': 'slash', '*': 'star', '\\': 'backslash',
                '←': 'back', '.': 'dot', '+': 'plus', '-': 'minus', '%': 'percent',
                '=': 'equals'
            }
            safe_lbl = safe_map.get(lbl, None)
            if safe_lbl is None:
                # fallback: keep alphanumerics, replace others with underscore
                import re
                safe_lbl = re.sub(r'[^A-Za-z0-9]+', '_', lbl)
                if not safe_lbl:
                    safe_lbl = 'key'
            fn = os.path.join(base, f'keycap_{safe_lbl}.png')
            # Always (re)create and overwrite the keycap PNG so deleted files are regenerated.
            # create a flat/vector-style keycap (like the provided illustration):
            # - transparent outer margin
            # - dark rounded outer cap
            # - slightly lighter inner panel (the visible top surface)
            # - bold white label near the top-middle
            img = Image.new('RGBA', (img_w, img_h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            # palette for vector style
            outer = (20, 20, 20, 255)      # outer rounded cap (very dark)
            inner = (56, 56, 56, 255)      # inner top panel (slightly lighter)
            corner_radius = 12
            # inset so the outer pixels are transparent (rounded outer margin)
            inset = 6
            left = inset
            top = inset
            right = img_w - inset
            bottom = img_h - inset
            # draw outer rounded cap (rim)
            draw.rounded_rectangle((left, top, right, bottom), radius=corner_radius, fill=outer)
            # draw inner panel inset a bit to form the lighter top surface
            panel_inset = 6
            pleft = left + panel_inset
            ptop = top + panel_inset
            pright = right - panel_inset
            pbottom = bottom - panel_inset
            draw.rounded_rectangle((pleft, ptop, pright, pbottom), radius=max(4, corner_radius-4), fill=inner)
            # optional accent: make 'C' key orange like the sample
            accent_orange = (245, 140, 30, 255)
            accent_labels = {'C'}
            if lbl in accent_labels:
                draw.rounded_rectangle((pleft, ptop, pright, pbottom), radius=max(4, corner_radius-4), fill=accent_orange)
            # label: bold, white, centered horizontally and placed near top of inner panel
            txt = lbl
            try:
                base_path = getattr(font, 'path', None)
            except Exception:
                base_path = None
            # pick size: larger for single-char keys
            if len(lbl) == 1:
                try:
                    if base_path:
                        f = ImageFont.truetype(base_path, 34)
                    else:
                        f = ImageFont.truetype('arial.ttf', 34)
                except Exception:
                    f = font
            else:
                try:
                    if base_path:
                        f = ImageFont.truetype(base_path, 20)
                    else:
                        f = ImageFont.truetype('arial.ttf', 20)
                except Exception:
                    f = font
            try:
                w, h = f.getsize(txt)
            except Exception:
                try:
                    w, h = draw.textsize(txt, font=f)
                except Exception:
                    w, h = (28, 18)
            text_x = (img_w - w) / 2
            # place label near top of inner panel (top-centered)
            text_y = ptop + 2
            draw.text((text_x, text_y), txt, font=f, fill=(250,250,250,255))
            try:
                img.save(fn)
                log(f'[keycap] saved: {fn}')
            except Exception as e:
                import traceback
                log(f'[keycap] failed save: {fn} -> {e}')
                log(traceback.format_exc())
                try:
                    img.save(fn)
                    log(f'[keycap] saved: {fn}')
                except Exception as e:
                    import traceback
                    log(f'[keycap] failed save: {fn} -> {e}')
                    log(traceback.format_exc())
            # load into PhotoImage
            try:
                pil = Image.open(fn)
                tkimg = ImageTk.PhotoImage(pil)
                self.keycap_images[lbl] = tkimg
            except Exception as e:
                import traceback
                log(f'[keycap] failed load: {fn} -> {e}')
                log(traceback.format_exc())
                # skip loading if something failed
                pass
        log('[keycap] generation complete')


    def _on_key(self, event) -> None:
        if event.keysym in ('Return', 'KP_Enter'):
            # animate '=' button then evaluate
            self._flash_button_for_label('=')
            self._evaluate(); return
        if event.keysym == 'BackSpace':
            self._flash_button_for_label('←')
            self._backspace(); return
        if event.keysym == 'Escape':
            self._flash_button_for_label('C')
            self._clear(); return
        ch = event.char
        if ch and ch in '0123456789.+-*/()':
            # trigger visual flash for the corresponding button
            self._flash_button_for_label(ch)
            self._append(ch)

    def open_prefs(self) -> None:
        dlg = tk.Toplevel(self)
        dlg.title('Preferences')
        # apply application icon to preferences dialog if available
        try:
            if getattr(self, '_icon_image', None) is not None:
                dlg.iconphoto(False, self._icon_image)
        except Exception:
            pass
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text='Digits:').grid(row=0, column=0, sticky='e', padx=6, pady=6)
        digits_var = tk.IntVar(value=self.display.digits)
        # limit allowed digits to 12 for the seven-segment display
        tk.Spinbox(dlg, from_=4, to=12, textvariable=digits_var, width=6).grid(row=0, column=1, sticky='w')

        ttk.Label(dlg, text='Segment On Color:').grid(row=1, column=0, sticky='e', padx=6, pady=6)
        on_ent = ttk.Entry(dlg)
        on_ent.insert(0, self.pref_on)
        on_ent.grid(row=1, column=1, sticky='w')
        # presets combobox for on color
        preset_colors = ['#6ef06e', '#00ff00', '#00ccff', '#ff0000', '#ffffff', '#000000', '#ffcc00', '#022202']
        on_combo = ttk.Combobox(dlg, values=preset_colors, state='readonly', width=10)
        on_combo.grid(row=1, column=2, sticky='w', padx=6)
        def _on_pick_on(event=None):
            try:
                val = on_combo.get()
                if val:
                    on_ent.delete(0, 'end')
                    on_ent.insert(0, val)
            except Exception:
                pass
        on_combo.bind('<<ComboboxSelected>>', _on_pick_on)

        ttk.Label(dlg, text='Segment Off Color:').grid(row=2, column=0, sticky='e', padx=6, pady=6)
        off_ent = ttk.Entry(dlg)
        off_ent.insert(0, self.pref_off)
        off_ent.grid(row=2, column=1, sticky='w')
        off_combo = ttk.Combobox(dlg, values=preset_colors, state='readonly', width=10)
        off_combo.grid(row=2, column=2, sticky='w', padx=6)
        def _on_pick_off(event=None):
            try:
                val = off_combo.get()
                if val:
                    off_ent.delete(0, 'end')
                    off_ent.insert(0, val)
            except Exception:
                pass
        off_combo.bind('<<ComboboxSelected>>', _on_pick_off)

        ttk.Label(dlg, text='Decimal Point Color:').grid(row=3, column=0, sticky='e', padx=6, pady=6)
        dp_ent = ttk.Entry(dlg)
        dp_ent.insert(0, self.pref_dp)
        dp_ent.grid(row=3, column=1, sticky='w')
        dp_combo = ttk.Combobox(dlg, values=preset_colors, state='readonly', width=10)
        dp_combo.grid(row=3, column=2, sticky='w', padx=6)
        def _on_pick_dp(event=None):
            try:
                val = dp_combo.get()
                if val:
                    dp_ent.delete(0, 'end')
                    dp_ent.insert(0, val)
            except Exception:
                pass
        dp_combo.bind('<<ComboboxSelected>>', _on_pick_dp)

        # Click sound variant selector
        ttk.Label(dlg, text='Click Sound:').grid(row=4, column=0, sticky='e', padx=6, pady=6)
        # determine current variant from existing click path
        cur_variant = 'Thock'
        try:
            cp = getattr(self, '_click_path', '') or ''
            if 'snap' in cp:
                cur_variant = 'Snap'
            elif 'balanced' in cp:
                cur_variant = 'Balanced'
            else:
                cur_variant = 'Thock'
        except Exception:
            cur_variant = 'Thock'
        click_var = tk.StringVar(value=cur_variant)
        click_combo = ttk.Combobox(dlg, textvariable=click_var, values=['Thock', 'Balanced', 'Snap'], state='readonly', width=10)
        click_combo.grid(row=4, column=1, sticky='w')

        def apply_prefs() -> None:
            self.pref_on = on_ent.get() or self.pref_on
            self.pref_off = off_ent.get() or self.pref_off
            self.pref_dp = dp_ent.get() or self.pref_dp
            sel_variant = click_var.get() or 'Thock'
            d = min(12, max(4, int(digits_var.get())))
            try:
                self.display.destroy()
            except Exception:
                pass
            # recreate display inside the original display parent so it remains at the top
            parent = getattr(self, '_display_parent', self)
            self.display = SevenSegment(parent, digits=d, on=self.pref_on, off=self.pref_off, dp=self.pref_dp)
            try:
                # place the display to overlay the angled panel
                self.display.place(relx=0.5, y=10, anchor='n', relwidth=0.98)
                try:
                    self.display.lift()
                except Exception:
                    pass
            except Exception:
                # fallback to pack if place fails
                self.display.pack(fill='x', pady=(4,8))
            self._update_display(self.current or '0')
            try:
                prefs = {'digits': d, 'on': self.pref_on, 'off': self.pref_off, 'dp': self.pref_dp, 'click_variant': sel_variant}
                with open(self._prefs_path, 'w', encoding='utf-8') as fh:
                    json.dump(prefs, fh)
                # update click path immediately (use resource_path so bundled exe finds files)
                try:
                    base = resource_path('')
                except Exception:
                    base = os.getcwd()
                filename = 'click_thock.wav'
                if sel_variant == 'Balanced':
                    filename = 'click_balanced.wav'
                elif sel_variant == 'Snap':
                    filename = 'click_snap.wav'
                pth = os.path.join(base, filename)
                if os.path.exists(pth):
                    self._click_path = pth
            except Exception:
                pass
            dlg.destroy()

        # Restore defaults button and Apply
        def _restore_defaults() -> None:
            try:
                DEFAULT_ON = '#6ef06e'
                DEFAULT_OFF = '#022202'
                DEFAULT_DP = '#ffcc00'
                on_ent.delete(0, 'end'); on_ent.insert(0, DEFAULT_ON)
                off_ent.delete(0, 'end'); off_ent.insert(0, DEFAULT_OFF)
                dp_ent.delete(0, 'end'); dp_ent.insert(0, DEFAULT_DP)
                # update combos to reflect restore
                try:
                    on_combo.set(DEFAULT_ON)
                    off_combo.set(DEFAULT_OFF)
                    dp_combo.set(DEFAULT_DP)
                except Exception:
                    pass
            except Exception:
                pass

        ttk.Button(dlg, text='Restore Defaults', command=_restore_defaults).grid(row=5, column=0, sticky='e', padx=6, pady=6)
        ttk.Button(dlg, text='Apply', command=apply_prefs).grid(row=5, column=1, sticky='w', padx=6, pady=6)

    # --- Button animation helpers ---
    def _hex_to_rgb(self, hx: str) -> tuple[int,int,int]:
        hx = hx.lstrip('#')
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: tuple[int,int,int]) -> str:
        return '#%02x%02x%02x' % rgb

    def _animate_button_color(self, btn: tk.Button, start: str, end: str, duration: float = 0.12) -> None:
        try:
            start_rgb = self._hex_to_rgb(start)
            end_rgb = self._hex_to_rgb(end)
        except Exception:
            return
        start_t = time.time()

        def step():
            now = time.time()
            t = (now - start_t) / duration
            if t >= 1.0:
                try:
                    btn.config(bg=end)
                except Exception:
                    pass
                return
            # ease out cubic
            eased = 1 - (1 - t) ** 3
            cur = tuple(int(round(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * eased)) for i in range(3))
            try:
                btn.config(bg=self._rgb_to_hex(cur))
            except Exception:
                pass
            self.after(16, step)

        step()

    def _on_button_press(self, btn: tk.Button) -> None:
        # swap to pressed ttk style and produce key travel by shifting cap down
        try:
            inner = btn.master  # the inner keycap frame
            outer = getattr(inner, 'master', None)
            # darken both inner and outer frames to simulate sink
            if isinstance(inner, tk.Frame):
                inner.config(bg='#2b2b2b')
                # move cap down by increasing top pady
                try:
                    inner.pack_configure(pady=(4,1))
                except Exception:
                    pass
            if isinstance(outer, tk.Frame):
                outer.config(bg='#000')
            btn.config(style='CalcPressed.TButton')
            try:
                btn.pack_configure(pady=1)
            except Exception:
                pass
        except Exception:
            pass
        # play click sound if available
        try:
            self._play_click()
        except Exception:
            pass

    def _on_button_release(self, btn: tk.Button) -> None:
        # restore normal ttk style, reset cap position
        try:
            inner = btn.master
            outer = getattr(inner, 'master', None)
            if isinstance(inner, tk.Frame):
                inner.config(bg='#3f3f3f')
                try:
                    inner.pack_configure(pady=1)
                except Exception:
                    pass
            if isinstance(outer, tk.Frame):
                outer.config(bg='#1a1a1a')
            btn.config(style='Calc.TButton')
            try:
                btn.pack_configure(pady=3)
            except Exception:
                pass
        except Exception:
            pass

    def _on_button_hover(self, btn: tk.Button, entering: bool) -> None:
        try:
            inner = btn.master
            if not isinstance(inner, tk.Frame):
                return
            if entering:
                inner.config(bg='#515151')
            else:
                inner.config(bg='#3f3f3f')
        except Exception:
            pass

    def _safe_invoke(self, func, label: str, btn: tk.Button) -> None:
        """Invoke a button command with a short debounce to avoid double activations.

        Ignores invocations that happen within 250ms of the previous click for the same label.
        Disables the button briefly (120ms) while handling to reduce duplicate events.
        """
        try:
            # global input lock: if locked, ignore further invocations
            if getattr(self, '_input_locked', False):
                return
            now = time.time()
            last = getattr(self, '_last_click_times', {}).get(label, 0)
            # increase debounce to 500ms to reduce accidental double activations
            if now - last < 0.50:
                return
            self._last_click_times[label] = now
            # set a short global input lock so keyboard shortcuts and other buttons
            # won't cause duplicate activations while this command is processed
            self._input_locked = True
        except Exception:
            pass
        try:
            try:
                btn.config(state='disabled')
            except Exception:
                pass
            func()
        finally:
            def _reenable():
                try:
                    btn.config(state='normal')
                except Exception:
                    pass
                try:
                    self._input_locked = False
                except Exception:
                    pass
            try:
                # keep the button disabled slightly longer to avoid immediate duplicate events
                # release global lock after 300ms
                self.after(300, _reenable)
            except Exception:
                _reenable()

    def _flash_button_for_label(self, label: str) -> None:
        # map input chars to button labels
        # respect global input lock
        if getattr(self, '_input_locked', False):
            return
        if not hasattr(self, 'buttons'):
            return
        lbl = label
        # normalize some keys
        if label == '\r':
            lbl = '='
        btn = self.buttons.get(lbl)
        if not btn:
            # maybe the operator is different (e.g., '*' etc.)
            btn = self.buttons.get(str(label))
        if not btn:
            return
        # perform press then release after short delay
        self._on_button_press(btn)
        self.after(120, lambda: self._on_button_release(btn))
        try:
            self._play_click()
        except Exception:
            pass

    def _load_prefs(self) -> None:
        try:
            if os.path.exists(self._prefs_path):
                with open(self._prefs_path, 'r', encoding='utf-8') as fh:
                    prefs = json.load(fh)
                d = int(prefs.get('digits', getattr(self.display, 'digits', 12)))
                self.pref_on = prefs.get('on', self.pref_on)
                self.pref_off = prefs.get('off', self.pref_off)
                self.pref_dp = prefs.get('dp', self.pref_dp)
                try:
                    self.display.destroy()
                except Exception:
                    pass
                parent = getattr(self, '_display_parent', self)
                # cap digits to 12 to match display limits
                self.display = SevenSegment(parent, digits=max(4, min(12, d)), on=self.pref_on, off=self.pref_off, dp=self.pref_dp)
                try:
                    self.display.place(relx=0.5, y=10, anchor='n', relwidth=0.98)
                    try:
                        self.display.lift()
                    except Exception:
                        pass
                except Exception:
                    self.display.pack(fill='x', pady=(4,8))
        except Exception:
            pass

    def _ensure_click_sound(self) -> None:
        """Create a short click WAV file next to the script (overwrites only if missing)."""
        # use resource_path so PyInstaller onefile bundles locate assets correctly
        try:
            base = resource_path('')
        except Exception:
            base = os.getcwd()
        # create three click variants so you can audition them: thock, balanced, snap
        variants = [
            ('click_thock.wav', dict(impulse_amp=22000.0, noise_amp=9000.0, low_amp=9000.0, low_freq=380.0, impulse_decay=12000.0, noise_decay=400.0, duration=0.055)),
            ('click_balanced.wav', dict(impulse_amp=18000.0, noise_amp=14000.0, low_amp=3000.0, low_freq=500.0, impulse_decay=8000.0, noise_decay=500.0, duration=0.045)),
            ('click_snap.wav', dict(impulse_amp=26000.0, noise_amp=18000.0, low_amp=1500.0, low_freq=700.0, impulse_decay=14000.0, noise_decay=300.0, duration=0.035)),
        ]

        def _write_variant(filename: str, params: dict) -> None:
            p = os.path.join(base, filename)
            framerate = 44100
            duration = params.get('duration', 0.045)
            n_samples = int(framerate * duration)
            frames = bytearray()
            imp_amp = params.get('impulse_amp', 18000.0)
            noise_amp = params.get('noise_amp', 12000.0)
            low_amp = params.get('low_amp', 3000.0)
            low_freq = params.get('low_freq', 500.0)
            imp_decay = params.get('impulse_decay', 8000.0)
            noise_decay = params.get('noise_decay', 500.0)
            for i in range(n_samples):
                t = i / framerate
                impulse = imp_amp * math.exp(-imp_decay * t) if i < 12 else 0.0
                noise = noise_amp * math.exp(-noise_decay * t) * (random.random() * 2 - 1)
                low = low_amp * math.exp(-60.0 * t) * math.sin(2.0 * math.pi * low_freq * t)
                sample = int(max(-32767, min(32767, impulse + noise + low)))
                frames.extend(struct.pack('<h', sample))
            try:
                with wave.open(p, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(framerate)
                    wf.writeframes(bytes(frames))
            except Exception:
                try:
                    if os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass

        try:
            for name, params in variants:
                pth = os.path.join(base, name)
                if not os.path.exists(pth):
                    _write_variant(name, params)
            # choose default based on saved prefs (if present), else thock
            click_variant = None
            try:
                if os.path.exists(self._prefs_path):
                    with open(self._prefs_path, 'r', encoding='utf-8') as fh:
                        p = json.load(fh)
                        click_variant = p.get('click_variant')
            except Exception:
                click_variant = None
            mapping = {'Thock': 'click_thock.wav', 'Balanced': 'click_balanced.wav', 'Snap': 'click_snap.wav'}
            # default to Snap when no preference exists
            filename = mapping.get(click_variant, 'click_snap.wav')
            default = os.path.join(base, filename)
            if os.path.exists(default):
                self._click_path = default
            else:
                # fallback to any existing variant
                for name, _ in variants:
                    pth = os.path.join(base, name)
                    if os.path.exists(pth):
                        self._click_path = pth
                        break
        except Exception:
            self._click_path = None

    def _make_window_icon(self) -> tk.PhotoImage:
        """Create a small runtime PhotoImage representing a calculator icon.

        The icon is constructed pixel-by-pixel so no external asset is required.
        """
        size = 64
        img = tk.PhotoImage(width=size, height=size)
        # colors
        bg = '#2b2b2b'
        body = '#111111'
        chrome = '#444444'
        key = '#d9d9d9'
        sym = '#111111'

        # fill background (transparent-looking) with bg
        for y in range(size):
            # build a row string to put for performance
            row = ' '.join([bg]*size)
            try:
                img.put('{' + row + '}', to=(0, y))
            except Exception:
                # fallback pixel-by-pixel
                for x in range(size):
                    img.put(bg, (x, y))

        # draw rounded rectangle body
        bx0, by0, bx1, by1 = 8, 8, size-9, size-9
        for y in range(by0, by1+1):
            for x in range(bx0, bx1+1):
                img.put(body, (x, y))

        # top chrome strip
        for y in range(by0, by0+8):
            for x in range(bx0+2, bx1-1):
                img.put(chrome, (x, y))

        # draw four small key squares and simple operator marks
        keys = [ (bx0+8, by0+18), (bx0+28, by0+18), (bx0+8, by0+34), (bx0+28, by0+34) ]
        ksize = 10
        for kx, ky in keys:
            for y in range(ky, ky+ksize):
                for x in range(kx, kx+ksize):
                    img.put(key, (x, y))

        # plus sign in top-left key
        px, py = keys[0]
        cx = px + ksize//2
        cy = py + ksize//2
        for d in range(-2,3):
            img.put(sym, (cx + d, cy))
            img.put(sym, (cx, cy + d))

        # minus sign in top-right key
        px, py = keys[1]
        cx = px + ksize//2
        cy = py + ksize//2
        for d in range(-2,3):
            img.put(sym, (cx + d, cy))

        # multiply (x) in bottom-left
        px, py = keys[2]
        for d in range(0, ksize):
            img.put(sym, (px + d, py + d))
            img.put(sym, (px + d, py + ksize - 1 - d))

        # divide sign in bottom-right: a dot, a line, and a dot
        px, py = keys[3]
        cx = px + ksize//2
        cy = py + ksize//2
        img.put(sym, (cx, cy - 3))
        for d in range(-2,3):
            img.put(sym, (cx + d, cy))
        img.put(sym, (cx, cy + 3))

        return img

    def _play_click(self) -> None:
        """Play the generated click sound asynchronously on Windows; noop otherwise."""
        try:
            if winsound is None:
                return
            path = getattr(self, '_click_path', None)
            if not path or not os.path.exists(path):
                return
            # Play asynchronously so GUI doesn't block
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

    # History toggle + animation
    def _toggle_history(self) -> None:
        # if history UI has been removed, do nothing
        if getattr(self, 'hist_frame', None) is None:
            return
        if getattr(self, 'hist_animating', False):
            return
        # start eased animation
        if self.hist_visible:
            self._animate_history(show=False)
        else:
            self._animate_history(show=True)

    def _animate_history(self, show: bool) -> None:
        """Eased animation to reveal/hide history. Uses time-based easing for smoothness."""
        duration = 0.28  # seconds
        target = 24

        # if history UI removed, persist desired state and return
        if getattr(self, 'hist_frame', None) is None or getattr(self, 'hist_list', None) is None:
            self.hist_visible = bool(show)
            try:
                self._save_prefs({'history_visible': bool(show)})
            except Exception:
                pass
            return

        # prepare packing when showing
        if show:
            try:
                # pack frame to the right of the dock
                self.hist_frame.pack(side='right', fill='y')
            except Exception:
                pass
            try:
                self.hist_list.pack(fill='y', expand=False)
            except Exception:
                pass

        # animation state
        start_w = int(self.hist_list.cget('width') or 0)
        end_w = target if show else 0
        start_t = time.time()
        self.hist_animating = True

        def step():
            now = time.time()
            t = (now - start_t) / duration
            if t >= 1.0:
                # finish
                final = end_w
                try:
                    self.hist_list.config(width=final)
                except Exception:
                    pass
                if end_w == 0:
                    try:
                        self.hist_list.forget()
                    except Exception:
                        pass
                    try:
                        self.hist_frame.forget()
                    except Exception:
                        pass
                    self.hist_visible = False
                    try:
                        self.hist_toggle.config(text='History ▸')
                    except Exception:
                        pass
                    # persist collapsed state
                    try:
                        self._save_prefs({'history_visible': False})
                    except Exception:
                        pass
                else:
                    self.hist_visible = True
                    try:
                        self.hist_toggle.config(text='History ▾')
                    except Exception:
                        pass
                    # persist expanded state
                    try:
                        self._save_prefs({'history_visible': True})
                    except Exception:
                        pass
                self.hist_animating = False
                return

            # cubic ease-out
            eased = 1 - (1 - t) ** 3
            cur = int(round(start_w + (end_w - start_w) * eased))
            try:
                self.hist_list.config(width=max(0, cur))
            except Exception:
                pass
            self.after(16, step)

        step()


def main() -> None:
    app = Calculator()
    app.mainloop()


if __name__ == '__main__':
    main()
