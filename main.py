from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
import os
from functools import wraps

app = Flask(__name__,template_folder='templates')


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:newpassword@localhost/quizapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:5500', 'http://localhost:5500'])


# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    created_quizzes = db.relationship('Quiz', backref='creator', lazy=True)


class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_limit = db.Column(db.Integer)  # in minutes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')
    points = db.Column(db.Integer, default=1)
    order_num = db.Column(db.Integer, default=1)

    # Relationships
    options = db.relationship('QuestionOption', backref='question', lazy=True, cascade='all, delete-orphan')
    answers = db.relationship('UserAnswer', backref='question', lazy=True)


class QuestionOption(db.Model):
    __tablename__ = 'question_options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    option_text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order_num = db.Column(db.Integer, default=1)


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)

    # Relationships
    answers = db.relationship('UserAnswer', backref='attempt', lazy=True)


class UserAnswer(db.Model):
    __tablename__ = 'user_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('question_options.id'))
    answer_text = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, default=False)
    points_earned = db.Column(db.Integer, default=0)


# Input validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    return len(password) >= 6


def validate_username(username):
    return len(username) >= 3 and len(username) <= 50 and username.replace('_', '').isalnum()


def validate_quiz_data(data):
    errors = []
    if not data.get('title') or len(data['title'].strip()) < 3:
        errors.append('Title must be at least 3 characters long')
    if len(data.get('title', '')) > 200:
        errors.append('Title must be less than 200 characters')
    if 'time_limit' in data and data['time_limit'] is not None:
        if not isinstance(data['time_limit'], int) or data['time_limit'] <= 0:
            errors.append('Time limit must be a positive number')
    return errors


def validate_question_data(data):
    errors = []
    if not data.get('question_text') or len(data['question_text'].strip()) < 5:
        errors.append('Question text must be at least 5 characters long')
    if data.get('question_type') not in ['multiple_choice', 'true_false', 'short_answer']:
        errors.append('Invalid question type')
    if 'points' in data and (not isinstance(data['points'], int) or data['points'] <= 0):
        errors.append('Points must be a positive number')
    return errors


# Admin required decorator
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Quiz API Backend',
        'version': '1.0',
        'endpoints': {
            'auth': ['/api/register', '/api/login', '/api/profile'],
            'quizzes': ['/api/quizzes', '/api/quizzes/<id>'],
            'attempts': ['/api/quizzes/<id>/start', '/api/attempts/<id>/submit', '/api/attempts/<id>/results']
        }
    })


# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Validation
        errors = []
        if not validate_username(username):
            errors.append('Username must be 3-50 characters, alphanumeric with underscores allowed')
        if not validate_email(email):
            errors.append('Invalid email format')
        if not validate_password(password):
            errors.append('Password must be at least 6 characters')

        if errors:
            return jsonify({'errors': errors}), 400

        # Check existing users
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Create user
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash)

        db.session.add(user)
        db.session.commit()

        # Create token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        # Find user
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            }
        })

    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get user stats
        total_attempts = QuizAttempt.query.filter_by(user_id=user.id, is_completed=True).count()
        created_quizzes = Quiz.query.filter_by(created_by=user.id).count()

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat(),
                'stats': {
                    'total_attempts': total_attempts,
                    'created_quizzes': created_quizzes
                }
            }
        })

    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500


# Quiz Routes
@app.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        quizzes = Quiz.query.filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )

        quiz_list = []
        for quiz in quizzes.items:
            creator = User.query.get(quiz.created_by)
            quiz_list.append({
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'created_by': creator.username if creator else 'Unknown',
                'time_limit': quiz.time_limit,
                'question_count': len(quiz.questions),
                'created_at': quiz.created_at.isoformat()
            })

        return jsonify({
            'quizzes': quiz_list,
            'pagination': {
                'page': page,
                'pages': quizzes.pages,
                'per_page': per_page,
                'total': quizzes.total
            }
        })

    except Exception as e:
        return jsonify({'error': 'Failed to fetch quizzes'}), 500


