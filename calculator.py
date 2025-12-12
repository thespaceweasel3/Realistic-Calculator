#!/usr/bin/env python3
"""
Seven-segment style calculator.

Run with: python calculator.py
"""
import tkinter as tk
from tkinter import ttk

SEGMENTS = {
    '0': (1,1,1,1,1,1,0), '1': (0,1,1,0,0,0,0), '2': (1,1,0,1,1,0,1),
    '3': (1,1,1,1,0,0,1), '4': (0,1,1,0,0,1,1), '5': (1,0,1,1,0,1,1),
    '6': (1,0,1,1,1,1,1), '7': (1,1,1,0,0,0,0), '8': (1,1,1,1,1,1,1),
    '9': (1,1,1,1,0,1,1), '-': (0,0,0,0,0,0,1), ' ': (0,0,0,0,0,0,0)
}

class SevenSegment(tk.Canvas):
    def __init__(self, master, digits=8, seg_len=20, seg_thick=6, pad=6, **kw):
        super().__init__(master, bg='#111', highlightthickness=0, **kw)
        self.digits = digits
        self.s = seg_len
        self.t = seg_thick
        self.pad = pad
        self.on = '#ff5f1f'
        self.off = '#220804'
        self.dp_color = '#ff8a3d'
        w = (self.s + self.t*2 + self.pad) * digits + self.pad
        h = self.s*2 + self.t*3 + self.pad*2
        self.config(width=w, height=h)
        self.slots = []
        self._create_slots()

    def _create_slots(self):
        self.delete('all')
        self.slots.clear()
        x = self.pad
        for _ in range(self.digits):
            segs = []
            s, t = self.s, self.t
            # a
            segs.append(self.create_polygon(x+t, self.pad, x+t+s, self.pad, x+t+s-t, self.pad+t, x+t+t, self.pad+t, fill=self.off, outline=self.off))
            # b
            segs.append(self.create_polygon(x+t+s, self.pad, x+t+s+t, self.pad+t, x+t+s+t, self.pad+t+s, x+t+s, self.pad+t+s-t, fill=self.off, outline=self.off))
            # c
            segs.append(self.create_polygon(x+t+s, self.pad+t+s, x+t+s+t, self.pad+t+s+t, x+t+s+t, self.pad+t+s+t+s, x+t+s, self.pad+t+s+t+s-t, fill=self.off, outline=self.off))
            # d
            segs.append(self.create_polygon(x+t, self.pad+t+s+t+s, x+t+s, self.pad+t+s+t+s, x+t+s-t, self.pad+t+s+t+s-t, x+t+t, self.pad+t+s+t+s-t, fill=self.off, outline=self.off))
            # e
            segs.append(self.create_polygon(x, self.pad+t+s, x+t, self.pad+t+s+t, x+t, self.pad+t+s+t+s-t, x, self.pad+t+s+t+s-t, fill=self.off, outline=self.off))
            # f
            segs.append(self.create_polygon(x, self.pad, x+t, self.pad+t, x+t, self.pad+t+s-t, x, self.pad+t+s, fill=self.off, outline=self.off))
            # g
            segs.append(self.create_polygon(x+t+t, self.pad+t+s, x+t+s-t, self.pad+t+s, x+t+s-t-t, self.pad+t+s+t, x+t+t+t, self.pad+t+s+t, fill=self.off, outline=self.off))
            dp_r = max(2, t//1 + 2)
            dp_x = x+t+s+t
            dp_y = self.pad+t+s+t+s - dp_r*2
            dp = self.create_oval(dp_x, dp_y, dp_x+dp_r*2, dp_y+dp_r*2, fill=self.off, outline=self.off)
            self.slots.append((segs, dp))
            x += self.s + self.t*2 + self.pad

    def set_text(self, text):
        text = str(text)
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
            chars = chars[-self.digits:]
        else:
            chars = [' ']*(self.digits-len(chars)) + chars
        for idx, ch in enumerate(chars):
            segs, dp = self.slots[idx]
            has_dp = ch.endswith('.')
            base = ch[0] if ch else ' '
            pattern = SEGMENTS.get(base, SEGMENTS[' '])
            for seg_id, on in zip(segs, pattern):
                color = self.on if on else self.off
                self.itemconfig(seg_id, fill=color, outline=color)
            dp_color = self.dp_color if has_dp else self.off
            self.itemconfig(dp, fill=dp_color, outline=dp_color)


class Calculator:
    def __init__(self, root):
        self.root = root
        root.title('Calculator')
        self.frame = ttk.Frame(root)
        self.frame.pack(padx=8, pady=8)
        self.expr_var = tk.StringVar()
        self.info = tk.Label(self.frame, textvariable=self.expr_var, anchor='e', bg='#111', fg='#ddd')
        self.info.pack(fill='x')
        self.display = SevenSegment(self.frame, digits=10)
        self.display.pack(pady=6)
        self.expression = ''
        self.just_eval = False
        self._make_buttons()
        root.bind('<Key>', self.on_key)

    def _make_buttons(self):
        specs = [
            ('C',1,0),('+/-',1,1),('%',1,2),('/',1,3),
            ('7',2,0),('8',2,1),('9',2,2),('*',2,3),
            ('4',3,0),('5',3,1),('6',3,2),('-',3,3),
            ('1',4,0),('2',4,1),('3',4,2),('+',4,3),
            ('0',5,0,2),('.',5,2),('=',5,3)
        ]
        for spec in specs:
            label = spec[0]
            r = spec[1]
            c = spec[2]
            colspan = spec[3] if len(spec) > 3 else 1
            def cmd(L=label):
                self.on_button(L)
            btn = tk.Button(self.frame, text=label, command=cmd, font=('Segoe UI',12,'bold'), bg='#222', fg='#fff', bd=3, relief='raised')
            btn.grid(row=r, column=c, columnspan=colspan, sticky='nsew', padx=3, pady=3)
        for i in range(4):
            self.frame.columnconfigure(i, weight=1)
        for i in range(1,6):
            self.frame.rowconfigure(i, weight=1)

    def on_button(self, label):
        if label == 'C':
            self.expression = ''
            self.just_eval = False
        elif label == '=':
            self._evaluate()
            return
        elif label == '+/-':
            self._negate(); return
        elif label == '%':
            self._percent(); return
        else:
            if self.just_eval and (label.isdigit() or label == '.'):
                self.expression = ''
            self.expression += label
            self.just_eval = False
        self._update()

    def on_key(self, event):
        k = event.char
        if k in '0123456789.+-*/()':
            if self.just_eval and (k.isdigit() or k == '.'):
                self.expression = ''
            self.expression += k
            self.just_eval = False
            self._update()
        elif event.keysym in ('Return','equal'):
            self._evaluate()
        elif event.keysym == 'BackSpace':
            self.expression = self.expression[:-1]
            self.just_eval = False
            self._update()
        elif event.keysym == 'Escape':
            self.expression = ''
            self.just_eval = False
            self._update()

    def _update(self):
        self.expr_var.set(self.expression)
        toshow = self.expression or '0'
        # show last number token
        i = len(toshow)-1
        while i>=0 and (toshow[i].isdigit() or toshow[i] in '.-'):
            i -= 1
        num = toshow[i+1:] or '0'
        if len(num) > self.display.digits:
            num = num[-self.display.digits:]
        self.display.set_text(num)

    def _safe_eval(self, expr):
        allowed = set('0123456789.+-*/()% ')
        if any(ch not in allowed for ch in expr):
            raise ValueError('Invalid char')
        return eval(expr, {'__builtins__':None}, {})

    def _evaluate(self):
        if not self.expression:
            return
        try:
            r = self._safe_eval(self.expression)
            if isinstance(r, float):
                s = ('%f' % r).rstrip('0').rstrip('.')
            else:
                s = str(r)
            self.expression = s
            self.just_eval = True
        except Exception:
            self.expression = 'ERR'
            self.just_eval = False
        self._update()

    def _negate(self):
        if not self.expression:
            self.expression = '-'
            self._update(); return
        i = len(self.expression)-1
        while i>=0 and (self.expression[i].isdigit() or self.expression[i]=='.'):
            i -= 1
        num = self.expression[i+1:]
        if not num: return
        try:
            v = -float(num)
            rep = str(int(v)) if v.is_integer() else str(v)
            self.expression = self.expression[:i+1] + rep
            self._update()
        except Exception:
            pass

    def _percent(self):
        if not self.expression: return
        i = len(self.expression)-1
        while i>=0 and (self.expression[i].isdigit() or self.expression[i]=='.'):
            i -= 1
        num = self.expression[i+1:]
        if not num: return
        try:
            v = float(num)/100.0
            rep = str(int(v)) if v.is_integer() else str(v)
            self.expression = self.expression[:i+1] + rep
            self._update()
        except Exception:
            pass

def main():
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Seven-segment style calculator (cleaned file to avoid indentation issues).

Run: python C:/workspace/calculator.py
"""
import tkinter as tk
from tkinter import ttk


SEGMENTS = {
    "0": (1, 1, 1, 1, 1, 1, 0),
    "1": (0, 1, 1, 0, 0, 0, 0),
    "2": (1, 1, 0, 1, 1, 0, 1),
    "3": (1, 1, 1, 1, 0, 0, 1),
    "4": (0, 1, 1, 0, 0, 1, 1),
    "5": (1, 0, 1, 1, 0, 1, 1),
    "6": (1, 0, 1, 1, 1, 1, 1),
    "7": (1, 1, 1, 0, 0, 0, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
    "-": (0, 0, 0, 0, 0, 0, 1),
    " ": (0, 0, 0, 0, 0, 0, 0),
}


class SevenSegmentDisplay(tk.Canvas):
    def __init__(self, master, digits=10, seg_length=30, seg_thickness=8, padding=8, **kwargs):
        bg = kwargs.pop("bg", "#111")
        super().__init__(master, bg=bg, highlightthickness=0, **kwargs)
        self.digits = digits
        self.seg_length = seg_length
        self.seg_thickness = seg_thickness
        self.padding = padding
        self.on_color = "#ff5f1f"
        self.off_color = "#220804"
        self.dp_color = "#ff8a3d"
        self.char_items = []
        self.width = (seg_length + seg_thickness * 2 + padding) * digits + padding
        self.height = seg_length * 2 + seg_thickness * 3 + padding * 2
        self.configure(width=self.width, height=self.height)
        self._create_slots()

    def _create_slots(self):
        self.char_items.clear()
        self.delete("all")
        x = self.padding
        for _ in range(self.digits):
            self.char_items.append(self._create_digit_slot(x, self.padding))
            x += self.seg_length + self.seg_thickness * 2 + self.padding

    def _create_digit_slot(self, x, y):
        s = self.seg_length
        t = self.seg_thickness
        segs = []
        # a
        segs.append(self.create_polygon(x + t, y, x + t + s, y, x + t + s - t, y + t, x + t + t, y + t, fill=self.off_color, outline=self.off_color))
        # b
        segs.append(self.create_polygon(x + t + s, y, x + t + s + t, y + t, x + t + s + t, y + t + s, x + t + s, y + t + s - t, fill=self.off_color, outline=self.off_color))
        # c
        segs.append(self.create_polygon(x + t + s, y + t + s, x + t + s + t, y + t + s + t, x + t + s + t, y + t + s + t + s, x + t + s, y + t + s + t + s - t, fill=self.off_color, outline=self.off_color))
        # d
        segs.append(self.create_polygon(x + t, y + t + s + t + s, x + t + s, y + t + s + t + s, x + t + s - t, y + t + s + t + s - t, x + t + t, y + t + s + t + s - t, fill=self.off_color, outline=self.off_color))
        # e
        segs.append(self.create_polygon(x, y + t + s, x + t, y + t + s + t, x + t, y + t + s + t + s - t, x, y + t + s + t + s - t, fill=self.off_color, outline=self.off_color))
        # f
        segs.append(self.create_polygon(x, y, x + t, y + t, x + t, y + t + s - t, x, y + t + s, fill=self.off_color, outline=self.off_color))
        # g
        segs.append(self.create_polygon(x + t + t, y + t + s, x + t + s - t, y + t + s, x + t + s - t - t, y + t + s + t, x + t + t + t, y + t + s + t, fill=self.off_color, outline=self.off_color))
        dp_r = t // 1 + 2
        dp_x = x + t + s + t
        dp_y = y + t + s + t + s - dp_r * 2
        dp = self.create_oval(dp_x, dp_y, dp_x + dp_r * 2, dp_y + dp_r * 2, fill=self.off_color, outline=self.off_color)
        return (segs, dp)

    def set_text(self, text: str):
        text = str(text)
        chars = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == ".":
                if chars:
                    chars[-1] += "."
                else:
                    chars.append(".")
                i += 1
                continue
            chars.append(ch)
            i += 1
        if len(chars) > self.digits:
            chars = chars[-self.digits :]
        else:
            chars = [" "] * (self.digits - len(chars)) + chars
        for idx, ch in enumerate(chars):
            segs, dp = self.char_items[idx]
            has_dp = ch.endswith(".")
            base = ch[0] if ch else " "
            if base.isdigit():
                pattern = SEGMENTS.get(base, SEGMENTS[" "])
            elif base == "-":
                pattern = SEGMENTS["-"]
            else:
                pattern = SEGMENTS[" "]
            for seg_id, on in zip(segs, pattern):
                color = self.on_color if on else self.off_color
                self.itemconfig(seg_id, fill=color, outline=color)
            dp_color = self.dp_color if has_dp else self.off_color
            self.itemconfig(dp, fill=dp_color, outline=dp_color)


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Seven-Segment Calculator")
        root.configure(bg="#0a0a0a")

        self.mainframe = ttk.Frame(root)
        self.mainframe.pack(padx=12, pady=12)

        self.display_frame = tk.Frame(self.mainframe, bg="#111")
        self.display_frame.grid(row=0, column=0, columnspan=4, sticky="ew")

        self.expr_var = tk.StringVar(value="")
        self.info_label = tk.Label(self.display_frame, textvariable=self.expr_var, anchor="e", fg="#ddd", bg="#111", font=("Segoe UI", 10))
        self.info_label.pack(fill="x", padx=8, pady=(8, 4))

        self.display = SevenSegmentDisplay(self.display_frame, digits=12, seg_length=28, seg_thickness=8, padding=6)
        self.display.pack(padx=6, pady=(0, 8))

        btn_specs = [
            ("C", 1, 0), ("+/-", 1, 1), ("%", 1, 2), ("/", 1, 3),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 2, 3),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3),
            ("0", 5, 0, 2), (".", 5, 2), ("=", 5, 3),
        ]

        for spec in btn_specs:
            label = spec[0]
            r = spec[1]
            c = spec[2]
            colspan = spec[3] if len(spec) > 3 else 1
            b = tk.Button(
                self.mainframe,
                text=label,
                command=lambda L=label: self.on_button(L),
                font=("Segoe UI", 14, "bold"),
                fg="#fff",
                bg="#222",
                activebackground="#333",
                bd=3,
                relief="raised",
                padx=8,
                pady=8,
            )
            b.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=3, pady=3)

        for i in range(4):
            self.mainframe.columnconfigure(i, weight=1)
        for i in range(1, 6):
            self.mainframe.rowconfigure(i, weight=1)

        self.expression = ""
        self.last_result = None
        self.just_evaluated = False

        root.bind("<Key>", self.on_key)

        self._update_display()

    def on_button(self, label):
        if label == "C":
            self.expression = ""
            self.last_result = None
            self.just_evaluated = False
        elif label == "=":
            self._evaluate()
        elif label == "+/-":
            self._negate()
        elif label == "%":
            self._percent()
        else:
            if self.just_evaluated and (label.isdigit() or label == "."):
                self.expression = ""
            self.expression += label
            self.just_evaluated = False
        self._update_display()

    def on_key(self, event):
        k = event.char
        if k in "0123456789.+-*/()":
            if self.just_evaluated and (k.isdigit() or k == "."):
                self.expression = ""
            self.expression += k
            self.just_evaluated = False
            self._update_display()
        elif event.keysym in ("Return", "equal"):
            self._evaluate()
        elif event.keysym == "BackSpace":
            self.expression = self.expression[:-1]
            self.just_evaluated = False
            self._update_display()
        elif event.keysym == "Escape":
            self.expression = ""
            self.just_evaluated = False
            self._update_display()

    def _update_display(self):
        self.expr_var.set(self.expression)
        text = self.expression
        if not text:
            text = "0"
        display_text = text
        try:
            i = len(text) - 1
            while i >= 0 and (text[i].isdigit() or text[i] in ".-"):
                i -= 1
            display_text = text[i+1:]
            if display_text == "":
                display_text = "0"
        except Exception:
            display_text = text[-self.display.digits:]
        if len(display_text) > self.display.digits:
            display_text = display_text[-self.display.digits:]
        self.display.set_text(display_text)

    def _safe_eval(self, expr: str):
        allowed = set("0123456789.+-*/()% ")
        if any(ch not in allowed for ch in expr):
            raise ValueError("Invalid characters in expression")
        return eval(expr, {"__builtins__": None}, {})

    def _evaluate(self):
        if not self.expression:
            return
        try:
            result = self._safe_eval(self.expression)
            if isinstance(result, float):
                s = ("%f" % result).rstrip("0").rstrip(".")
            else:
                s = str(result)
            self.expression = s
            self.last_result = s
            self.just_evaluated = True
        except Exception:
            self.expression = "ERR"
            self.just_evaluated = False
        self._update_display()

    def _negate(self):
        if not self.expression:
            self.expression = "-"
            return
        i = len(self.expression) - 1
        while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == "."):
            i -= 1
        num = self.expression[i+1:]
        if not num:
            return
        try:
            val = float(num)
            val = -val
            if val.is_integer():
                rep = str(int(val))
            else:
                rep = str(val)
            self.expression = self.expression[: i + 1] + rep
        except Exception:
            pass

    def _percent(self):
        if not self.expression:
            return
        i = len(self.expression) - 1
        while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == "."):
            i -= 1
        num = self.expression[i+1:]
        if not num:
            return
        try:
            val = float(num) / 100.0
            if val.is_integer():
                rep = str(int(val))
            else:
                rep = str(val)
            self.expression = self.expression[: i + 1] + rep
            self._update_display()
        except Exception:
            pass


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Seven-segment style calculator (cleaned file to avoid indentation issues).

Run: python C:\workspace\calculator.py
"""
import tkinter as tk
from tkinter import ttk


SEGMENTS = {
    "0": (1, 1, 1, 1, 1, 1, 0),
    "1": (0, 1, 1, 0, 0, 0, 0),
    "2": (1, 1, 0, 1, 1, 0, 1),
    "3": (1, 1, 1, 1, 0, 0, 1),
    "4": (0, 1, 1, 0, 0, 1, 1),
    "5": (1, 0, 1, 1, 0, 1, 1),
    "6": (1, 0, 1, 1, 1, 1, 1),
    "7": (1, 1, 1, 0, 0, 0, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
    "-": (0, 0, 0, 0, 0, 0, 1),
    " ": (0, 0, 0, 0, 0, 0, 0),
}


class SevenSegmentDisplay(tk.Canvas):
    def __init__(self, master, digits=10, seg_length=30, seg_thickness=8, padding=8, **kwargs):
        bg = kwargs.pop("bg", "#111")
        super().__init__(master, bg=bg, highlightthickness=0, **kwargs)
        self.digits = digits
        self.seg_length = seg_length
        self.seg_thickness = seg_thickness
        self.padding = padding
        self.on_color = "#ff5f1f"
        self.off_color = "#220804"
        self.dp_color = "#ff8a3d"
        self.char_items = []
        self.width = (seg_length + seg_thickness * 2 + padding) * digits + padding
        self.height = seg_length * 2 + seg_thickness * 3 + padding * 2
        self.configure(width=self.width, height=self.height)
        self._create_slots()

    def _create_slots(self):
        self.char_items.clear()
        self.delete("all")
        x = self.padding
        for _ in range(self.digits):
            self.char_items.append(self._create_digit_slot(x, self.padding))
            x += self.seg_length + self.seg_thickness * 2 + self.padding

    def _create_digit_slot(self, x, y):
        s = self.seg_length
        t = self.seg_thickness
        segs = []
        # a
        segs.append(self.create_polygon(x + t, y, x + t + s, y, x + t + s - t, y + t, x + t + t, y + t, fill=self.off_color, outline=self.off_color))
        # b
        segs.append(self.create_polygon(x + t + s, y, x + t + s + t, y + t, x + t + s + t, y + t + s, x + t + s, y + t + s - t, fill=self.off_color, outline=self.off_color))
        # c
        segs.append(self.create_polygon(x + t + s, y + t + s, x + t + s + t, y + t + s + t, x + t + s + t, y + t + s + t + s, x + t + s, y + t + s + t + s - t, fill=self.off_color, outline=self.off_color))
        # d
        segs.append(self.create_polygon(x + t, y + t + s + t + s, x + t + s, y + t + s + t + s, x + t + s - t, y + t + s + t + s - t, x + t + t, y + t + s + t + s - t, fill=self.off_color, outline=self.off_color))
        # e
        segs.append(self.create_polygon(x, y + t + s, x + t, y + t + s + t, x + t, y + t + s + t + s - t, x, y + t + s + t + s - t, fill=self.off_color, outline=self.off_color))
        # f
        segs.append(self.create_polygon(x, y, x + t, y + t, x + t, y + t + s - t, x, y + t + s, fill=self.off_color, outline=self.off_color))
        # g
        segs.append(self.create_polygon(x + t + t, y + t + s, x + t + s - t, y + t + s, x + t + s - t - t, y + t + s + t, x + t + t + t, y + t + s + t, fill=self.off_color, outline=self.off_color))
        dp_r = t // 1 + 2
        dp_x = x + t + s + t
        dp_y = y + t + s + t + s - dp_r * 2
        dp = self.create_oval(dp_x, dp_y, dp_x + dp_r * 2, dp_y + dp_r * 2, fill=self.off_color, outline=self.off_color)
        return (segs, dp)

    def set_text(self, text: str):
        text = str(text)
        chars = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == ".":
                if chars:
                    chars[-1] += "."
                else:
                    chars.append(".")
                i += 1
                continue
            chars.append(ch)
            i += 1
        if len(chars) > self.digits:
            chars = chars[-self.digits :]
        else:
            chars = [" "] * (self.digits - len(chars)) + chars
        for idx, ch in enumerate(chars):
            segs, dp = self.char_items[idx]
            has_dp = ch.endswith(".")
            base = ch[0] if ch else " "
            if base.isdigit():
                pattern = SEGMENTS.get(base, SEGMENTS[" "])
            elif base == "-":
                pattern = SEGMENTS["-"]
            else:
                pattern = SEGMENTS[" "]
            for seg_id, on in zip(segs, pattern):
                color = self.on_color if on else self.off_color
                self.itemconfig(seg_id, fill=color, outline=color)
            dp_color = self.dp_color if has_dp else self.off_color
            self.itemconfig(dp, fill=dp_color, outline=dp_color)


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Seven-Segment Calculator")
        root.configure(bg="#0a0a0a")

        self.mainframe = ttk.Frame(root)
        self.mainframe.pack(padx=12, pady=12)

        self.display_frame = tk.Frame(self.mainframe, bg="#111")
        self.display_frame.grid(row=0, column=0, columnspan=4, sticky="ew")

        self.expr_var = tk.StringVar(value="")
        self.info_label = tk.Label(self.display_frame, textvariable=self.expr_var, anchor="e", fg="#ddd", bg="#111", font=("Segoe UI", 10))
        self.info_label.pack(fill="x", padx=8, pady=(8, 4))

        self.display = SevenSegmentDisplay(self.display_frame, digits=12, seg_length=28, seg_thickness=8, padding=6)
        self.display.pack(padx=6, pady=(0, 8))

        btn_specs = [
            ("C", 1, 0), ("+/-", 1, 1), ("%", 1, 2), ("/", 1, 3),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 2, 3),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3),
            ("0", 5, 0, 2), (".", 5, 2), ("=", 5, 3),
        ]

        for spec in btn_specs:
            label = spec[0]
            r = spec[1]
            c = spec[2]
            colspan = spec[3] if len(spec) > 3 else 1
            b = tk.Button(self.mainframe, text=label, command=lambda L=label: self.on_button(L), font=("Segoe UI", 14, "bold"), fg="#fff", bg="#222", activebackground="#333", bd=3, relief="raised", padx=8, pady=8)
            b.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=3, pady=3)

        for i in range(4):
            self.mainframe.columnconfigure(i, weight=1)
        for i in range(1, 6):
            self.mainframe.rowconfigure(i, weight=1)

        self.expression = ""
        self.last_result = None
        self.just_evaluated = False

        root.bind("<Key>", self.on_key)

        self._update_display()

    def on_button(self, label):
        if label == "C":
            self.expression = ""
            self.last_result = None
            self.just_evaluated = False
        elif label == "=":
            self._evaluate()
        elif label == "+/-":
            self._negate()
        elif label == "%":
            self._percent()
        else:
            if self.just_evaluated and (label.isdigit() or label == "."):
                self.expression = ""
            self.expression += label
            self.just_evaluated = False
        self._update_display()

    def on_key(self, event):
        k = event.char
        if k in "0123456789.+-*/()":
            if self.just_evaluated and (k.isdigit() or k == "."):
                self.expression = ""
            self.expression += k
            self.just_evaluated = False
            self._update_display()
        elif event.keysym in ("Return", "equal"):
            self._evaluate()
        elif event.keysym == "BackSpace":
            self.expression = self.expression[:-1]
            self.just_evaluated = False
            self._update_display()
        elif event.keysym == "Escape":
            self.expression = ""
            self.just_evaluated = False
            self._update_display()

    def _update_display(self):
        self.expr_var.set(self.expression)
        text = self.expression
        if not text:
            text = "0"
        display_text = text
        try:
            i = len(text) - 1
            while i >= 0 and (text[i].isdigit() or text[i] in ".-"):
                i -= 1
            display_text = text[i+1:]
            if display_text == "":
                display_text = "0"
        except Exception:
            display_text = text[-self.display.digits:]
        if len(display_text) > self.display.digits:
            display_text = display_text[-self.display.digits:]
        self.display.set_text(display_text)

    def _safe_eval(self, expr: str):
        allowed = set("0123456789.+-*/()% ")
        if any(ch not in allowed for ch in expr):
            raise ValueError("Invalid characters in expression")
        return eval(expr, {"__builtins__": None}, {})

    def _evaluate(self):
        if not self.expression:
            return
        try:
            result = self._safe_eval(self.expression)
            if isinstance(result, float):
                s = ("%f" % result).rstrip("0").rstrip(".")
            else:
                s = str(result)
            self.expression = s
            self.last_result = s
            self.just_evaluated = True
        except Exception:
            self.expression = "ERR"
            self.just_evaluated = False
        self._update_display()

    def _negate(self):
        if not self.expression:
            self.expression = "-"
            return
        i = len(self.expression) - 1
        while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == "."):
            i -= 1
        num = self.expression[i+1:]
        if not num:
            return
        try:
            val = float(num)
            val = -val
            if val.is_integer():
                rep = str(int(val))
            else:
                rep = str(val)
            self.expression = self.expression[: i + 1] + rep
        except Exception:
            pass

    def _percent(self):
        if not self.expression:
            return
        i = len(self.expression) - 1
        while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == "."):
            i -= 1
        num = self.expression[i+1:]
        if not num:
            return
        try:
            val = float(num) / 100.0
            if val.is_integer():
                rep = str(int(val))
            else:
                rep = str(val)
            self.expression = self.expression[: i + 1] + rep
            self._update_display()
        except Exception:
            pass


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple Calculator with a seven-segment style display using Tkinter.

