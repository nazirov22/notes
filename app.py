from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import sqlite3
from datetime import datetime
import hashlib

app = Flask(__name__, static_folder='static', static_url_path='/')
CORS(app)

def get_db_connection(db_name='notes.db'):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return password  # Временно отключаем хэширование для тестов

# Эндпоинт для получения user_id из куки
@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    user_id = request.cookies.get('user_id')
    if user_id:
        return jsonify({'user_id': user_id}), 200
    return jsonify({'error': 'User not logged in'}), 401

# Регистрация
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

# Вход
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
        response = make_response(jsonify({'user_id': user['user_id'], 'message': 'Вход выполнен'}), 200)
        response.set_cookie('user_id', str(user['user_id']), max_age=3600)
        return response
    return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401

# Создание заметки
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

# Получение заметок (оригинальный эндпоинт)
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

# Обновление заметки
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

# Удаление заметки
@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Note WHERE note_id = ?', (note_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Заметка удалена'}), 200

# Получение категорий
@app.route('/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT category_id, name FROM Category')
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(categories), 200

# Получение тегов
@app.route('/tags', methods=['GET'])
def get_tags():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT tag_id, name FROM Tag')
    tags = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tags), 200

# Сохранение запроса (из save_request.py)
@app.route('/save', methods=['POST'])
def save_request():
    data = request.get_json()
    request_text = str(data)
    conn = get_db_connection('requests.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS Requests
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     request_text TEXT,
                     timestamp DATETIME)''')
    conn.execute('INSERT INTO Requests (request_text, timestamp) VALUES (?, ?)',
                 (request_text, datetime.now()))
    conn.commit()
    conn.close()
    return "Выполнено", 200

# Обработка запросов заметок (из process_request.py)
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

# Маршруты для статических HTML
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/register')
def serve_register():
    return app.send_static_file('register.html')

@app.route('/login')
def serve_login():
    return app.send_static_file('login.html')

@app.route('/notes')
def serve_notes():
    return app.send_static_file('notes.html')

@app.route('/edit-note')
def serve_edit_note():
    return app.send_static_file('edit-note.html')

# Обработка всех остальных статических файлов
@app.route('/<path:path>')
def static_files(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)