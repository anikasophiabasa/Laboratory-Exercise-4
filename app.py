import json
import math
import os
import re
import smtplib
from datetime import datetime
from email.message import EmailMessage

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from linkedlist import LinkedList
from stack import Stack          # linked-list stack made of Nodes (stack.py)

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# =====================================================================
#  ✏️  EDIT THIS SECTION — put your own personal data here.
#  Every page (profile, contact, home, footer) reads from these values.
# =====================================================================
PROFILE = {
    "name": "Anika Sophia C. Basa",
    "first_name": "Anika",
    "initials": "AB",
    "intro": "I love solving problems, building things, and finding inspiration in music.",
    "roles": ["Computer Engineering Student", "Python Developer", "Problem Solver", "Musician & Gamer"],
    "about": (
        "I'm a 2nd year Computer Engineering student at the Polytechnic University of the Philippines. "
        "I love turning tricky problems into clean, working solutions, whether that's a Python program, "
        "a web page, or a data structure. Outside of code, I'm usually singing, dancing, playing an "
        "instrument, or gaming. I believe creativity and logic work best together."
    ),
    # --- player card (home page) ---
    "level": 2,
    "player_class": "Computer Engineer in training",
    "main_quest": "Finish Data Structures & Algorithms",
    "side_quest": "Learn a new song on guitar",
    "section": "BSCPE 2-3",
    "course": "Bachelor of Science in Computer Engineering",
    "year": "2nd Year",
    "school": "Polytechnic University of the Philippines",
    "subject": "Data Structures and Algorithms",
    "motto": "Problems are not stop signs, they are guidelines.",
    "sayings": [
        ("Problems are not stop signs, they are guidelines.", "Robert H. Schuller"),
        ("Talk is cheap. Show me the code.", "Linus Torvalds"),
        ("The best way to predict the future is to invent it.", "Alan Kay"),
    ],
    "skills": [
        ("HTML & CSS", 90),
        ("Python", 80),
        ("C / C++", 70),
        ("Git & GitHub", 70),
        ("Arduino & Microcontrollers", 60),
    ],
    "interests": ["Gaming 🎮", "Music 🎵", "Singing 🎤", "Playing Instruments 🎸"],
    "timeline": [
        ("2026", "Learning Data Structures & Algorithms",
         "Building linked lists and more, and turning this Flask lab into my own personal portfolio."),
        ("2025", "Started Computer Engineering at PUP",
         "Began my BS Computer Engineering journey at the Polytechnic University of the Philippines."),
        ("Always", "Creative at heart",
         "Singing, dancing and playing instruments keep me balanced and inspire the way I solve problems."),
    ],
    # Contact
    "email": "anikasophia.cabigbasa@gmail.com",
    "phone": "0968 523 0711",
    "location": "Cainta, Rizal, Philippines",
    "socials": [
        ("GitHub", "https://github.com/anikasophiabasa", "github"),
        ("Facebook", "https://www.facebook.com/anikasophia.cabigbasa", "facebook"),
    ],
}

WORKS = [
    {"title": "toUpperCase", "desc": "Turn any text into UPPERCASE instantly.",
     "url": "works", "icon": "Aa", "tag": "Strings"},
    {"title": "Area of a Circle", "desc": "Enter a radius, get area, diameter & circumference.",
     "url": "acircle", "icon": "◯", "tag": "Math"},
    {"title": "Area of a Triangle", "desc": "Use base × height or the three sides (Heron's formula).",
     "url": "atriangle", "icon": "△", "tag": "Math"},
    {"title": "Linked List", "desc": "An interactive, animated singly linked list.",
     "url": "linkedlist_page", "icon": "⛓", "tag": "Data Structures"},
    {"title": "Infix to Postfix", "desc": "Convert an expression to postfix using a stack made of linked-list nodes.",
     "url": "infixtopostfix", "icon": "⇄", "tag": "Data Structures"},
]


@app.context_processor
def inject_globals():
    photo = os.path.exists(os.path.join(app.static_folder, "images", "profile.jpg"))
    return {"me": PROFILE, "works_list": WORKS, "has_photo": photo, "year": datetime.now().year}


# ------------------------------- pages -------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")



