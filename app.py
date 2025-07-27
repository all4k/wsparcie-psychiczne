from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-fallback-key")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    historia = session.get("historia", [])
    return render_template("chat.html", historia=historia)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"response": "Wiadomość była pusta."})

    if "historia" not in session:
        session["historia"] = []

    historia = session["historia"]

    # Dodaj wiadomość użytkownika
    historia.append({
        "czas": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "wiadomosc": message,
        "autor": "user"
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Jesteś wspierającym asystentem psychologicznym."},
                {"role": "user", "content": message}
            ]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = "Wystąpił błąd podczas generowania odpowiedzi."

    # Dodaj wiadomość AI
    historia.append({
        "czas": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "wiadomosc": answer,
        "autor": "AI"
    })

    session["historia"] = historia[-10:]  # zachowaj tylko ostatnie 10 wiadomości

    return jsonify({"response": answer})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("login")
        return redirect("/chat")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

