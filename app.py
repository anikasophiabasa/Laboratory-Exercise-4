import json
import math
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

import linkedlist                # linked list class + button logic (linkedlist.py)
import queue_dequeue             # queue class + button logic (queue_dequeue.py)
from infix_postfix import PRECEDENCE, NUMBER_RE, evaluate_postfix, infix_to_postfix   # (infix_postfix.py)

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
    "intro": "I love solving problems, building things, and making music.",
    "tagline": "Computer Engineering student who loves solving problems, building things, and making music",
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
    {"title": "Queue", "desc": "Enqueue and dequeue in a first-in, first-out line made of linked-list nodes.",
     "url": "queue_page", "icon": "⇉", "tag": "Data Structures"},
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
# The conversion code (infix_to_postfix, evaluate_postfix) lives in infix_postfix.py
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
# The LinkedList class and the code that runs each button live in linkedlist.py
ll = linkedlist.create_demo_list()


@app.route("/works/linkedlist")
def linkedlist_page():
    return render_template("linkedlist.html")


@app.route("/api/linkedlist", methods=["GET"])
def ll_state():
    return jsonify(linkedlist.snapshot(ll, "Linked list loaded."))


@app.route("/api/linkedlist/<op>", methods=["POST"])
def ll_op(op):
    body = request.get_json(silent=True) or {}
    return jsonify(linkedlist.run_operation(ll, op, body.get("value", ""), body.get("index", "")))


# ------------------------------ queue ------------------------------
# The Queue class (enqueue / dequeue) and the code that runs each button live in queue_dequeue.py
q = queue_dequeue.create_demo_queue()


@app.route("/works/queue")
def queue_page():
    return render_template("queue.html")


@app.route("/api/queue", methods=["GET"])
def queue_state():
    return jsonify(queue_dequeue.snapshot(q, "Queue loaded."))


@app.route("/api/queue/<op>", methods=["POST"])
def queue_op(op):
    body = request.get_json(silent=True) or {}
    return jsonify(queue_dequeue.run_operation(q, op, body.get("value", "")))


if __name__ == "__main__":
    app.run(debug=True)
