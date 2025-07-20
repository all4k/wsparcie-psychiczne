# Wsparcie Psychiczne – Aplikacja webowa

Aplikacja do anonimowego czatu z wirtualnym terapeutą wspieranym przez model GPT-4.

## Funkcje:
- Rejestracja/logowanie użytkownika (tymczasowe sesje)
- Czat z AI (empatyczna odpowiedź, detekcja kryzysu)
- Sugerowanie technik DBT przy słowach kluczowych
- Zachowanie historii rozmowy w sesji
- Obsługa emoji, interfejs typu Messenger
- Odpowiedzi pisane "maszynowo" litera po literze

## Technologia:
- Python (Flask)
- OpenAI API (GPT-4)
- HTML / CSS / JS
- Bootstrap / EventSource

## Uruchomienie lokalne:
```bash
git clone https://github.com/all4k/wsparcie-psychiczne.git
cd wsparcie-psychiczne
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=twoj_klucz_api
python app.py
Autor:

Jakub Wąsik / Projekt wsparcia psychicznego, 2025
