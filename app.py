from flask import Flask, render_template, request, jsonify, redirect
import os
import json
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import random
from openai import OpenAI

app = Flask(__name__)

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


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/cwiczenie-oddechowe')
def cwiczenie():
    return render_template('cwiczenie-oddechowe.html')


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

