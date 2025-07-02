import matplotlib.pyplot as plt
from collections import Counter

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import random
from openai import OpenAI

app = Flask(__name__)

# Lista technik DBT
DBT_TECHNIQUES = [
    "Ćwiczenie oddechowe: Wdech przez 4 sekundy, zatrzymaj na 7 sekund, wydech przez 8 sekund.",
    "Zanotuj swoje emocje i myśli na papierze – nie oceniaj, tylko obserwuj.",
    "Zastosuj technikę STOP: Stój, Weź oddech, Obserwuj, Podejmij decyzję.",
    "Skieruj uwagę na otoczenie – opisz 5 rzeczy, które widzisz, 4 które słyszysz, 3 które czujesz dotykiem.",
    "Zanurz twarz w zimnej wodzie na kilka sekund, by obniżyć napięcie emocjonalne (technika TIPP)."
]

# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/cwiczenie-oddechowe')
def cwiczenie_oddechowe():
    return render_template('cwiczenie-oddechowe.html')

@app.route('/<path:filename>')
def serve_file(filename):
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    else:
        return "File not found", 404

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        CRISIS_KEYWORDS = [
            "nie chcę żyć", "mam dość", "jestem bezużyteczny",
            "popełnię samobójstwo", "chcę zniknąć", "koniec wszystkiego"
        ]

        STRESS_KEYWORDS = [
            "jestem zestresowany", "nie mogę spać", "panika",
            "mam lęk", "czuję niepokój", "nerwy", "nie mogę się uspokoić"
        ]

        user_lower = user_message.lower()
        is_crisis = any(kw in user_lower for kw in CRISIS_KEYWORDS)
        is_stress = any(kw in user_lower for kw in STRESS_KEYWORDS)

        if is_crisis:
            selected_technique = random.choice(DBT_TECHNIQUES)
            system_prompt = (
                "Zachowuj się jak bardzo empatyczny, spokojny i troskliwy psycholog. "
                "Użytkownik może być w sytuacji kryzysowej, więc Twoim zadaniem jest go wesprzeć emocjonalnie, bez dawania gotowych rozwiązań. "
                "Zachęć go do kontaktu z profesjonalistą, pokaż zrozumienie, zapytaj czy potrzebuje pomocy. "
                "Możesz delikatnie wspomnieć o możliwości wykonania techniki DBT, ale tylko jako wsparcie doraźne. "
                f"Oto jedna z technik:\n\n{selected_technique}\n\n"
                "Zakończ pytaniem: 'Czy chciałbyś, żebym pokazał Ci coś, co możesz spróbować zrobić teraz?'"
            )

        elif is_stress:
            selected_technique = random.choice(DBT_TECHNIQUES)
            system_prompt = (
                "Użytkownik doświadcza stresu, napięcia lub lęku. "
                "Zaproponuj empatyczną odpowiedź, a następnie spokojnie zaproś go do wypróbowania prostej techniki DBT "
                f"– takiej jak:\n\n{selected_technique}\n\n"
                "Wyjaśnij, że może ona pomóc się uspokoić. Zapytaj: 'Czy chciałbyś, żebym poprowadził Cię przez to ćwiczenie?'"
            )

        else:
            system_prompt = (
                "Jesteś pomocnym asystentem psychologicznym. Odpowiadaj empatycznie i profesjonalnie. "
                "Jeśli to możliwe, zachęć do kontaktu z terapeutą lub bliską osobą w trudnych chwilach."
            )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content
        return jsonify({"response": ai_response})

    except Exception as e:
        app.logger.error(f"Błąd API: {e}")
        return jsonify({"error": str(e)}), 500
import json
from datetime import datetime
from flask import redirect, url_for

FORUM_PATH = "data/forum.json"