# --------------------------- contact form → email ---------------------------
# Every message is ALWAYS saved to messages.jsonl (a file next to app.py).
# If you also want each message emailed to you, set these 3 environment variables
# before running the app (see the readme):
#     MAIL_USER  = your Gmail address
#     MAIL_PASS  = a Gmail "App Password" (NOT your normal password)
#     MAIL_TO    = where to send the messages (optional, defaults to MAIL_USER)
def send_email(entry):
    user, password = os.environ.get("MAIL_USER"), os.environ.get("MAIL_PASS")
    if not user or not password:
        return False                      # email not set up -> just keep the saved copy
    try:
        msg = EmailMessage()
        msg["Subject"] = "Portfolio message from " + entry["name"]
        msg["From"] = user
        msg["To"] = os.environ.get("MAIL_TO", user)
        msg["Reply-To"] = entry["email"]  # so you can just hit "Reply"
        msg.set_content(f"Name: {entry['name']}\nEmail: {entry['email']}\nTime: {entry['time']}\n\n{entry['message']}")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(user, password)
            server.send_message(msg)
        return True
    except Exception as err:              # wrong password, no internet, bad email, etc.
        print("Email failed:", err)
        return False

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        entry = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "message": request.form.get("message", "").strip(),
        }
        if entry["name"] and entry["email"] and entry["message"]:
            with open("messages.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            if send_email(entry):
                flash("Thanks for reaching out! Your message was sent to my email.", "success")
            else:
                flash("Thanks for reaching out! Your message has been saved.", "success")
        else:
            flash("Please fill in all the fields.", "error")
        return redirect(url_for("contact") + "#form")
    return render_template("contact.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


# --------------------------- programming works ---------------------------
@app.route("/works", methods=["GET", "POST"])
def works():
    result, text = None, ""
    if request.method == "POST":
        text = request.form.get("inputString", "")
        result = text.upper()
    return render_template("touppercase.html", result=result, text=text)


@app.route("/works/area/circle", methods=["GET", "POST"])
def acircle():
    data, error, radius = None, None, ""
    if request.method == "POST":
        radius = request.form.get("radius", "").strip()
        try:
            r = float(radius)
            if r < 0 or not math.isfinite(r):
                raise ValueError
            data = {"area": math.pi * r * r, "diameter": 2 * r, "circumference": 2 * math.pi * r}
        except ValueError:
            error = "Please enter a valid, non-negative number for the radius."
    return render_template("circle.html", data=data, error=error, radius=radius)


@app.route("/works/area/triangle", methods=["GET", "POST"])
def atriangle():
    data, error, mode = None, None, request.form.get("mode", "bh")
    form = request.form
    if request.method == "POST":
        try:
            if mode == "bh":
                b, h = float(form.get("base", "")), float(form.get("height", ""))
                if b < 0 or h < 0:
                    raise ValueError("Base and height must not be negative.")
                data = {"area": 0.5 * b * h, "formula": f"½ × {b:g} × {h:g}"}
            else:
                a, b, c = (float(form.get(k, "")) for k in ("side_a", "side_b", "side_c"))
                if min(a, b, c) <= 0:
                    raise ValueError("All sides must be greater than zero.")
                if a + b <= c or a + c <= b or b + c <= a:
                    raise ValueError("Those sides can't form a triangle (triangle inequality).")
                s = (a + b + c) / 2
                data = {"area": math.sqrt(s * (s - a) * (s - b) * (s - c)),
                        "formula": f"√[s(s−a)(s−b)(s−c)], s = {s:g}", "perimeter": a + b + c}
        except ValueError as e:
            msg = str(e)
            error = msg if "must" in msg or "can't" in msg else "Please enter valid numbers in every field."
    return render_template("triangle.html", data=data, error=error, mode=mode, form=form)


# --------------------------- infix → postfix (stack) ---------------------------
# The stack is the linked-list Stack from stack.py (every item is a Node).
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "^": 3}
TOKEN_RE = re.compile(r"\s*(\d+\.\d+|[A-Za-z0-9]+|\S)")
OPERAND_RE = re.compile(r"\d+\.\d+|[A-Za-z0-9]+")
NUMBER_RE = re.compile(r"\d+(\.\d+)?")


def stack_to_list(stack):
    """Walk the nodes from top to bottom and return their data as a list."""
    items = []
    current = stack.top
    while current:
        items.append(current.data)
        current = current.next
    return items


def infix_to_postfix(expression):
    """Return (postfix_string, steps). Raises ValueError if the expression is not valid."""
    if len(expression) > 200:
        raise ValueError("That expression is too long (200 characters max).")
    tokens = TOKEN_RE.findall(expression)
    if not tokens:
        raise ValueError("Please type an infix expression first, like A+B*C.")

    stack = Stack()
    output = []
    steps = []
    expect_operand = True          # True when the next token must be a value or "("

    def record(token, action):
        steps.append({"token": token, "action": action,
                      "stack": stack_to_list(stack), "output": " ".join(output)})

    for tok in tokens:
        if OPERAND_RE.fullmatch(tok):                      # operand (A, b, 12, 3.5, x1 ...)
            if not expect_operand:
                raise ValueError(f"Two values in a row near '{tok}'. Is an operator missing?")
            output.append(tok)
            expect_operand = False
            record(tok, "Operand → goes straight to the output")

        elif tok == "(":
            if not expect_operand:
                raise ValueError("An operator is missing before '('.")
            stack.push(tok)
            record(tok, "Push '(' onto the stack")

        elif tok == ")":
            if expect_operand:
                raise ValueError("Something is missing before ')'.")
            popped = []
            while stack.peek() is not None and stack.peek() != "(":
                item = stack.pop()
                output.append(item)
                popped.append(item)
            if stack.peek() != "(":
                raise ValueError("Mismatched parentheses: a ')' has no matching '('.")
            stack.pop()                                    # throw away the "("
            moved = ", ".join(popped) if popped else "nothing"
            record(tok, f"Pop {moved} to the output until '(' , then remove '('")

        elif tok in PRECEDENCE:
            if expect_operand:
                raise ValueError(f"The operator '{tok}' needs a value before it.")
            popped = []
            while True:
                top = stack.peek()
                if top is None or top == "(":
                    break
                same = PRECEDENCE[top] == PRECEDENCE[tok]
                # pop higher precedence, or equal precedence (except ^ which goes right-to-left)
                if PRECEDENCE[top] > PRECEDENCE[tok] or (same and tok != "^"):
                    item = stack.pop()
                    output.append(item)
                    popped.append(item)
                else:
                    break
            stack.push(tok)
            expect_operand = True
            action = f"Push '{tok}'"
            if popped:
                action = f"Pop {', '.join(popped)} to the output first, then push '{tok}'"
            record(tok, action)

        else:
            raise ValueError(f"'{tok}' is not allowed. Use letters, numbers, + - * / % ^ and ( ).")

    if expect_operand:
        raise ValueError("The expression ends too early. A value is missing at the end.")

    while stack.peek() is not None:                        # empty the stack at the end
        item = stack.pop()
        if item == "(":
            raise ValueError("Mismatched parentheses: a '(' was never closed.")
        output.append(item)
        record("end", f"No more tokens → pop '{item}' to the output")

    joiner = "" if all(len(x) == 1 for x in output) else " "
    return joiner.join(output), steps, output


def evaluate_postfix(tokens):
    """Evaluate postfix tokens with the same linked-list Stack.
    Returns (value, steps). Only works when every operand is a number."""
    stack = Stack()
    steps = []

    def record(token, action):
        steps.append({"token": token, "action": action, "stack": stack_to_list(stack)})

    def show(n):
        return f"{n:.10g}" if isinstance(n, float) else str(n)

    for tok in tokens:
        if NUMBER_RE.fullmatch(tok):
            stack.push(float(tok) if "." in tok else int(tok))
            record(tok, f"Number → push {tok}")
        else:
            b = stack.pop()                                # the top is the RIGHT side
            a = stack.pop()
            try:
                if tok == "+":
                    r = a + b
                elif tok == "-":
                    r = a - b
                elif tok == "*":
                    r = a * b
                elif tok == "/":
                    r = a / b
                elif tok == "%":
                    r = a % b
                else:                                      # "^"
                    if abs(b) > 1000:
                        raise OverflowError
                    r = a ** b
                if isinstance(r, complex) or abs(r) > 1e300:
                    raise OverflowError
            except ZeroDivisionError:
                raise ValueError("Can't divide by zero, so this expression has no value.")
            except OverflowError:
                raise ValueError("That calculation is too big (or not a real number), so there is no value.")
            stack.push(r)
            record(tok, f"Pop {show(b)} and {show(a)}, calculate {show(a)} {tok} {show(b)} = {show(r)}, push {show(r)}")
    return stack.pop(), steps


@app.route("/works/infixtopostfix", methods=["GET", "POST"])
def infixtopostfix():
    expression, postfix, steps, error = "", None, [], None
    value, eval_steps, value_note = None, [], None
    if request.method == "POST":
        expression = request.form.get("infix", "").strip()
        try:
            postfix, steps, tokens = infix_to_postfix(expression)
            if all(t in PRECEDENCE or NUMBER_RE.fullmatch(t) for t in tokens):   # only numbers + operators
                try:
                    value, eval_steps = evaluate_postfix(tokens)
                except ValueError as e:
                    value_note = str(e)
            else:
                value_note = "This expression has letters, so there is no number to calculate. Try numbers like 3+4*2."
        except ValueError as e:
            error = str(e)
    if isinstance(value, float):
        value = f"{value:.10g}"
    return render_template("infixtopostfix.html", expression=expression, postfix=postfix, steps=steps,
                           error=error, value=value, eval_steps=eval_steps, value_note=value_note)


# ------------------------------ linked list ------------------------------
ll = LinkedList()
for v in ("Flask", "Python", "Portfolio"):
    ll.insert_tail(v)


def _snapshot(message, highlight=None, ok=True):
    return jsonify({"ok": ok, "message": message, "nodes": ll.to_list(),
                    "size": ll.size, "highlight": highlight})


@app.route("/works/linkedlist")
def linkedlist_page():
    return render_template("linkedlist.html")


@app.route("/api/linkedlist", methods=["GET"])
def ll_state():
    return _snapshot("Linked list loaded.")


@app.route("/api/linkedlist/<op>", methods=["POST"])
def ll_op(op):
    body = request.get_json(silent=True) or {}
    value = str(body.get("value", "")).strip()
    raw_index = body.get("index", "")
    try:
        needs_value = {"insert_head", "insert_tail", "insert_at", "delete_value", "search"}
        if op in needs_value and not value:
            raise ValueError("Please enter a value.")
        if op in {"insert_at", "delete_at"}:
            try:
                index = int(raw_index)
            except (TypeError, ValueError):
                raise ValueError("Please enter a whole number for the index.")

        if op == "insert_head":
            i = ll.insert_head(value); return _snapshot(f'Inserted "{value}" at the head.', i)
        if op == "insert_tail":
            i = ll.insert_tail(value); return _snapshot(f'Inserted "{value}" at the tail.', i)
        if op == "insert_at":
            i = ll.insert_at(index, value); return _snapshot(f'Inserted "{value}" at index {i}.', i)
        if op == "delete_head":
            v = ll.delete_at(0); return _snapshot(f'Deleted head node "{v}".')
        if op == "delete_tail":
            v = ll.delete_at(ll.size - 1) if ll.size else ll.delete_at(0)
            return _snapshot(f'Deleted tail node "{v}".')
        if op == "delete_at":
            v = ll.delete_at(index); return _snapshot(f'Deleted "{v}" at index {index}.')
        if op == "delete_value":
            i = ll.delete_value(value); return _snapshot(f'Deleted "{value}" (was at index {i}).')
        if op == "search":
            i = ll.search(value)
            if i == -1:
                return _snapshot(f'"{value}" was not found.', None, ok=False)
            return _snapshot(f'Found "{value}" at index {i}.', i)
        if op == "reverse":
            ll.reverse(); return _snapshot("List reversed.")
        if op == "clear":
            ll.clear(); return _snapshot("List cleared.")
        return _snapshot("Unknown operation.", None, ok=False)
    except (ValueError, IndexError) as e:
        return _snapshot(str(e), None, ok=False)


if __name__ == "__main__":
    app.run(debug=True)
