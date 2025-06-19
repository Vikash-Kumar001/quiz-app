# QuizApp 🧠

A comprehensive, full-featured web application for creating, taking, and managing quizzes. Built with Flask, PostgreSQL, SQLAlchemy, and Alembic for robust database migrations. Features secure user authentication, real-time scoring, and seamless deployment to [Render](https://render.com/).

## ✨ Features

- **User Registration & Login**: Secure authentication with hashed passwords and session management
- **Quiz Creation & Management**: Users (optionally admins) can create quizzes with multiple questions and options
- **Quiz Participation**: Interactive quiz-taking experience with real-time feedback
- **Multiple Question Types**: Supports multiple-choice (single or multiple answers), text input, and more
- **Real-time Scoring**: Automatic calculation and display of quiz results
- **Quiz Attempts & Tracking**: Complete history of attempts and scores for each user
- **Results Viewing**: Detailed results analysis after each attempt
- **Admin Interface**: (Optional) Comprehensive management of users, quizzes, questions, and results
- **Category Support**: Organize quizzes by categories and difficulty levels
- **Time Limits**: Configurable time limits per quiz with countdown timer
- **Database Migrations**: Robust migration system via Alembic and Flask-Migrate
- **RESTful API Endpoints**: Easily extensible for frontend frameworks or mobile apps
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Security Features**: Environment variables for secrets, CSRF protection, and secure password handling
- **Easy Deployment**: One-click deploy to Render with automatic migrations

## 🚀 Demo

[Live Demo](https://your-quiz-app-demo.com) (Replace with actual demo link)

## 📱 Screenshots

```
[Add screenshots of your quiz app here]
- Login/Registration page
- Quiz dashboard
- Quiz creation interface
- Quiz in progress
- Results page
- Admin panel
- Mobile view
```

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask
- **Database**: PostgreSQL (12.0+)
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Migrations**: Flask-Migrate (Alembic)
- **Authentication**: Flask-Login, Werkzeug Security
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Production Server**: Gunicorn
- **Deployment**: Render
- **Session Management**: Flask Sessions

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- Python 3.8 or higher
- PostgreSQL (version 12.0 or higher)
- pip (Python package manager)
- Git

## ⚡ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/quizapp.git
cd quizapp
```

### 2. Create Virtual Environment & Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set up PostgreSQL Database

```bash
# Create database (replace with your credentials)
psql -U postgres
CREATE DATABASE quizapp_db;
CREATE USER quiz_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE quizapp_db TO quiz_user;
\q
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://quiz_user:your_password@localhost:5432/quizapp_db

# Optional Configuration
QUESTIONS_PER_QUIZ=10
QUIZ_TIME_LIMIT=1800  # 30 minutes in seconds
```

### 5. Database Setup & Migrations

**For a fresh setup:**

```bash
# Initialize migration repository (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

**If you have an existing DB with tables, but no Alembic history:**

```bash
flask db stamp head
```

### 6. Running Locally

```bash
flask run
# or
python app.py
```

App will be available at [http://localhost:5000](http://localhost:5000)

## 🏗️ Project Structure

```
quizapp/
│
├── app.py                  # Main application file
├── models.py              # Database models
├── routes.py              # Application routes
├── forms.py               # WTForms definitions
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── .env.example          # Environment variables template
├── README.md             # This file
│
├── migrations/           # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── auth/
│   ├── quiz/
│   └── admin/
│
├── static/              # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
└── tests/               # Test files
    ├── test_models.py
    ├── test_routes.py
    └── conftest.py
```

## 🔧 Dependencies

### Main Dependencies (`requirements.txt`)

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5
Flask-Login==0.6.2
Flask-WTF==1.1.1
WTForms==3.0.1
psycopg2-binary==2.9.7
Werkzeug==2.3.7
python-dotenv==1.0.0
gunicorn==21.2.0
```

### Development Dependencies

```txt
pytest==7.4.0
pytest-flask==1.2.0
pytest-cov==4.1.0
black==23.7.0
flake8==6.0.0
```

## 📊 Database Schema Overview

### Core Tables

The application uses the following main tables:

- **users**: Stores user credentials, emails, and registration info
- **quizzes**: Quiz metadata (title, description, creator, time limit, etc.)
- **categories**: Quiz categories for organization
- **questions**: Each question belongs to a quiz
- **question_options**: Options for multiple-choice questions
- **quiz_attempts**: Stores each attempt a user makes on a quiz
- **user_answers**: Stores user's answers to each question in an attempt
- **results**: Final results for each quiz attempt

### Database Schema Diagram

```
users ──< quiz_attempts ──< user_answers >── questions >── quizzes
   |         |                                 |              |
   |         └────────────── results ──────────┘              |
   |                                                           |
   └─────────────────────── created_quizzes ──────────────────┘

questions ──< question_options
quizzes ──< categories
```

### Detailed Schema

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Categories Table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quizzes Table
CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    creator_id INTEGER REFERENCES users(id),
    time_limit INTEGER DEFAULT 1800, -- seconds
    max_attempts INTEGER DEFAULT 0, -- 0 = unlimited
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions Table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'multiple_choice',
    points INTEGER DEFAULT 1,
    explanation TEXT,
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Question Options Table
CREATE TABLE question_options (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    option_text VARCHAR(500) NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    order_index INTEGER
);

-- Quiz Attempts Table
CREATE TABLE quiz_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    quiz_id INTEGER REFERENCES quizzes(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    time_taken INTEGER, -- seconds
    is_completed BOOLEAN DEFAULT FALSE
);

-- User Answers Table
CREATE TABLE user_answers (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id),
    selected_option_id INTEGER REFERENCES question_options(id),
    text_answer TEXT,
    is_correct BOOLEAN,
    points_earned INTEGER DEFAULT 0
);

-- Results Table
CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    quiz_id INTEGER REFERENCES quizzes(id),
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    total_points INTEGER NOT NULL,
    earned_points INTEGER NOT NULL,
    percentage DECIMAL(5,2),
    grade VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Usage

### User Authentication

1. **Register**: Navigate to `/register` to create a new account
2. **Login**: Use `/login` to access your account
3. **Dashboard**: View available quizzes and your statistics

### Taking a Quiz

1. **Browse Quizzes**: Select from available quiz categories
2. **Start Quiz**: Click to begin, timer starts automatically
3. **Answer Questions**: Select your answers for each question
4. **Submit**: Complete the quiz to see your results
5. **Review**: Check your score, correct answers, and explanations

### Creating Quizzes (Admin/Creator)

1. **Access Creator Panel**: Navigate to `/create-quiz`
2. **Set Quiz Details**: Title, description, category, time limit
3. **Add Questions**: Create questions with multiple options
4. **Configure Settings**: Set difficulty, points, explanations
5. **Publish**: Make quiz available to users

## 🔌 API Endpoints

### Authentication Endpoints

```python
# Authentication
GET  /login                    # Display login form
POST /login                    # Process login
GET  /register                 # Display registration form  
POST /register                 # Process registration
GET  /logout                   # Logout user
```

### Quiz Management Endpoints

```python
# Quiz Management
GET  /dashboard               # User dashboard
GET  /quizzes                # List all quizzes
GET  /quizzes/<int:quiz_id>  # Quiz details
POST /quizzes/<int:quiz_id>/start  # Start quiz attempt
POST /quizzes/<int:quiz_id>/submit # Submit quiz answers
GET  /results/<int:attempt_id>     # View specific result

# Quiz Creation (Admin/Creator)
GET  /create-quiz            # Quiz creation form
POST /create-quiz            # Create new quiz
GET  /edit-quiz/<int:id>     # Edit quiz form
POST /edit-quiz/<int:id>     # Update quiz
DELETE /delete-quiz/<int:id> # Delete quiz
```

### API Endpoints (JSON)

```python
# JSON API Endpoints
GET  /api/quizzes            # Get all quizzes (JSON)
GET  /api/quizzes/<int:id>   # Get specific quiz (JSON)
POST /api/quiz/submit        # Submit quiz via API
GET  /api/user/stats         # Get user statistics
GET  /api/categories         # Get all categories
GET  /api/leaderboard        # Get leaderboard data
```

## 🚀 Deployment

### Render Deployment (Recommended)

1. **Push your code to GitHub**

2. **Create a new Web Service on [Render](https://render.com/)**
   - Connect your GitHub repository
   - Set environment variables in the Render dashboard

3. **Configure render.yaml** (recommended for automatic migrations):

```yaml
services:
  - type: web
    name: quizapp
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: quizapp-db
          property: connectionString
    preDeploy:
      - flask db upgrade

databases:
  - name: quizapp-db
    databaseName: quizapp
    plan: free
```

4. **Deploy!**
   - Render will automatically install dependencies and run DB migrations
   - Your app will be live on your Render URL

### Heroku Deployment

```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-quiz-app

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Run migrations
heroku run flask db upgrade
```

### VPS Deployment (Ubuntu)

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip postgresql nginx

# Set up application
git clone your-repo
cd quizapp
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
flask db upgrade

# Start with Gunicorn
pip3 install gunicorn
gunicorn --bind 0.0.0.0:8000 app:app
```

## ⚙️ Configuration

### Environment Variables

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production  # or development
SECRET_KEY=your-super-secret-key

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/quizapp_db

# Quiz Configuration
QUESTIONS_PER_QUIZ=10
QUIZ_TIME_LIMIT=1800  # 30 minutes in seconds
MAX_QUIZ_ATTEMPTS=3

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Admin Configuration
ADMIN_EMAIL=admin@yourapp.com
```

### Example .env.example

```env
FLASK_APP=app.py
FLASK_ENV=production
DATABASE_URL=postgresql://username:password@host:port/dbname
SECRET_KEY=your-secret-key
QUESTIONS_PER_QUIZ=10
QUIZ_TIME_LIMIT=1800
MAX_QUIZ_ATTEMPTS=3
```

## 🧪 Testing

### Running Tests

```bash
# Install testing dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_models.py

# Run tests with verbose output
python -m pytest -v
```

### Test Structure

```python
# Example test file structure
tests/
├── conftest.py          # Test configuration
├── test_models.py       # Model tests
├── test_routes.py       # Route tests
├── test_auth.py         # Authentication tests
└── test_quiz.py         # Quiz functionality tests
```

## 🛡️ Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing with salt
- **Session Management**: Secure session handling with Flask-Login
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection attacks
- **CSRF Protection**: Cross-Site Request Forgery protection with Flask-WTF
- **Input Validation**: Server-side validation for all user inputs
- **Environment Variables**: Sensitive data stored in environment variables
- **Rate Limiting**: (Optional) Implement rate limiting for API endpoints
- **Secure Headers**: Security headers for production deployment

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Verify database credentials
   psql -U quiz_user -d quizapp_db
   
   # Check DATABASE_URL format
   echo $DATABASE_URL
   ```

2. **Migration Issues**
   ```bash
   # Reset migrations (development only)
   rm -rf migrations/
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. **Module Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. **Template Not Found**
   - Verify templates are in the correct `templates/` directory
   - Check Flask template configuration in `app.py`

5. **Static Files Not Loading**
   - Ensure static files are in `static/` directory
   - Check Flask static folder configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes following PEP 8 style guide
4. Add tests for new features
5. Run tests: `python -m pytest`
6. Commit changes: `git commit -am 'Add new feature'`
7. Push to branch: `git push origin feature/new-feature`
8. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages
- Ensure all tests pass before submitting PR

## 📝 Changelog

### Version 2.0.0 (Latest)
- Added comprehensive database schema with migrations
- Implemented Flask-Login for user management
- Added quiz categories and difficulty levels
- Enhanced admin interface
- Added time limits and attempt tracking
- Improved API endpoints with JSON responses
- Added comprehensive testing suite

### Version 1.2.0
- Added user authentication system
- Implemented PostgreSQL database
- Added quiz result tracking
- Enhanced security with password hashing

### Version 1.1.0
- Added session management
- Improved database schema
- Added basic API endpoints

### Version 1.0.0
- Initial Flask application
- Basic quiz functionality
- PostgreSQL integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [PostgreSQL](https://www.postgresql.org/) - Database system
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit and ORM
- [Render](https://render.com/) - Deployment platform
- [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool
- Flask-Login, Flask-WTF, and other Flask extensions

## 📞 Support

If you have any questions or need help:

- **GitHub Issues**: [Open an issue](https://github.com/yourusername/quizapp/issues)
- **Email**: your.email@example.com
- **Documentation**: Check the [Flask documentation](https://flask.palletsprojects.com/)
- **Community**: Join our [Discord server](https://discord.gg/yourserver)

## 🔮 Roadmap & Future Features

- [ ] **Enhanced Admin Dashboard**
  - [ ] User management interface
  - [ ] Quiz analytics and statistics
  - [ ] Bulk question import/export

- [ ] **Advanced Quiz Features**
  - [ ] Question randomization
  - [ ] Conditional logic (branching questions)
  - [ ] Media support (images, videos, audio)
  - [ ] LaTeX math equation support

- [ ] **User Experience Improvements**
  - [ ] Dark mode theme
  - [ ] Quiz bookmarking and favorites
  - [ ] Social sharing of results
  - [ ] Leaderboards and achievements

- [ ] **Integration & API**
  - [ ] Single Sign-On (SSO) integration
  - [ ] Webhook support for external systems
  - [ ] Mobile app API optimization
  - [ ] Export results to CSV/PDF

- [ ] **Performance & Scaling**
  - [ ] Redis caching layer
  - [ ] Background task processing
  - [ ] CDN integration for static assets
  - [ ] Database optimization and indexing

- [ ] **Monitoring & Analytics**
  - [ ] Application performance monitoring
  - [ ] User behavior analytics
  - [ ] Error tracking and reporting
  - [ ] A/B testing framework

---

**Made with ❤️ using Flask, PostgreSQL, and modern web technologies**

*Star ⭐ this repository if you found it helpful!*

## 🚀 Quick Start Commands

```bash
# One-line setup for development
git clone https://github.com/yourusername/quizapp.git && cd quizapp && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Quick database setup
flask db init && flask db migrate -m "Initial migration" && flask db upgrade

# Run the app
flask run
```

---

*For more detailed documentation, visit our [Wiki](https://github.com/yourusername/quizapp/wiki)*
