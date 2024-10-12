# app.py

from app import app

from flask import Flask, send_from_directory
app = Flask(__name__)

@app.route('/static')
def custom_static(filename):
    return send_from_directory('static', filename, cache_timeout=3600)  # 1 heure de cache

if __name__ == "__main__":
    app.run(debug=True)