@app.route('/api/quizzes', methods=['POST'])
@jwt_required()
def create_quiz():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate
        errors = validate_quiz_data(data)
        if errors:
            return jsonify({'errors': errors}), 400

        quiz = Quiz(
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            created_by=current_user_id,
            time_limit=data.get('time_limit')
        )

        db.session.add(quiz)
        db.session.commit()

        return jsonify({
            'message': 'Quiz created successfully',
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'time_limit': quiz.time_limit
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create quiz'}), 500


@app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    try:
        quiz = Quiz.query.get(quiz_id)

        if not quiz or not quiz.is_active:
            return jsonify({'error': 'Quiz not found'}), 404

        questions = []
        for question in sorted(quiz.questions, key=lambda x: x.order_num):
            options = []
            for option in sorted(question.options, key=lambda x: x.order_num):
                options.append({
                    'id': option.id,
                    'text': option.option_text,
                    'order_num': option.order_num
                })

            questions.append({
                'id': question.id,
                'text': question.question_text,
                'type': question.question_type,
                'points': question.points,
                'order_num': question.order_num,
                'options': options
            })

        creator = User.query.get(quiz.created_by)

        return jsonify({
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'created_by': creator.username if creator else 'Unknown',
                'time_limit': quiz.time_limit,
                'questions': questions
            }
        })

    except Exception as e:
        return jsonify({'error': 'Failed to fetch quiz'}), 500


@app.route('/api/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
def add_question(quiz_id):
    try:
        current_user_id = get_jwt_identity()
        quiz = Quiz.query.get(quiz_id)

        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        # Check permissions
        if quiz.created_by != current_user_id:
            user = User.query.get(current_user_id)
            if not user or not user.is_admin:
                return jsonify({'error': 'Permission denied'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate
        errors = validate_question_data(data)
        if errors:
            return jsonify({'errors': errors}), 400

        question = Question(
            quiz_id=quiz_id,
            question_text=data['question_text'].strip(),
            question_type=data.get('question_type', 'multiple_choice'),
            points=data.get('points', 1),
            order_num=data.get('order_num', len(quiz.questions) + 1)
        )

        db.session.add(question)
        db.session.flush()

        # Add options
        if 'options' in data and data['options']:
            for i, option_data in enumerate(data['options']):
                if not option_data.get('text', '').strip():
                    continue

                option = QuestionOption(
                    question_id=question.id,
                    option_text=option_data['text'].strip(),
                    is_correct=option_data.get('is_correct', False),
                    order_num=option_data.get('order_num', i + 1)
                )
                db.session.add(option)

        db.session.commit()

        return jsonify({
            'message': 'Question added successfully',
            'question': {
                'id': question.id,
                'text': question.question_text,
                'type': question.question_type,
                'points': question.points
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add question'}), 500


# Quiz Attempt Routes
@app.route('/api/quizzes/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    try:
        current_user_id = get_jwt_identity()
        quiz = Quiz.query.get(quiz_id)

        if not quiz or not quiz.is_active:
            return jsonify({'error': 'Quiz not found'}), 404

        if not quiz.questions:
            return jsonify({'error': 'Quiz has no questions'}), 400

        # Check for existing incomplete attempt
        existing_attempt = QuizAttempt.query.filter_by(
            user_id=current_user_id,
            quiz_id=quiz_id,
            is_completed=False
        ).first()

        if existing_attempt:
            return jsonify({
                'message': 'Quiz attempt resumed',
                'attempt_id': existing_attempt.id,
                'started_at': existing_attempt.started_at.isoformat(),
                'time_limit': quiz.time_limit
            })

        # Create new attempt
        max_score = sum(q.points for q in quiz.questions)
        attempt = QuizAttempt(
            user_id=current_user_id,
            quiz_id=quiz_id,
            max_score=max_score
        )

        db.session.add(attempt)
        db.session.commit()

        return jsonify({
            'message': 'Quiz started successfully',
            'attempt_id': attempt.id,
            'started_at': attempt.started_at.isoformat(),
            'time_limit': quiz.time_limit
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to start quiz'}), 500


@app.route('/api/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(attempt_id):
    try:
        current_user_id = get_jwt_identity()
        attempt = QuizAttempt.query.get(attempt_id)

        if not attempt or attempt.user_id != current_user_id:
            return jsonify({'error': 'Quiz attempt not found'}), 404

        if attempt.is_completed:
            return jsonify({'error': 'Quiz already completed'}), 400

        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({'error': 'No answers provided'}), 400

        total_score = 0

        # Process answers
        for answer_data in data['answers']:
            question_id = answer_data.get('question_id')
            selected_option_id = answer_data.get('selected_option_id')
            answer_text = answer_data.get('answer_text', '').strip()

            if not question_id:
                continue

            question = Question.query.get(question_id)
            if not question or question.quiz_id != attempt.quiz_id:
                continue

            # Skip if already answered
            existing_answer = UserAnswer.query.filter_by(
                attempt_id=attempt_id,
                question_id=question_id
            ).first()

            if existing_answer:
                continue

            is_correct = False
            points_earned = 0

            # Check answer
            if question.question_type in ['multiple_choice', 'true_false'] and selected_option_id:
                option = QuestionOption.query.get(selected_option_id)
                if option and option.question_id == question_id and option.is_correct:
                    is_correct = True
                    points_earned = question.points

            # Save user answer
            user_answer = UserAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                answer_text=answer_text,
                is_correct=is_correct,
                points_earned=points_earned
            )

            db.session.add(user_answer)
            total_score += points_earned

        # Update attempt
        attempt.score = total_score
        attempt.completed_at = datetime.utcnow()
        attempt.is_completed = True

        db.session.commit()

        percentage = round((total_score / attempt.max_score) * 100, 2) if attempt.max_score > 0 else 0

        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': total_score,
            'max_score': attempt.max_score,
            'percentage': percentage
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit quiz'}), 500


@app.route('/api/attempts/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_results(attempt_id):
    try:
        current_user_id = get_jwt_identity()
        attempt = QuizAttempt.query.get(attempt_id)

        if not attempt or attempt.user_id != current_user_id:
            return jsonify({'error': 'Quiz attempt not found'}), 404

        if not attempt.is_completed:
            return jsonify({'error': 'Quiz not completed yet'}), 400

        quiz = Quiz.query.get(attempt.quiz_id)
        answers = UserAnswer.query.filter_by(attempt_id=attempt_id).all()

        answer_details = []
        for answer in answers:
            question = Question.query.get(answer.question_id)
            selected_option = None
            correct_options = []

            if answer.selected_option_id:
                selected_option = QuestionOption.query.get(answer.selected_option_id)

            # Get correct options for reference
            for option in question.options:
                if option.is_correct:
                    correct_options.append(option.option_text)

            answer_details.append({
                'question_id': answer.question_id,
                'question_text': question.question_text,
                'selected_option': selected_option.option_text if selected_option else None,
                'correct_options': correct_options,
                'answer_text': answer.answer_text,
                'is_correct': answer.is_correct,
                'points_earned': answer.points_earned,
                'max_points': question.points
            })

        percentage = round((attempt.score / attempt.max_score) * 100, 2) if attempt.max_score > 0 else 0

        return jsonify({
            'attempt_id': attempt.id,
            'quiz_title': quiz.title,
            'score': attempt.score,
            'max_score': attempt.max_score,
            'percentage': percentage,
            'completed_at': attempt.completed_at.isoformat(),
            'answers': answer_details
        })

    except Exception as e:
        return jsonify({'error': 'Failed to fetch results'}), 500


# Admin Routes
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        users = User.query.all()
        user_list = []

        for user in users:
            completed_attempts = QuizAttempt.query.filter_by(
                user_id=user.id, is_completed=True
            ).count()

            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat(),
                'completed_attempts': completed_attempts,
                'created_quizzes': len(user.created_quizzes)
            })

        return jsonify({'users': user_list})

    except Exception as e:
        return jsonify({'error': 'Failed to fetch users'}), 500


@app.route('/api/admin/quizzes', methods=['GET'])
@admin_required
def get_all_quizzes():
    try:
        quizzes = Quiz.query.all()
        quiz_list = []

        for quiz in quizzes:
            creator = User.query.get(quiz.created_by)
            attempts_count = QuizAttempt.query.filter_by(quiz_id=quiz.id).count()

            quiz_list.append({
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'created_by': creator.username if creator else 'Unknown',
                'question_count': len(quiz.questions),
                'attempts_count': attempts_count,
                'is_active': quiz.is_active,
                'created_at': quiz.created_at.isoformat()
            })

        return jsonify({'quizzes': quiz_list})

    except Exception as e:
        return jsonify({'error': 'Failed to fetch quizzes'}), 500


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authentication token required'}), 401


# Database initialization
def init_db():
    """Initialize database tables and create admin user"""
    with app.app_context():
        db.create_all()

        # Create admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_password = generate_password_hash('admin123')
            admin = User(
                username='admin',
                email='admin@quiz.com',
                password_hash=admin_password,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created: username='admin', password='admin123'")
        else:
            print("✓ Admin user already exists")

        print("✓ Database initialized successfully")


if __name__ == '__main__':
    init_db()
    print("🚀 Starting Flask Quiz Backend...")
    print("📊 Database: PostgreSQL")
    print("🔐 Authentication: JWT")
    print("🌐 CORS: Enabled")
    print("🔑 Admin Login: admin/admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)