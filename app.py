
from flask import Flask, render_template, request, jsonify, redirect
from functools import wraps
from flask import session, redirect, url_for
import os
import json
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import random
from openai import OpenAI
app = Flask(__name__)
app.secret_key = 'tajny_klucz_123'  # ważne: zmień na bezpieczny

def czy_ukryc_tresc(tresc):
    tresc_niska = tresc.lower()
    niepokojace_slowa = [
        "powiesić", "zabić się", "koniec ze mną", "nie chce żyć", "samobójstwo", "mam dość życia"
    ]
    return any(slowo in tresc_niska for slowo in niepokojace_slowa)

USERS_FILE = "data/uzytkownicy.json"
FORUM_FILE = "data/forum.json"  # ← TUTAJ
HISTORIA_CZATU_PATH = "data/historia_czatu.json"

# Dekorator: wymaga zalogowania
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Lista słów kluczowych dla sytuacji kryzysowej
CRISIS_KEYWORDS = [
    "nie chce mi się żyć", "mam dość", "samobójstwo", "koniec", "zrezygnowany", "chcę umrzeć"
]

# Techniki DBT
DBT_TECHNIQUES = [
    "Weź kilka głębokich oddechów i skup się na tym, jak powietrze wchodzi i wychodzi z Twojego ciała.",
    "Spróbuj zanurzyć twarz w zimnej wodzie lub ochłodzić kark – to technika TIPP z DBT.",
    "Skieruj uwagę na otoczenie: co widzisz, słyszysz, czujesz? Nazwij 5 rzeczy zmysłowych.",
    "Spróbuj napiąć i rozluźnić mięśnie – to ćwiczenie z regulacji emocji.",
]

# Historia czatu
HISTORIA_CZATU_PATH = "historia_czatu.json"

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/chat")
@login_required
def chat():
    HISTORIA_PLIK = "data/chat_historia.json"
    try:
        with open(HISTORIA_PLIK, "r") as f:
            historia = json.load(f)
    except FileNotFoundError:
        historia = []
    return render_template("chat.html", historia=historia)

    if request.method == "POST":
        wiadomosc = request.json.get("wiadomosc")
        autor = session.get("user", "anonim")
        data = datetime.now().strftime("%Y-%m-%d %H:%M")

        historia.append({"autor": autor, "data": data, "wiadomosc": wiadomosc})

        # Odpowiedź AI
        try:
            odpowiedz = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Jesteś empatycznym terapeutą."},
                    {"role": "user", "content": wiadomosc}
                ]
            )
            odpowiedz_ai = odpowiedz.choices[0].message.content.strip()

        except Exception as e:
            odpowiedz_ai = "Przepraszam, wystąpił problem z odpowiedzią AI."

        historia.append({"autor": "AI", "data": data, "wiadomosc": odpowiedz_ai})

        with open(HISTORIA_PLIK, "w") as f:
            json.dump(historia, f, indent=2, ensure_ascii=False)

        return redirect("/chat")

    # Zwróć historię do szablonu przy GET
    return render_template("chat.html", historia=historia)


@app.route("/cwiczenie-oddechowe")
@login_required
def cwiczenie_oddechowe():
    return render_template("cwiczenie-oddechowe.html")



