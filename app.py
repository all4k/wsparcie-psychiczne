from flask import Flask, send_from_directory, render_template
import os

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
