from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
load_dotenv()
import json
from datetime import datetime
from functools import wraps
import traceback
import random
import time

app = Flask(__name__)
app.jinja_env.cache = {}

app.secret_key = 'tajny_klucz_123'  # zmień na bezpieczny

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CRISIS_KEYWORDS = [
    "nie chce mi się żyć", "mam dość", "samobójstwo", "koniec", "zrezygnowany", "chcę umrzeć"
]

DBT_TECHNIQUES = [
    "Weź kilka głębokich oddechów i skup się na tym, jak powietrze wchodzi i wychodzi z Twojego ciała.",
    "Zanurz twarz w zimnej wodzie lub schłodź kark – technika TIPP.",
    "Skieruj uwagę na otoczenie: co widzisz, słyszysz, czujesz? Nazwij 5 rzeczy.",
    "Napnij i rozluźnij mięśnie – ćwiczenie z regulacji emocji.",
]

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
@login_required
def chat():
    historia = session.get("historia", [])
    return render_template("chat.html", historia=historia)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    message = data.get("message", "")

    if "historia" not in session:
        session["historia"] = []

    historia = session["historia"]
    system_prompt = "Jesteś wspierającym asystentem psychologicznym."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print("Błąd w API:", e)
        answer = "Wystąpił błąd podczas generowania odpowiedzi."

    historia.append({
        "czas": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user": message,
        "ai": answer
    })
    session["historia"] = historia

    return jsonify({"response": answer})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("login")
        return redirect("/chat")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("historia", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