@app.route('/historia')
def historia():
    if os.path.exists(HISTORIA_CZATU_PATH):
        with open(HISTORIA_CZATU_PATH, "r") as f:
            historia = json.load(f)
    else:
        historia = []
    return render_template("historia_czatu.html", historia=historia[::-1])


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get("message", "")
    is_crisis = any(keyword in message.lower() for keyword in CRISIS_KEYWORDS)

    if is_crisis:
        selected_technique = random.choice(DBT_TECHNIQUES)
        system_prompt = (
            "Zachowuj się jak bardzo empatyczny i spokojny psycholog. "
            "Użytkownik może być w sytuacji kryzysowej. "
            "Nie dawaj gotowych rozwiązań, tylko zachęć do kontaktu z profesjonalistą, "
            "pokaż troskę i zapytaj, czy potrzebuje pomocy. "
            f"Oto propozycja techniki DBT, która może pomóc:\n\n{selected_technique}\n\n"
            "Na końcu zapytaj łagodnie: 'Czy chciałbyś, żebym pokazał Ci coś, co możesz spróbować zrobić teraz?'"
        )
    else:
        system_prompt = (
            "Jesteś wspierającym asystentem psychologicznym. "
            "Pomóż użytkownikowi zrozumieć swoje emocje i zachęć do dbania o siebie. "
            "Bądź empatyczny i spokojny."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content

        # zapis do historii czatu
        wpis = {
            "czas": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "uzytkownik": message,
            "asystent": ai_response
        }
        if os.path.exists(HISTORIA_CZATU_PATH):
            with open(HISTORIA_CZATU_PATH, "r") as f:
                historia = json.load(f)
        else:
            historia = []

        historia.append(wpis)
        with open(HISTORIA_CZATU_PATH, "w") as f:
            json.dump(historia, f, indent=2)

        return jsonify({"response": ai_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
from flask import session, redirect, url_for, flash

app.secret_key = 'tajny_klucz_123'  # ważne: zmień na bezpieczny

# Plik z użytkownikami
USERS_FILE = "data/uzytkownicy.json"

@app.route("/forum")
@login_required
def forum():
    try:
        with open(FORUM_FILE, "r") as f:
            posts = json.load(f)
    except FileNotFoundError:
        posts = []
    return render_template("forum.html", posts=posts[::-1])
@app.route("/forum/<int:watek_id>")
@login_required
def watek(watek_id):
    with open(FORUM_FILE, "r") as f:
        wątki = json.load(f)
    
    if watek_id < 0 or watek_id >= len(wątki):
        return "Nie znaleziono wątku", 404

    watek = wątki[watek_id]
    return render_template("watek.html", watek=watek, watek_id=watek_id)
def ocen_watek_ai(tytul, tresc):
    prompt = f"Przeanalizuj następujący wpis na forum:\nTytuł: {tytul}\nTreść: {tresc}\n\nJaka to kategoria emocjonalna? Wybierz jedno słowo: pilne, wsparcie, neutralne."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem wsparcia psychicznego."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        wynik = response.choices[0].message.content.strip().lower()
        if wynik in ["pilne", "wsparcie", "neutralne"]:
            return wynik
        return "neutralne"
    except Exception as e:
        print("Błąd analizy AI:", e)
        return "neutralne"


@app.route("/forum/dodaj", methods=["GET", "POST"])
@login_required
def dodaj_watek():
    if request.method == "POST":
        tytul = request.form["tytul"]
        tresc = request.form["tresc"]
        kategoria = request.form["kategoria"]
        autor = session.get("user", "anonim")
        data = datetime.now().strftime("%Y-%m-%d %H:%M")

        nowy_watek = {
            "tytul": tytul,
            "tresc": tresc,
            "kategoria": kategoria,
            "autor": autor,
            "data": data,
            "odpowiedzi": [],
            "ocena_ai": ocen_watek_ai(tytul, tresc)

        }

        with open(FORUM_FILE, "r") as f:
            wątki = json.load(f)
        wątki.append(nowy_watek)

        with open(FORUM_FILE, "w") as f:
            json.dump(wątki, f, indent=2)

        return redirect("/forum")
    
    return render_template("dodaj_watek.html")

@app.route("/forum/<int:watek_id>/dodaj", methods=["POST"])
@login_required
def dodaj_odpowiedz(watek_id):
    tresc = request.form["tresc"]
    autor = session.get("user", "anonim")
    data = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Słowa-klucze, które powodują ukrycie odpowiedzi
    niepokojace_slowa = [
        "samobójstwo", "samobójcze", "zabiję", "zabiłbym", "powiesić się", 
        "nie chcę żyć", "chciałbym umrzeć", "skończyć ze sobą"
    ]

    # Filtr treści
    ukryj = any(slowo in tresc.lower() for slowo in niepokojace_slowa)

    with open(FORUM_FILE, "r") as f:
        watki = json.load(f)

    if watek_id < 0 or watek_id >= len(watki):
        return "Nie znaleziono wątku", 404

    odpowiedz = {
        "tresc": tresc,
        "autor": autor,
        "data": data,
        "ukryj": ukryj
    }

    watki[watek_id]["odpowiedzi"].append(odpowiedz)

    with open(FORUM_FILE, "w") as f:
        json.dump(watki, f, indent=2, ensure_ascii=False)

    return redirect(f"/forum/{watek_id}")

# Rejestracja
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login = request.form["login"]
        haslo = request.form["haslo"]
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        if login in users:
            return "Użytkownik już istnieje"
        users[login] = {"haslo": haslo}
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        return redirect("/login")
    return render_template("register.html")

# Logowanie
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        haslo = request.form.get("haslo")

        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        if login in users and users[login]["haslo"] == haslo:
            session["user"] = login
            return redirect("/")
        else:
            return "Nieprawidłowe dane logowania"
    return render_template("login.html")

# Wylogowanie
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/dziennik", methods=["GET", "POST"])
@login_required
def dziennik():
    if request.method == "POST":
        emocje = request.form.get("emocje")
        tresc = request.form.get("tresc")
        data = datetime.now().strftime("%Y-%m-%d %H:%M")
        wpis = {"data": data, "emocje": emocje, "tresc": tresc}

        try:
            with open("data/dziennik.json", "r") as f:
                wpisy = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            wpisy = []

        wpisy.append(wpis)

        with open("data/dziennik.json", "w") as f:
            json.dump(wpisy, f, indent=2, ensure_ascii=False)

        return redirect("/dziennik")

    try:
        with open("data/dziennik.json", "r") as f:
            wpisy = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        wpisy = []

    return render_template("dziennik.html", wpisy=wpisy)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

