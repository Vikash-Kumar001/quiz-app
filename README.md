# Quiz App 🧠

A modern, interactive quiz application built with Flask (Python) and PostgreSQL that allows users to test their knowledge across various topics with user authentication, session management, and persistent data storage.

## ✨ Features

- **User Authentication**: Secure user registration and login system with password hashing
- **Session Management**: Persistent user sessions across browser visits
- **Multiple Choice Questions**: Interactive quiz format with multiple answer options
- **Real-time Scoring**: Instant feedback and score tracking throughout the quiz
- **Progress Tracking**: Visual progress bar showing completion status
- **Database Storage**: Persistent storage of users, questions, and quiz results
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Results History**: View past quiz attempts and scores
- **Admin Panel**: Manage questions and view user statistics (if implemented)
- **RESTful API**: JSON endpoints for dynamic content loading

## 🚀 Demo

[Live Demo](https://your-quiz-app-demo.com) (Replace with actual demo link)

## 📱 Screenshots

```
[Add screenshots of your quiz app here]
- Login/Registration page
- Quiz dashboard
- Quiz in progress
- Results page
- Mobile view
```

## 🛠️ Technologies Used

- **Backend**: Python 3.8+, Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Authentication**: Werkzeug Security (Password hashing)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Session Management**: Flask Sessions
- **Password Security**: Werkzeug password hashing

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- Python 3.8 or higher
- PostgreSQL (version 12.0 or higher)
- pip (Python package manager)
- Git

## ⚡ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/quiz-app.git
   cd quiz-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv quiz_env
   
   # On Windows
   quiz_env\Scripts\activate
   
   # On macOS/Linux
   source quiz_env/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database (replace with your credentials)
   psql -U postgres
   CREATE DATABASE quiz_app;
   CREATE USER quiz_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE quiz_app TO quiz_user;
   \q
   ```

5. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://quiz_user:your_password@localhost/quiz_app
   ```

6. **Initialize the database**
   ```bash
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

7. **Run the application**
   ```bash
   flask run
   # or
   python app.py
   ```

8. **Open your browser**
   Navigate to `http://localhost:5000` to view the application

## 🏗️ Project Structure

```
quiz-app/

```

## 🔧 Dependencies

Create a `requirements.txt` file with these dependencies:

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
psycopg2-binary==2.9.7
Werkzeug==2.3.7
python-dotenv==1.0.0
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Questions Table
```sql
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    category VARCHAR(50),
    difficulty VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Quiz Results Table
```sql
CREATE TABLE quiz_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    time_taken INTEGER, -- in seconds
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Usage

### User Registration and Login

1. **Register**: Navigate to `/register` to create a new account
2. **Login**: Use `/login` to access your account
3. **Dashboard**: View available quizzes and your statistics

### Taking a Quiz

1. **Select Quiz**: Choose from available quiz categories
2. **Answer Questions**: Select your answers for each question
3. **Submit**: Complete the quiz to see your results
4. **Review**: Check your score and correct answers

### API Endpoints

```python
# Authentication
GET  /login          # Display login form
POST /login          # Process login
GET  /register       # Display registration form
POST /register       # Process registration
GET  /logout         # Logout user

# Quiz Management
GET  /dashboard      # User dashboard
GET  /quiz/<int:id>  # Start specific quiz
POST /quiz/submit    # Submit quiz answers
GET  /results/<int:quiz_result_id>  # View quiz results

# API Endpoints (JSON)
GET  /api/questions/<category>  # Get questions by category
POST /api/quiz/submit          # Submit quiz via API
GET  /api/user/stats           # Get user statistics
```

## ⚙️ Configuration

### Environment Variables

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development  # or production
SECRET_KEY=your-super-secret-key

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/quiz_app

# Optional Configuration
QUESTIONS_PER_QUIZ=10
QUIZ_TIME_LIMIT=1800  # 30 minutes in seconds
```

### Application Configuration

In your `app.py`:

```python
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

db = SQLAlchemy(app)
```

## 🗄️ Database Management

### Create Tables
```bash
python -c "from app import db; db.create_all()"
```

### Add Sample Data
```python
from app import db, Question

# Add sample questions
question1 = Question(
    question_text="What is the capital of France?",
    option_a="London",
    option_b="Berlin", 
    option_c="Paris",
    option_d="Madrid",
    correct_answer="c",
    category="Geography"
)
db.session.add(question1)
db.session.commit()
```

### Database Backup
```bash
pg_dump quiz_app > backup.sql
```

## 🚀 Deployment

### Heroku Deployment

1. **Install Heroku CLI**
2. **Create Heroku app**
   ```bash
   heroku create your-quiz-app
   ```

3. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set environment variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   ```

5. **Deploy**
   ```bash
   git push heroku main
   heroku run python -c "from app import db; db.create_all()"
   ```

### VPS Deployment (Ubuntu)

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip postgresql nginx
   ```

2. **Set up application**
   ```bash
   git clone your-repo
   cd quiz-app
   pip3 install -r requirements.txt
   ```

3. **Configure Nginx and Gunicorn**
   ```bash
   pip3 install gunicorn
   gunicorn --bind 0.0.0.0:8000 app:app
   ```

## 🧪 Testing

Create test files and run:

```bash
# Install testing dependencies
pip install pytest pytest-flask

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

## 🛡️ Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Session Management**: Secure session handling with Flask
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CSRF Protection**: Implement CSRF tokens for forms
- **Input Validation**: Server-side validation for all user inputs

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Verify database credentials
   psql -U quiz_user -d quiz_app
   ```

2. **Module Import Errors**
   ```bash
   # Ensure virtual environment is activated
   pip install -r requirements.txt
   ```

3. **Template Not Found**
   - Verify templates are in the `templates/` directory
   - Check Flask template configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes following PEP 8 style guide
4. Add tests for new features
5. Commit changes: `git commit -am 'Add new feature'`
6. Push to branch: `git push origin feature/new-feature`
7. Submit a pull request

## 📝 Changelog

### Version 1.2.0 (Latest)
- Added user authentication system
- Implemented PostgreSQL database
- Added quiz result tracking
- Enhanced security with password hashing

### Version 1.1.0
- Added session management
- Improved database schema
- Added API endpoints

### Version 1.0.0
- Initial Flask application
- Basic quiz functionality
- PostgreSQL integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Flask documentation and community
- PostgreSQL database system
- Werkzeug security utilities
- SQLAlchemy ORM

## 📞 Support

If you have any questions or need help:

- Open an issue on GitHub
- Email: your.email@example.com
- Check the [Flask documentation](https://flask.palletsprojects.com/)

## 🔮 Roadmap

- [ ] Add Flask-Migrate for database migrations
- [ ] Implement email verification
- [ ] Add question categories and difficulty filters
- [ ] Create admin dashboard
- [ ] Add quiz timer functionality
- [ ] Implement quiz sharing features
- [ ] Add detailed analytics and reporting
- [ ] Mobile app API integration

---

**Made with ❤️ using Flask and PostgreSQL**

*Star ⭐ this repository if you found it helpful!*
