"""Bird Phone - run with:  python bird_phone.py
A small standalone program: just the bird phone, no browser, no background.
Drag the bird to move it. Click the red X to close."""
import ast, json, operator as op, os, random, time, tkinter as tk

TRANS = "#010203"
SAVE = os.path.join(os.path.expanduser("~"), ".bird_phone.json")
W, H = 330, 650
SX, SY, SW, SH = 54, 135, 222, 455  # screen position and size

try:
    data = json.load(open(SAVE))
except Exception:
    data = {}


def save():
    try:
        json.dump(data, open(SAVE, "w"))
    except Exception:
        pass


root = tk.Tk()
root.title("Bird Phone")
root.overrideredirect(True)
root.geometry(f"{W}x{H}+200+60")
root.attributes("-topmost", True)
try:
    root.attributes("-transparentcolor", TRANS)
except tk.TclError:
    pass
root.configure(bg=TRANS)

cv = tk.Canvas(root, width=W, height=H, bg=TRANS, highlightthickness=0)
cv.pack()


def rrect(x0, y0, x1, y1, r, **kw):
    pts = [x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r, x1, y1 - r, x1, y1,
           x1 - r, y1, x0 + r, y1, x0, y1, x0, y1 - r, x0, y0 + r, x0, y0]
    return cv.create_polygon(pts, smooth=True, **kw)


OUT = "#533846"
rrect(284, 96, 326, 126, 14, fill="#f4902a", outline=OUT, width=3)   # beak
rrect(284, 124, 318, 148, 12, fill="#e2492b", outline=OUT, width=3)
rrect(20, 24, 304, 628, 120, fill="#f7d63c", outline=OUT, width=4)   # body
cv.create_oval(170, 38, 246, 114, fill="white", outline=OUT, width=4)  # eye
cv.create_oval(212, 62, 238, 88, fill=OUT, outline=OUT)
cv.create_oval(4, 340, 62, 392, fill="white", outline=OUT, width=4)   # wing
cv.create_line(80, 70, 135, 70, fill=OUT, width=7, capstyle="round")  # speaker
rrect(SX - 6, SY - 6, SX + SW + 6, SY + SH + 6, 30, fill="#1c1c24")   # bezel

cv.create_oval(34, 30, 62, 58, fill="#d9423a", outline=OUT, width=2)   # close button
cv.create_text(48, 44, text="X", font=("Arial", 11, "bold"), fill="white")
drag = {}


def press(e):
    if (e.x - 48) ** 2 + (e.y - 44) ** 2 < 196:
        root.destroy()
    else:
        drag["o"] = (e.x, e.y)


def move(e):
    if "o" in drag:
        root.geometry(f"+{root.winfo_pointerx() - drag['o'][0]}+{root.winfo_pointery() - drag['o'][1]}")


cv.bind("<Button-1>", press)
cv.bind("<B1-Motion>", move)

frames = {}
current = ["home"]


def make(name, bg):
    f = tk.Frame(root, bg=bg)
    f.place(x=SX, y=SY, width=SW, height=SH - 24)
    frames[name] = f
    return f


def show(name):
    frames[name].tkraise()
    current[0] = name


home_btn = tk.Button(root, text="home", bg="#1c1c24", fg="#cfd6df", bd=0, activebackground="#333",
                     command=lambda: show("home"))
home_btn.place(x=SX, y=SY + SH - 24, width=SW, height=24)

# ---------------- Home ----------------
hm = make("home", "#3b4a7a")
APPS = [("Calc", "#ff9f0a", "calc"), ("Tiny AI", "#3b6df0", "ai"), ("Math", "#27ae60", "math"),
        ("Phone", "#34c759", "phone"), ("Flappy", "#f5b82e", "flappy"), ("Blocks", "#8b5a2b", "blocks"),
        ("Obby", "#e2492b", "obby"), ("Settings", "#8e8e93", "set")]
