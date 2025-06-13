from flask import Flask, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('requests.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS Requests
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     request_text TEXT,
                     timestamp DATETIME)''')
    return conn

@app.route('/save', methods=['POST'])
def save_request():
    data = request.get_json()
    request_text = str(data)
    conn = get_db_connection()
    conn.execute('INSERT INTO Requests (request_text, timestamp) VALUES (?, ?)',
                 (request_text, datetime.now()))
    conn.commit()
    conn.close()
    return "Выполнено", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)