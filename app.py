from flask import Flask, send_from_directory, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/<path:filename>')
def serve_file(filename):
    # Sprawdź czy plik istnieje
    if os.path.exists(filename):
        return send_from_directory('.', filename)
    else:
        # Jeśli plik nie istnieje, zwróć 404
        return "File not found", 404
# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem do wsparcia psychicznego. Odpowiadaj po polsku, z empatią i zrozumieniem."},
                {"role": "user", "content": user_message}
            ]
        )
        
        ai_response = response.choices[0].message.content
        return jsonify({"response": ai_response})
        
    except Exception as e:
        print(f"Błąd API: {e}")  # To pokaże błąd w logach
        return jsonify({"error": str(e)}), 500
        
        ai_response = response.choices[0].message.content
        return jsonify({"response": ai_response})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
