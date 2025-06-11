from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:newpassword@localhost/quizapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')

db = SQLAlchemy(app)

# MODELS

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

# Utility: seed quiz/questions if missing
def ensure_quiz_exists():
    quiz = Quiz.query.first()
    if not quiz:
        quiz = Quiz(title="Web Technology Quiz", category="Web")
        db.session.add(quiz)
        db.session.commit()
    if not Question.query.filter_by(quiz_id=quiz.id).count():
        questions = [
            {
                "question_text": "What does HTML stand for?",
                "options": [
                    "Hyper Text Preprocessor",
                    "Hyper Text Markup Language",
                    "Hyper Text Multiple Language",
                    "Hyper Tool Multi Language"
                ],
                "correct_option": "B"
            },
            {
                "question_text": "What does CSS stand for?",
                "options": [
                    "Common Style Sheet",
                    "Colorful Style Sheet",
                    "Computer Style Sheet",
                    "Cascading Style Sheet"
                ],
                "correct_option": "D"
            },
            {
                "question_text": "What does PHP stand for?",
                "options": [
                    "Hypertext Preprocessor",
                    "Hypertext Programming",
                    "Hypertext Preprogramming",
                    "Hometext Preprocessor"
                ],
                "correct_option": "A"
            },
            {
                "question_text": "What does SQL stand for?",
                "options": [
                    "Stylish Question Language",
                    "Stylesheet Query Language",
                    "Statement Question Language",
                    "Structured Query Language"
                ],
                "correct_option": "D"
            },
            {
                "question_text": "What does XML stand for?",
                "options": [
                    "eXtensible Markup Language",
                    "eXecutable Multiple Language",
                    "eXTra Multi-Program Language",
                    "eXamine Multiple Language"
                ],
                "correct_option": "A"
            },
        ]
        for q in questions:
            db.session.add(Question(
                quiz_id=quiz.id,
                question_text=q["question_text"],
                option_a=q["options"][0],
                option_b=q["options"][1],
                option_c=q["options"][2],
                option_d=q["options"][3],
                correct_option=q["correct_option"]
            ))
        db.session.commit()
    return quiz

# ROUTE

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/quizpage', methods=['GET'])
def quiz_page():
    return render_template('quiz.html')

@app.route('/scorepage', methods=['GET'])
def score_page():
    return render_template('score.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_page'))


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already exists'}), 409

    password_hash = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful', 'username': user.username})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/quiz', methods=['GET'])
def get_quiz():
    quiz = ensure_quiz_exists()
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    question_list = []
    for q in questions:
        question_list.append({
            'id': q.id,
            'question_text': q.question_text,
            'options': {
                'A': q.option_a,
                'B': q.option_b,
                'C': q.option_c,
                'D': q.option_d
            }
        })
    return jsonify({
        'quiz_id': quiz.id,
        'title': quiz.title,
        'category': quiz.category,
        'questions': question_list
    })

@app.route('/submit', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json() or request.form
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', {})  # {question_id: selected_option}
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    score = 0
    for q in questions:
        selected = answers.get(str(q.id))
        if selected and selected.upper() == q.correct_option.upper():
            score += 1
    result = Result(user_id=session['user_id'], quiz_id=quiz_id, score=score)
    db.session.add(result)
    db.session.commit()
    return jsonify({'message': 'Quiz submitted', 'score': score, 'max_score': len(questions)})

@app.route('/score', methods=['GET'])
def user_scores():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    results = Result.query.filter_by(user_id=session['user_id']).order_by(Result.submitted_at.desc()).all()
    scores = []
    for r in results:
        quiz = Quiz.query.get(r.quiz_id)
        scores.append({
            'quiz_title': quiz.title if quiz else 'Unknown',
            'score': r.score,
            'submitted_at': r.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'scores': scores})

def init_db():
    with app.app_context():
        db.create_all()
        print("✓ Database initialized.")

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)