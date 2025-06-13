from flask import Flask, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('notes.db')
    return conn

@app.route('/query', methods=['GET'])
def query_notes():
    user_id = request.args.get('user_id')
    category_id = request.args.get('category_id')
    search_query = request.args.get('search_query')

    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT note_id, title, content FROM Note WHERE user_id = ? AND is_archived = 0'
    params = [user_id]
    if category_id:
        query += ' AND category_id = ?'
        params.append(category_id)
    if search_query:
        query += ' AND title LIKE ?'
        params.append(f'%{search_query}%')
    cursor.execute(query, params)
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {'notes': notes}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)