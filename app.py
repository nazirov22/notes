from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import hashlib

app = Flask(__name__, static_folder='static', static_url_path='/')
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    # return hashlib.sha256(password.encode()).hexdigest()
    return password  # Временно отключаем хэширование для тестов


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = hash_password(data.get('password'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO User (username, email, password) VALUES (?, ?, ?)',
                      (username, email, password))
        conn.commit()
        return jsonify({'message': 'Пользователь зарегистрирован'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Пользователь с таким именем или email уже существует'}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = hash_password(data.get('password'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM User WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({'user_id': user['user_id'], 'message': 'Вход выполнен'}), 200
    return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401

@app.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    tags = data.get('tags', [])
    creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Note (title, content, creation_date, last_modified, is_archived, user_id, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, content, creation_date, creation_date, 0, user_id, category_id))
    note_id = cursor.lastrowid
    
    for tag_id in tags:
        cursor.execute('INSERT INTO Note_Tag (note_id, tag_id) VALUES (?, ?)', (note_id, tag_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Заметка создана', 'note_id': note_id}), 201

@app.route('/notes', methods=['GET'])
def get_notes():
    user_id = request.args.get('user_id')
    tag_name = request.args.get('tag_name')
    category_id = request.args.get('category_id')
    search_query = request.args.get('search_query')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT n.note_id, n.title, n.content, c.name as category, n.creation_date
        FROM Note n
        JOIN Category c ON n.category_id = c.category_id
        WHERE n.user_id = ? AND n.is_archived = 0
    '''
    params = [user_id]
    
    if tag_name:
        query += ' AND n.note_id IN (SELECT note_id FROM Note_Tag nt JOIN Tag t ON nt.tag_id = t.tag_id WHERE t.name = ?)'
        params.append(tag_name)
    if category_id:
        query += ' AND n.category_id = ?'
        params.append(category_id)
    if search_query:
        query += ' AND n.title LIKE ?'
        params.append(f'%{search_query}%')
    
    cursor.execute(query, params)
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(notes), 200

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    category_id = data.get('category_id')
    tags = data.get('tags', [])
    last_modified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Note
        SET title = ?, content = ?, category_id = ?, last_modified = ?
        WHERE note_id = ?
    ''', (title, content, category_id, last_modified, note_id))
    
    cursor.execute('DELETE FROM Note_Tag WHERE note_id = ?', (note_id,))
    for tag_id in tags:
        cursor.execute('INSERT INTO Note_Tag (note_id, tag_id) VALUES (?, ?)', (note_id, tag_id))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Заметка обновлена'}), 200

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Note WHERE note_id = ?', (note_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Заметка удалена'}), 200

@app.route('/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT category_id, name FROM Category')
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(categories), 200

@app.route('/tags', methods=['GET'])
def get_tags():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT tag_id, name FROM Tag')
    tags = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tags), 200

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)