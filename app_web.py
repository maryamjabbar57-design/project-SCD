from flask import Flask, request, jsonify, send_from_directory
from app.database.db_manager import DatabaseManager
import os

app = Flask(__name__, static_folder='app/web', static_url_path='')
db = DatabaseManager()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def static_files(path):
    return app.send_static_file(path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = db.fetch_one("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    if user:
        return jsonify({"success": True, "user": {"id": user[0], "username": user[1], "role": user[3]}})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    existing = db.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
    if existing:
        return jsonify({"success": False, "message": "Username already exists"}), 400
        
    db.execute_query("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    return jsonify({"success": True, "message": "Registered successfully"})

@app.route('/api/questions', methods=['GET'])
def get_questions():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    
    query = "SELECT * FROM questions WHERE category = ? AND difficulty = ?"
    questions_raw = db.fetch_all(query, (category, difficulty))
    
    questions = []
    for q in questions_raw:
        # q: id, category, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option
        correct_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        questions.append({
            "id": q[0],
            "text": q[3],
            "options": [q[4], q[5], q[6], q[7]],
            "correct": correct_map.get(q[8], 0)
        })
        
    return jsonify({"questions": questions})

@app.route('/api/results', methods=['POST'])
def save_result():
    data = request.json
    db.execute_query(
        "INSERT INTO results (user_id, score, total_questions, category, difficulty) VALUES (?, ?, ?, ?, ?)",
        (data['user_id'], data['score'], data['total_questions'], data['category'], data['difficulty'])
    )
    return jsonify({"success": True})

@app.route('/api/history', methods=['GET'])
def get_history():
    user_id = request.args.get('user_id')
    results = db.fetch_all("SELECT score, total_questions, category, difficulty, date_taken FROM results WHERE user_id = ? ORDER BY date_taken DESC LIMIT 5", (user_id,))
    
    history = []
    for r in results:
        history.append({
            "score": r[0],
            "total": r[1],
            "category": r[2],
            "difficulty": r[3],
            "date": r[4]
        })
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
