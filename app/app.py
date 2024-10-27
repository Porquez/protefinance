# app.py
import logging
from app import app
from flask_socketio import SocketIO

from flask import Flask, send_from_directory
app = Flask(__name__)
socketio = SocketIO(app)

# Configurer le logger
logging.basicConfig(level=logging.INFO)

@app.route('/static')
def custom_static(filename):
    return send_from_directory('static', filename, cache_timeout=3600)  # 1 heure de cache

if __name__ == "__main__":
    app.run(debug=True)

