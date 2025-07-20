from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import random
import traceback
from datetime import datetime
from functools import wraps
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'tajny_klucz_123'  # zmień na coś bezpiecznego w produkcji

# OpenAI client (zgodny z openai>=1.0.0)
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
    try:
        data = request.get_json()
        message = data.get("message", "")
        is_crisis = any(keyword in message.lower() for keyword in CRISIS_KEYWORDS)

        if is_crisis:
            selected_technique = random.choice(DBT_TECHNIQUES)
            system_prompt = (
                "Jesteś empatycznym psychologiem. "
                "Użytkownik może być w kryzysie. "
                "Zaoferuj wsparcie i zachęć do kontaktu z profesjonalistą.\n\n"
                f"Technika DBT: {selected_technique}"
            )
        else:
            system_prompt = "Jesteś wspierającym asystentem psychologicznym."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content.strip()

        # Zapisz do sesji
        if "historia" not in session:
            session["historia"] = []

        session["historia"].append({
            "czas": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "user": message,
            "ai": ai_response
        })

        return jsonify({"response": ai_response})

    except Exception as e:
        print("BŁĄD W CZACIE:")
        traceback.print_exc()
        return jsonify({"error": "Wystąpił błąd na serwerze."}), 500

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