for i, (label, color, target) in enumerate(APPS):
    tk.Button(hm, text=label, bg=color, fg="white", font=("Arial", 9, "bold"), bd=0,
              command=lambda t=target: show(t)).place(x=6 + (i % 3) * 72, y=16 + (i // 3) * 84, width=66, height=72)
tk.Label(hm, text="Tap an app", bg="#3b4a7a", fg="#cfd6df").place(x=0, y=SH - 70, width=SW)

# ---------------- Calculator ----------------
ca = make("calc", "#111")
expr_l = tk.Label(ca, text="", bg="#111", fg="#9aa3ad", anchor="e", font=("Arial", 10))
expr_l.place(x=6, y=6, width=SW - 12)
cur_l = tk.Label(ca, text="0", bg="#111", fg="white", anchor="e", font=("Arial", 32))
cur_l.place(x=6, y=26, width=SW - 12, height=60)
st = {"cur": "0", "prev": None, "op": None, "fresh": False, "expr": ""}


def fmt(n):
    try:
        return f"{n:.12g}" if abs(n) != float("inf") and n == n else "Error"
    except Exception:
        return "Error"


def comp(a, b, o):
    a, b = float(a), float(b)
    return a + b if o == "+" else a - b if o == "-" else a * b if o == "x" else (a / b if b else float("nan"))


def key(k):
    s = st
    if s["cur"] == "Error" and not (k.isdigit() or k in ".C"):
        return
    if k.isdigit():
        if s["fresh"] or s["cur"] == "0":
            s["cur"], s["fresh"] = k, False
        elif len(s["cur"]) < 12:
            s["cur"] += k
    elif k == ".":
        if s["fresh"]:
            s["cur"], s["fresh"] = "0.", False
        elif "." not in s["cur"]:
            s["cur"] += "."
    elif k == "C":
        s.update(cur="0", prev=None, op=None, fresh=False, expr="")
    elif k == "<":
        if not s["fresh"]:
            s["cur"] = s["cur"][:-1] or "0"
            if s["cur"] == "-":
                s["cur"] = "0"
    elif k == "%":
        s["cur"], s["fresh"] = fmt(float(s["cur"]) / 100), True
    elif k == "=":
        if s["op"]:
            r = fmt(comp(s["prev"], s["cur"], s["op"]))
            s["expr"] = f'{s["prev"]} {s["op"]} {s["cur"]} ='
            s.update(cur=r, prev=None, op=None, fresh=True)
    else:
        if s["op"] and not s["fresh"]:
            s["cur"] = fmt(comp(s["prev"], s["cur"], s["op"]))
        s.update(prev=s["cur"], op=k, fresh=True)
        s["expr"] = f'{s["prev"]} {k}'
    if s["cur"] == "Error":
        s.update(prev=None, op=None, expr="", fresh=True)
    cur_l.config(text=s["cur"], font=("Arial", 32 if len(s["cur"]) < 9 else 20))
    expr_l.config(text=s["expr"].replace("x", "\u00d7"))


rows = [[("C", 0, 1), ("<", 1, 1), ("%", 2, 1), ("/", 3, 1)],
        [("7", 0, 1), ("8", 1, 1), ("9", 2, 1), ("x", 3, 1)],
        [("4", 0, 1), ("5", 1, 1), ("6", 2, 1), ("-", 3, 1)],
        [("1", 0, 1), ("2", 1, 1), ("3", 2, 1), ("+", 3, 1)],
        [("0", 0, 2), (".", 2, 1), ("=", 3, 1)]]
for r, row in enumerate(rows):
    for k, col, span in row:
        color = "#a5adb8" if k in "C<%" else "#ff9f0a" if k in "/x-+=" else "#2a2d33"
        tk.Button(ca, text=k.replace("/", "\u00f7").replace("x", "\u00d7"), bg=color,
                  fg="#111" if k in "C<%" else "white", bd=0, font=("Arial", 14),
                  command=lambda k=k: key(k)).place(x=6 + col * 54, y=96 + r * 62,
                                                    width=50 + 54 * (span - 1), height=56)

# ---------------- Tiny AI ----------------
ai = make("ai", "#f4f6fa")
log = tk.Text(ai, wrap="word", bg="#f4f6fa", bd=0, font=("Arial", 10), state="disabled")
log.place(x=4, y=4, width=SW - 8, height=SH - 80)
log.tag_config("u", foreground="#3b6df0", justify="right")
log.tag_config("a", foreground="#222")
entry = tk.Entry(ai, font=("Arial", 11))
entry.place(x=4, y=SH - 70, width=SW - 70, height=34)

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg, ast.UAdd: op.pos}


def ev(n):
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
        return n.value
    if isinstance(n, ast.BinOp):
        if isinstance(n.op, ast.Pow):
            b, e = ev(n.left), ev(n.right)
            if abs(e) > 1000:
                raise ValueError
            return b ** e
        return OPS[type(n.op)](ev(n.left), ev(n.right))
    if isinstance(n, ast.UnaryOp):
        return OPS[type(n.op)](ev(n.operand))
    raise ValueError


def calc(s):
    s = s.replace("x", "*").replace("\u00d7", "*").replace("\u00f7", "/").replace("^", "**")
    try:
        return ev(ast.parse(s.strip(), mode="eval").body)
    except Exception:
        return None


JOKES = ["Why was the math book sad? It had too many problems.",
         "Why did the circle get an A? It was well-rounded.",
         "Why did the bird fail the test? It kept flapping."]


def reply(q):
    s = q.lower()
    if "my name" in s or "who am i" in s:
        n = data.get("name", "")
        return f"Your name is {n}!" if n else "I don't know your name yet. Open Settings, save it, then ask me again."
    if any(w in s for w in ("my address", "home address", "where do i live", "where i live")):
        a = data.get("addr", "")
        return f"Your address is:\n{a}" if a else "I don't have your address yet. Open Settings, save it, then ask me again."
    if s and all(ch in "0123456789+-*/^().x\u00d7\u00f7 " for ch in s) and any(ch in s for ch in "+-*/^x\u00d7\u00f7"):
        v = calc(s)
        if v is not None:
            return f"{q.strip()} = {fmt(v)}"
    if "time" in s:
        return "It's " + time.strftime("%I:%M %p").lstrip("0") + "."
    if "date" in s or "today" in s:
        return "Today is " + time.strftime("%A, %B %d") + "."
    if s.startswith(("hi", "hello", "hey")):
        return "Flap flap! What's up?"
    if "joke" in s:
        return random.choice(JOKES)
    if "name" in s or "who are you" in s:
        return "I'm Tiny AI, the bird in your phone."
    return "I'm a tiny offline bird: I can do math, the time, the date, jokes, and tell you your name and address."


def say(who, text):
    log.config(state="normal")
    log.insert("end", text + "\n\n", who)
    log.config(state="disabled")
    log.see("end")


def send(event=None):
    q = entry.get().strip()
    if q:
        entry.delete(0, "end")
        say("u", q)
        say("a", reply(q))


tk.Button(ai, text="Send", bg="#3b6df0", fg="white", bd=0, command=send).place(x=SW - 62, y=SH - 70, width=58, height=34)
entry.bind("<Return>", send)
say("a", "Hi! I'm Tiny AI. Ask me math, the time, or a joke.")

# ---------------- Math homework ----------------
mh = make("math", "#fff7e8")
R = random.randint
GENS = {
    "easy": [lambda: (lambda a, b: (f"{a} + {b}", a + b))(R(1, 20), R(1, 20)),
             lambda: (lambda a: (lambda b: (f"{a} - {b}", a - b))(R(1, a)))(R(5, 30)),
             lambda: (lambda a, b: (f"{a} x {b}", a * b))(R(2, 5), R(2, 5))],
    "medium": [lambda: (lambda a, b: (f"{a} x {b}", a * b))(R(3, 12), R(3, 12)),
               lambda: (lambda b, n: (f"{b * n} / {b}", n))(R(2, 12), R(2, 12)),
               lambda: (lambda a, b, c: (f"{a} x {b} + {c}", a * b + c))(R(2, 9), R(2, 9), R(1, 30)),
               lambda: (lambda a, b: (f"{a} + {b}", a + b))(R(40, 150), R(20, 90))],
    "hard": [lambda: (lambda a, b, c, d: (f"({a} + {b}) x {c} - {d}", (a + b) * c - d))(R(2, 9), R(2, 9), R(2, 9), R(1, 8)),
             lambda: (lambda x, a, b: (f"Solve for x:\n{a}x + {b} = {a * x + b}", x))(R(2, 15), R(2, 9), R(1, 20)),
             lambda: (lambda n: (f"{n} squared", n * n))(R(11, 25)),
             lambda: (lambda p, b: (f"{p}% of {b}", p * b // 100))([10, 15, 20, 25, 30, 40, 50, 75][R(0, 7)], 20 * R(2, 25))],
}
ms = {"lvl": "easy", "ans": 0, "done": True, "first": True, "wrong": False, "tried": 0, "right": 0, "streak": 0}
pick = tk.Frame(mh, bg="#fff7e8")
quiz = tk.Frame(mh, bg="#fff7e8")
for f in (pick, quiz):
    f.place(x=0, y=0, width=SW, height=SH - 24)
tk.Label(pick, text="Pick your level:", bg="#fff7e8", font=("Arial", 12, "bold")).pack(pady=14)
q_l = tk.Label(quiz, text="", bg="white", font=("Arial", 18, "bold"), wraplength=SW - 30, height=4)
q_l.pack(fill="x", padx=10, pady=(14, 8))
a_e = tk.Entry(quiz, font=("Arial", 18), justify="center")
a_e.pack(fill="x", padx=10)
fb_l = tk.Label(quiz, text="", bg="#fff7e8", font=("Arial", 11, "bold"))
fb_l.pack(pady=6)
sc_l = tk.Label(quiz, text="", bg="#fff7e8", fg="#6b5a2e")
sc_l.pack()


def score():
    sc_l.config(text=f'{ms["lvl"].title()}   Score {ms["right"]}/{ms["tried"]}   Streak {ms["streak"]}')


def nextq():
    q, a = random.choice(GENS[ms["lvl"]])()
    ms.update(ans=a, done=False, first=True, wrong=False)
    q_l.config(text=q)
    a_e.delete(0, "end")
    fb_l.config(text="")
    chk.config(text="Check")
    a_e.focus_set()


def check(event=None):
    if ms["done"]:
        nextq()
        return
    try:
        v = float(a_e.get().replace(",", "."))
    except ValueError:
        return
    if ms["first"]:
        ms["tried"] += 1
        ms["first"] = False
    if abs(v - ms["ans"]) < 1e-9:
        if not ms["wrong"]:
            ms["right"] += 1
            ms["streak"] += 1
        fb_l.config(text="Correct!", fg="#168a3a")
        ms["done"] = True
        chk.config(text="Next")
    else:
        ms["wrong"] = True
        ms["streak"] = 0
        fb_l.config(text="Not quite. Try again.", fg="#c0392b")
    score()


def reveal():
    if ms["done"]:
        return
    if ms["first"]:
        ms["tried"] += 1
        ms["first"] = False
    ms.update(streak=0, wrong=True, done=True)
    fb_l.config(text=f'Answer: {ms["ans"]}', fg="#c0392b")
    chk.config(text="Next")
    score()


chk = tk.Button(quiz, text="Check", bg="#27ae60", fg="white", bd=0, font=("Arial", 12, "bold"), command=check)
chk.pack(fill="x", padx=10, pady=4, ipady=6)
tk.Button(quiz, text="Show answer", bg="#eadcb8", bd=0, command=reveal).pack(fill="x", padx=10, pady=2, ipady=4)
tk.Button(quiz, text="Change level", bg="#fff7e8", bd=0, fg="#6b5a2e", command=lambda: pick.tkraise()).pack(pady=6)
a_e.bind("<Return>", check)


def start(level):
    ms.update(lvl=level, tried=0, right=0, streak=0)
    score()
    quiz.tkraise()
    nextq()


for level, color, desc in (("easy", "#27ae60", "small adding, subtracting"), ("medium", "#e67e22", "times tables, division"),
                           ("hard", "#c0392b", "brackets, equations, percents")):
    tk.Button(pick, text=f"{level.title()}\n{desc}", bg=color, fg="white", bd=0, font=("Arial", 11, "bold"),
              command=lambda l=level: start(l)).pack(fill="x", padx=14, pady=6, ipady=10)
pick.tkraise()

# ---------------- Phone (calls) ----------------
ph = make("phone", "#f4f6fa")
tk.Label(ph, text="Contacts", bg="#f4f6fa", font=("Arial", 13, "bold")).pack(pady=(14, 8))
call_msg = tk.Label(ph, text="Tap a contact to call", bg="#f4f6fa", fg="#333", wraplength=SW - 24,
                    font=("Arial", 11), height=5)


def call(n):
    call_msg.config(text=f"Calling {n}...")
    ph.after(900, lambda: call_msg.config(text=f'{n}:\n"Hello! I can\'t call right now. I will call you later."'))


for n in ("Mom", "Dad", "Brother"):
    tk.Button(ph, text="Call " + n, bg="#34c759", fg="white", bd=0, font=("Arial", 12, "bold"),
              command=lambda n=n: call(n)).pack(fill="x", padx=14, pady=5, ipady=8)
call_msg.pack(pady=14)

# ---------------- Flappy ----------------
FH, FGAP = SH - 24, 112
fl = make("flappy", "#70c5ce")
fc = tk.Canvas(fl, width=SW, height=FH, bg="#70c5ce", highlightthickness=0)
fc.pack()
fs = {"y": 160.0, "v": 0.0, "pipes": [], "score": 0, "state": "ready", "f": 0, "best": 0}


def f_flap(e=None):
    if fs["state"] == "dead":
        fs.update(y=160.0, v=0.0, pipes=[], score=0, state="ready", f=0)
        return
    fs["state"], fs["v"] = "play", -6.0


def f_tick():
    s = fs
    s["f"] += 1
    if s["state"] == "play":
        s["v"] += 0.33
        s["y"] += s["v"]
        if s["f"] % 75 == 1:
            s["pipes"].append([SW, R(50, FH - 40 - FGAP - 50), False])
        for p in s["pipes"]:
            p[0] -= 2.2
            if not p[2] and p[0] + 40 < 50:
                p[2] = True
                s["score"] += 1
            if p[0] < 70 and p[0] + 40 > 50 and (s["y"] - 10 < p[1] or s["y"] + 10 > p[1] + FGAP):
                s["state"] = "dead"
        s["pipes"] = [p for p in s["pipes"] if p[0] > -45]
        if s["y"] + 10 > FH - 40 or s["y"] < -10:
            s["state"] = "dead"
        s["best"] = max(s["best"], s["score"])
    c = fc
    c.delete("all")
    for x, top, _ in s["pipes"]:
        c.create_rectangle(x, -2, x + 40, top, fill="#3f9b4a", outline="#2d7a37", width=2)
        c.create_rectangle(x, top + FGAP, x + 40, FH, fill="#3f9b4a", outline="#2d7a37", width=2)
    c.create_rectangle(0, FH - 40, SW, FH, fill="#d9c585", width=0)
    y = s["y"] + (4 * ((s["f"] // 8) % 2) if s["state"] == "ready" else 0)
    c.create_oval(50, y - 10, 70, y + 10, fill="#f5b82e", outline=OUT, width=2)
    c.create_oval(60, y - 8, 67, y - 1, fill="white", outline=OUT)
    c.create_polygon(69, y - 1, 79, y + 2, 69, y + 5, fill="#e8892b", outline=OUT)
    if s["state"] != "ready":
        c.create_text(SW // 2, 36, text=str(s["score"]), font=("Arial", 26, "bold"), fill="white")
    if s["state"] == "ready":
        c.create_text(SW // 2, 100, text="Tap to flap", font=("Arial", 14, "bold"), fill="white")
    if s["state"] == "dead":
        c.create_text(SW // 2, 100, text=f'Game over\nBest {s["best"]}\nTap to retry', font=("Arial", 14, "bold"), fill="white")


fc.bind("<Button-1>", f_flap)

# ---------------- Blocks (build with blocks) ----------------
bl = make("blocks", "#87ceeb")
COLS = 11
CELL = SW // COLS
ROWS = (FH - 44) // CELL
BT = {"grass": "#5aa832", "dirt": "#8b5a2b", "stone": "#8a8a8a", "wood": "#a0702e", "leaf": "#2f7d32", "erase": None}
sel = ["stone"]
grid = [[None] * COLS for _ in range(ROWS)]
for c_ in range(COLS):
    grid[ROWS - 3][c_] = "grass"
    grid[ROWS - 2][c_] = grid[ROWS - 1][c_] = "dirt"
bc = tk.Canvas(bl, width=SW, height=ROWS * CELL, bg="#87ceeb", highlightthickness=0)
bc.pack()


def b_draw():
    bc.delete("all")
    for r_ in range(ROWS):
        for c_ in range(COLS):
            t = grid[r_][c_]
            if t:
                bc.create_rectangle(c_ * CELL, r_ * CELL, (c_ + 1) * CELL, (r_ + 1) * CELL, fill=BT[t], outline="#3a3a3a")


def b_click(e, erase=False):
    c_, r_ = e.x // CELL, e.y // CELL
    if 0 <= r_ < ROWS and 0 <= c_ < COLS:
        grid[r_][c_] = None if erase or sel[0] == "erase" else sel[0]
        b_draw()


bc.bind("<Button-1>", b_click)
bc.bind("<B1-Motion>", b_click)
bc.bind("<Button-3>", lambda e: b_click(e, True))
pal = tk.Frame(bl, bg="#87ceeb")
pal.pack(fill="x", pady=4)
for name, col in BT.items():
    tk.Button(pal, text="x" if name == "erase" else "", bg=col or "white", width=3, height=1, relief="raised",
              command=lambda n=name: sel.__setitem__(0, n)).pack(side="left", padx=2)
b_draw()

# ---------------- Obby (jump over the lava) ----------------
GY = FH - 110
ob = make("obby", "#9bd7ff")
oc = tk.Canvas(ob, width=SW, height=FH, bg="#9bd7ff", highlightthickness=0)
oc.pack()
os_ = {}


def o_gen():
    segs = os_["segs"]
    while segs[-1][1] < os_["x"] + SW + 250:
        a_ = segs[-1][1] + R(40, 64)
        segs.append([a_, a_ + R(90, 200)])


def o_reset():
    os_.update(x=0.0, y=GY - 16.0, vy=0.0, ground=True, segs=[[-100, 300]], state="ready")
    o_gen()


def o_jump(e=None):
    if os_["state"] == "dead":
        o_reset()
        return
    os_["state"] = "play"
    if os_["ground"]:
        os_["vy"], os_["ground"] = -7.2, False


def o_tick():
    s = os_
    if s["state"] == "play":
        s["x"] += 2.4
        s["vy"] += 0.4
        old = s["y"]
        s["y"] += s["vy"]
        s["ground"] = False
        for a_, b_ in s["segs"]:
            if a_ - 4 < s["x"] < b_ + 4 and old + 16 <= GY + 2 and s["y"] + 16 >= GY:
                s["y"], s["vy"], s["ground"] = GY - 16.0, 0.0, True
        if s["y"] > FH:
            s["state"] = "dead"
        o_gen()
        s["segs"] = [g for g in s["segs"] if g[1] > s["x"] - 200]
    cam = s["x"] - 60
    c = oc
    c.delete("all")
    c.create_rectangle(0, GY + 4, SW, FH, fill="#ff4d2e", width=0)
    for a_, b_ in s["segs"]:
        c.create_rectangle(a_ - cam, GY, b_ - cam, FH, fill="#8b5a2b", outline="#5c3a1a")
        c.create_rectangle(a_ - cam, GY, b_ - cam, GY + 8, fill="#5aa832", outline="#3d7a22")
    y = s["y"]
    c.create_rectangle(52, y, 68, y + 16, fill="#ff9f0a", outline=OUT, width=2)
    c.create_rectangle(58, y + 4, 61, y + 7, fill="black")
    c.create_rectangle(64, y + 4, 67, y + 7, fill="black")
    c.create_text(SW // 2, 24, text=f"{int(s['x'] // 20)} m", font=("Arial", 16, "bold"), fill="#1c1c24")
    if s["state"] == "ready":
        c.create_text(SW // 2, 90, text="Tap to jump\nDon't fall in the lava!", font=("Arial", 12, "bold"), fill="#1c1c24")
    if s["state"] == "dead":
        c.create_text(SW // 2, 90, text=f"Game over: {int(s['x'] // 20)} m\nTap to retry", font=("Arial", 13, "bold"), fill="#1c1c24")


oc.bind("<Button-1>", o_jump)
o_reset()

GAMES = {"flappy": f_tick, "obby": o_tick}


def loop():
    t = GAMES.get(current[0])
    if t:
        t()
    root.after(16, loop)


loop()

# ---------------- Settings ----------------
se = make("set", "#f4f6fa")
tk.Label(se, text="Your name", bg="#f4f6fa", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(14, 4))
name_e = tk.Entry(se, font=("Arial", 11))
name_e.pack(fill="x", padx=10)
name_e.insert(0, data.get("name", ""))
tk.Label(se, text="Home address", bg="#f4f6fa", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
addr = tk.Text(se, height=3, width=24, font=("Arial", 11), wrap="word")
addr.pack(padx=10)
addr.insert("1.0", data.get("addr", ""))
saved = tk.Label(se, text="", bg="#f4f6fa", fg="#168a3a")


def save_all():
    data["name"] = name_e.get().strip()
    data["addr"] = addr.get("1.0", "end").strip()
    save()
    saved.config(text="Saved!" if data["name"] or data["addr"] else "Cleared.")


tk.Button(se, text="Save", bg="#3b6df0", fg="white", bd=0, command=save_all).pack(fill="x", padx=10, pady=8, ipady=6)
saved.pack()
tk.Label(se, text="Stays on this computer.\nTiny AI tells them to you if you ask.", bg="#f4f6fa", fg="#6b7280",
         font=("Arial", 9)).pack(pady=8)


def on_key(e):
    if e.keysym == "space" and current[0] in ("flappy", "obby"):
        (f_flap if current[0] == "flappy" else o_jump)()
        return
    if current[0] != "calc":
        return
    m = {"Return": "=", "equal": "=", "BackSpace": "<", "Escape": "C", "asterisk": "x", "slash": "/",
         "minus": "-", "plus": "+", "period": "."}
    k = m.get(e.keysym) or (e.char if e.char.isdigit() else None)
    if k:
        key(k)


root.bind("<Key>", on_key)
show("home")
root.mainloop()