def load_posts():
    with open(FORUM_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_posts(posts):
    with open(FORUM_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

@app.route('/forum')
def forum():
    with open("data/forum.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    # Statystyki
    total_posts = len(posts)
    kryzys_count = sum(1 for p in posts if p.get("ocena_ai") == "kryzys")
    wsparcie_count = sum(1 for p in posts if p.get("ocena_ai") == "wsparcie")
    
    ukryte_odp = 0
    for p in posts:
        for o in p.get("odpowiedzi", []):
            if o.get("ukryj"):
                ukryte_odp += 1

    return render_template(
        "forum.html",
        posts=posts[::-1],  # od najnowszego
        total_posts=total_posts,
        kryzys_count=kryzys_count,
        wsparcie_count=wsparcie_count,
        ukryte_odp=ukryte_odp
    )


@app.route('/forum/dodaj', methods=["POST"])
def dodaj_watek():
    data = request.form
    posts = load_posts()
    new_id = (posts[-1]["id"] + 1) if posts else 1

    # Składamy wiadomość do oceny przez GPT
    tresc = data.get("tresc")
    system_prompt = (
        "Jesteś pomocnym moderatorem forum wsparcia psychicznego. "
        "Twoim zadaniem jest ocenić wpis użytkownika i zaklasyfikować go jako: "
        "'neutralny', 'wsparcie' lub 'kryzys'. "
        "Oceń krótko, bez komentarzy. Zwróć tylko jeden z tych trzech słów."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # lub gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": tresc}
            ],
            max_tokens=10,
            temperature=0.3,
        )
        klasyfikacja = response.choices[0].message.content.strip().lower()
    except Exception as e:
        klasyfikacja = "nieokreślony"

    posts.append({
        "id": new_id,
        "kategoria": data.get("kategoria"),
        "tytul": data.get("tytul"),
        "tresc": tresc,
        "autor": data.get("autor") or "Anonim",
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ocena_ai": klasyfikacja,
        "odpowiedzi": []
    })

    save_posts(posts)
    return redirect(url_for('forum'))


@app.route('/forum/<int:watek_id>')
def pokaz_watek(watek_id):
    posts = load_posts()
    for post in posts:
        if post["id"] == watek_id:
            return render_template("watek.html", post=post)
    return "Nie znaleziono wątku", 404

@app.route('/forum/<int:id>/odpowiedz', methods=['POST'])
def dodaj_odpowiedz(id):
    with open("data/forum.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    post = next((p for p in posts if p["id"] == id), None)
    if not post:
        return "Wątek nie istnieje", 404

    tresc = request.form["tresc"]
    autor = request.form.get("autor", "Anonim")

    # Ocena AI – czy odpowiedź jest niepokojąca
    try:
        ocena = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Twoim zadaniem jest ocenić, czy wpis użytkownika zawiera niepokojące lub agresywne treści. Jeśli tak, odpowiedz tylko 'ukryj', w przeciwnym razie odpowiedz 'ok'."},
                {"role": "user", "content": tresc}
            ],
            max_tokens=10
        ).choices[0].message.content.strip().lower()

        ukryj = (ocena == "ukryj")
    except Exception as e:
        ukryj = False

    nowa_odpowiedz = {
        "tresc": tresc,
        "autor": autor,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ukryj": ukryj
    }

    post.setdefault("odpowiedzi", []).append(nowa_odpowiedz)

    with open("data/forum.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    return redirect(f"/forum/{id}")
@app.route('/dziennik', methods=["GET", "POST"])
def dziennik():
    with open("data/dziennik.json", "r", encoding="utf-8") as f:
        wpisy = json.load(f)

    if request.method == "POST":
        tresc = request.form["tresc"]
        autor = request.form.get("autor", "Anonim")

        # Ocena AI nastroju
        try:
            analiza = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Twoim zadaniem jest ocenić emocję wpisu. Odpowiedz jednym słowem: 'smutek', 'lęk', 'złość', 'radość', 'spokój', 'przygnębienie', 'nadzieja' itp."},
                    {"role": "user", "content": tresc}
                ],
                max_tokens=10
            ).choices[0].message.content.strip().lower()
        except Exception as e:
            analiza = "nieokreślone"
    # Zapis nowego wpisu (jeśli formularz POST)
    if request.method == "POST":
        wpis = {
            "autor": request.form.get("autor", "anonim"),
            "tresc": request.form.get("tresc", ""),
            "emocja": ocen_emocje(request.form.get("tresc", "nieokreślone")),
            "data": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        wpisy.append(wpis)
        with open("dziennik.json", "w", encoding="utf-8") as f:
            json.dump(wpisy, f, ensure_ascii=False, indent=2)

    # Analiza emocji do wykresu
    emocje = [w["emocja"] for w in wpisy if "emocja" in w]

    if emocje:
        licznik = Counter(emocje)
        etykiety = list(licznik.keys())
        wartosci = list(licznik.values())

        plt.figure(figsize=(8, 5))
        plt.bar(etykiety, wartosci, color="seagreen")
        plt.title("Emocje z ostatnich wpisów")
        plt.xlabel("Emocja")
        plt.ylabel("Liczba")
        plt.tight_layout()
        plt.savefig("static/emocje.png")
        print("Wykres zapisany!")
        plt.close()
    else:
        print("Brak emocji – nie generuję wykresu.")

    # Wyświetlenie dziennika
    return render_template("dziennik.html", wpisy=wpisy[::-1])
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