Run: python calculator.py

Features:
- Realistic seven-segment style digits (Canvas-drawn)
- Basic operations: + - * /, parentheses, decimal point
- Clear, backspace, +/- and equals
- Keyboard support for digits and operators
"""
import tkinter as tk
from tkinter import ttk


SEGMENTS = {
    # a, b, c, d, e, f, g  (segments top, top-right, bottom-right, bottom, bottom-left, top-left, middle)
    "0": (1, 1, 1, 1, 1, 1, 0),
    "1": (0, 1, 1, 0, 0, 0, 0),
    "2": (1, 1, 0, 1, 1, 0, 1),
    "3": (1, 1, 1, 1, 0, 0, 1),
    "4": (0, 1, 1, 0, 0, 1, 1),
    "5": (1, 0, 1, 1, 0, 1, 1),
    "6": (1, 0, 1, 1, 1, 1, 1),
    "7": (1, 1, 1, 0, 0, 0, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
    "-": (0, 0, 0, 0, 0, 0, 1),
    " ": (0, 0, 0, 0, 0, 0, 0),
}


class SevenSegmentDisplay(tk.Canvas):
    def __init__(self, master, digits=10, seg_length=30, seg_thickness=8, padding=8, **kwargs):
        # Background and color choices to mimic calculator
        bg = kwargs.pop("bg", "#111")
        super().__init__(master, bg=bg, highlightthickness=0, **kwargs)
        self.digits = digits
        self.seg_length = seg_length
        self.seg_thickness = seg_thickness
        self.padding = padding
        self.on_color = "#ff5f1f"
        self.off_color = "#220804"
        self.dp_color = "#ff8a3d"
        self.char_items = []
        self.width = (seg_length + seg_thickness * 2 + padding) * digits + padding
        self.height = seg_length * 2 + seg_thickness * 3 + padding * 2
        self.configure(width=self.width, height=self.height)
        self._create_slots()

    def _create_slots(self):
        self.char_items.clear()
        self.delete("all")
        x = self.padding
        for i in range(self.digits):
            items = self._create_digit_slot(x, self.padding)
            self.char_items.append(items)
            x += self.seg_length + self.seg_thickness * 2 + self.padding

    def _create_digit_slot(self, x, y):
        s = self.seg_length
        t = self.seg_thickness
        # Coordinates are relative to (x, y)
        # We'll draw 7 polygons for segments and one oval for decimal point
        segs = []
        # a (top)
        segs.append(self._polygon([(x + t, y), (x + t + s, y), (x + t + s - t, y + t), (x + t + t, y + t)]))
        # b (top-right)
        segs.append(self._polygon([(x + t + s, y), (x + t + s + t, y + t), (x + t + s + t, y + t + s), (x + t + s, y + t + s - t)]))
        # c (bottom-right)
        segs.append(self._polygon([(x + t + s, y + t + s), (x + t + s + t, y + t + s + t), (x + t + s + t, y + t + s + t + s), (x + t + s, y + t + s + t + s - t)]))
        # d (bottom)
        segs.append(self._polygon([(x + t, y + t + s + t + s), (x + t + s, y + t + s + t + s), (x + t + s - t, y + t + s + t + s - t), (x + t + t, y + t + s + t + s - t)]))
        # e (bottom-left)
        segs.append(self._polygon([(x, y + t + s), (x + t, y + t + s + t), (x + t, y + t + s + t + s - t), (x, y + t + s + t + s - t)]))
        # f (top-left)
        segs.append(self._polygon([(x, y), (x + t, y + t), (x + t, y + t + s - t), (x, y + t + s)]))
        # g (middle)
        segs.append(self._polygon([(x + t + t, y + t + s), (x + t + s - t, y + t + s), (x + t + s - t - t, y + t + s + t), (x + t + t + t, y + t + s + t)]))
        # decimal point
        dp_r = t // 1 + 2
        dp_x = x + t + s + t
        dp_y = y + t + s + t + s - dp_r * 2
        dp = self.create_oval(dp_x, dp_y, dp_x + dp_r * 2, dp_y + dp_r * 2, fill=self.off_color, outline=self.off_color)
        # ensure segments start off
        for seg in segs:
            self.itemconfig(seg, fill=self.off_color, outline=self.off_color)
        return (segs, dp)

    def _polygon(self, points):
        # Slightly smooth the polygon by returning a polygon object
        return self.create_polygon(points, smooth=False)

    def set_text(self, text: str):
        # Right-align text into digits
        text = str(text)
        # Build mapping of characters; handle decimal points attached to previous digit
        chars = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch == ".":
                # Attach decimal to previous if exists, else to leading space
                if chars:
                    chars[-1] += "."
                else:
                    chars.append(".")
                i += 1
                continue
            else:
                # include minus sign as its own char
                chars.append(ch)
            i += 1

        # Trim or pad
        if len(chars) > self.digits:
            chars = chars[-self.digits :]
        else:
            chars = [" "] * (self.digits - len(chars)) + chars

        for idx, ch in enumerate(chars):
            segs, dp = self.char_items[idx]
            has_dp = ch.endswith(".")
            base = ch[0] if ch else " "
            if base.isdigit():
                pattern = SEGMENTS.get(base, SEGMENTS[" "])
            elif base == "-":
                pattern = SEGMENTS["-"]
            else:
                pattern = SEGMENTS[" "]
            # update segments
            for seg_id, on in zip(segs, pattern):
                color = self.on_color if on else self.off_color
                self.itemconfig(seg_id, fill=color, outline=color)
            # decimal point
            dp_color = self.dp_color if has_dp else self.off_color
            self.itemconfig(dp, fill=dp_color, outline=dp_color)


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Seven-Segment Calculator")
        root.configure(bg="#0a0a0a")

        self.mainframe = ttk.Frame(root)
        self.mainframe.pack(padx=12, pady=12)

        # Display area
        self.display_frame = tk.Frame(self.mainframe, bg="#111")
        self.display_frame.grid(row=0, column=0, columnspan=4, sticky="ew")

        self.expr_var = tk.StringVar(value="")
        self.info_label = tk.Label(self.display_frame, textvariable=self.expr_var, anchor="e", fg="#ddd", bg="#111", font=("Segoe UI", 10))
        self.info_label.pack(fill="x", padx=8, pady=(8, 4))

        self.display = SevenSegmentDisplay(self.display_frame, digits=12, seg_length=28, seg_thickness=8, padding=6)
        self.display.pack(padx=6, pady=(0, 8))

        # Buttons
        btn_specs = [
            ("C", 1, 0), ("+/-", 1, 1), ("%", 1, 2), ("/", 1, 3),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 2, 3),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3),
            ("0", 5, 0, 2), (".", 5, 2), ("=", 5, 3),
        ]

        for spec in btn_specs:
            label = spec[0]
            r = spec[1]
            c = spec[2]
            colspan = spec[3] if len(spec) > 3 else 1
            b = tk.Button(self.mainframe,
                          text=label,
                          command=lambda L=label: self.on_button(L),
                          font=("Segoe UI", 14, "bold"),
                          fg="#fff",
                          bg="#222",
                          activebackground="#333",
                          bd=3,
                          relief="raised",
                          padx=8,
                          pady=8)
            b.grid(row=r, column=c, columnspan=colspan, sticky="nsew", padx=3, pady=3)
        # Configure grid weights
        for i in range(4):
            self.mainframe.columnconfigure(i, weight=1)
        for i in range(1, 6):
            self.mainframe.rowconfigure(i, weight=1)

        self.expression = ""
        self.last_result = None
        self.just_evaluated = False

        # Bind keys
        root.bind("<Key>", self.on_key)

        # initialize display
        self._update_display()

    def on_button(self, label):
        if label == "C":
            self.expression = ""
            self.last_result = None
            self.just_evaluated = False
        elif label == "=":
            self._evaluate()
        elif label == "+/-":
            self._negate()
        elif label == "%":
            self._percent()
        else:
            # append
            # If a calculation was just completed and the user starts typing a digit or dot,
            # clear the old result so typing a new number begins fresh.
            if self.just_evaluated and (label.isdigit() or label == "."):
                self.expression = ""
            if label == "0":
                self.expression += "0"
            else:
                self.expression += label
            # any manual edit clears the just_evaluated state
            self.just_evaluated = False
        self._update_display()

    def on_key(self, event):
        k = event.char
        if k in "0123456789.+-*/()":
            # if a result was just shown and the user types a digit or dot, start a new number
            if self.just_evaluated and (k.isdigit() or k == "."):
                self.expression = ""
            self.expression += k
            self.just_evaluated = False
            self._update_display()
        elif event.keysym in ("Return", "equal"):
            self._evaluate()
        elif event.keysym == "BackSpace":
            self.expression = self.expression[:-1]
            self.just_evaluated = False
            self._update_display()
        elif event.keysym == "Escape":
            self.expression = ""
            self.just_evaluated = False
            self._update_display()

    def _update_display(self):
        # Show expression on top and the rightmost up to digits on seven seg
        self.expr_var.set(self.expression)
        text = self.expression
        if not text:
            text = "0"
        # Right-align and show only the last continuous token (number) in seven-seg
        display_text = text
        try:
            i = len(text) - 1
            while i >= 0 and (text[i].isdigit() or text[i] in ".-"):
                i -= 1
            display_text = text[i+1:]
            if display_text == "":
                display_text = "0"
        except Exception:
            display_text = text[-self.display.digits:]

        if len(display_text) > self.display.digits:
            display_text = display_text[-self.display.digits:]
        self.display.set_text(display_text)

    def _safe_eval(self, expr: str):
        # Allow only digits, operators and parentheses
        allowed = set("0123456789.+-*/()% ")
        if any(ch not in allowed for ch in expr):
            raise ValueError("Invalid characters in expression")
        # Evaluate in restricted namespace
        return eval(expr, {"__builtins__": None}, {})

    def _evaluate(self):
        if not self.expression:
            return
        try:
            result = self._safe_eval(self.expression)
            # Normalize result to string
            if isinstance(result, float):
                s = ("%f" % result).rstrip("0").rstrip(".")
            else:
                s = str(result)
            self.expression = s
            self.last_result = s
            self.just_evaluated = True
        except Exception:
            self.expression = "ERR"
        self._update_display()

    def _negate(self):
        # Try to negate last number
        if not self.expression:
            self.expression = "-"
            return
        # find last number
        i = len(self.expression) - 1
        while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == "."):
            i -= 1
        num = self.expression[i+1:]
        if not num:
            # nothing to negate
            return
        try:
            val = float(num)
            val = -val
            if val.is_integer():
                rep = str(int(val))
            else:
                rep = str(val)
            self.expression = self.expression[: i + 1] + rep
        except Exception:
            pass

    def _percent(self):
        # convert last number to percentage
        if not self.expression:
            return
        i = len(self.expression) - 1
        while i >= 0 and (self.expression[i].isdigit() or self.expression[i] == "."):
            i -= 1
        num = self.expression[i+1:]
        if not num:
            return
        try:
            val = float(num) / 100.0
            if val.is_integer():
                rep = str(int(val))
            else:
                rep = str(val)
            self.expression = self.expression[: i + 1] + rep
            self._update_display()
        except Exception:
            pass


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
