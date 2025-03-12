from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quizzes = db.relationship('Quiz', backref='category', lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    questions = db.relationship('Question', backref='quiz', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    options = db.relationship('Option', backref='question', lazy=True)
    correct_option_id = db.Column(db.Integer, nullable=False)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    quiz = db.relationship('Quiz')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Username already exists.')
            return redirect(url_for('signup'))
        
        if email_exists:
            flash('Email already registered.')
            return redirect(url_for('signup'))
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    return render_template('dashboard.html', categories=categories)

@app.route('/category/<int:category_id>')
@login_required
def category(category_id):
    category = Category.query.get_or_404(category_id)
    quizzes = Quiz.query.filter_by(category_id=category_id).all()
    return render_template('category.html', category=category, quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>')
@login_required
def quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz.html', quiz=quiz, questions=questions)

@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    score = 0
    for question in questions:
        selected_option = request.form.get(f'question_{question.id}')
        if selected_option and int(selected_option) == question.correct_option_id:
            score += 1
    
    # Save score
    new_score = Score(user_id=current_user.id, quiz_id=quiz_id, score=score)
    db.session.add(new_score)
    db.session.commit()
    
    flash(f'Your score: {score}/{len(questions)}')
    return redirect(url_for('quiz_results', quiz_id=quiz_id))

@app.route('/leaderboard')
def leaderboard():
    scores = db.session.query(
        User.username,
        User.email,
        Quiz.title,
        Score.score,
        Score.date
    ).join(Score, User.id == Score.user_id).join(
        Quiz, Score.quiz_id == Quiz.id
    ).order_by(Score.score.desc()).limit(20).all()
    
    return render_template('leaderboard.html', scores=scores)

# Initialize database with sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Category.query.first() is None:
            # Create categories
            tech = Category(name='Technology')
            general = Category(name='General Knowledge')
            science = Category(name='Science')
            
            db.session.add_all([tech, general, science])
            db.session.commit()
            
            # Create quizzes
            tech_quiz = Quiz(title='Web Development Basics', category_id=tech.id)
            general_quiz = Quiz(title='World Trivia', category_id=general.id)
            science_quiz = Quiz(title='Basic Physics', category_id=science.id)
            
            db.session.add_all([tech_quiz, general_quiz, science_quiz])
            db.session.commit()
            
            # Create questions for tech quiz
            q1 = Question(content='What does HTML stand for?', quiz_id=tech_quiz.id, correct_option_id=1)
            db.session.add(q1)
            db.session.commit()
            
            # Options for q1
            o1 = Option(content='Hypertext Markup Language', question_id=q1.id)
            o2 = Option(content='Hyperlinks and Text Markup Language', question_id=q1.id)
            o3 = Option(content='Home Tool Markup Language', question_id=q1.id)
            o4 = Option(content='Hypertext Machine Language', question_id=q1.id)
            
            db.session.add_all([o1, o2, o3, o4])
            db.session.commit()
            
            # More questions for tech quiz
            q2 = Question(content='Which language is used for styling web pages?', quiz_id=tech_quiz.id, correct_option_id=2)
            db.session.add(q2)
            db.session.commit()
            
            # Options for q2
            o5 = Option(content='HTML', question_id=q2.id)
            o6 = Option(content='CSS', question_id=q2.id)
            o7 = Option(content='JavaScript', question_id=q2.id)
            o8 = Option(content='PHP', question_id=q2.id)
            
            db.session.add_all([o5, o6, o7, o8])
            db.session.commit()
            
            # Add more questions and options for other quizzes
            # General Knowledge Quiz
            q3 = Question(content='What is the capital of France?', quiz_id=general_quiz.id, correct_option_id=1)
            db.session.add(q3)
            db.session.commit()
            
            o9 = Option(content='Paris', question_id=q3.id)
            o10 = Option(content='London', question_id=q3.id)
            o11 = Option(content='Berlin', question_id=q3.id)
            o12 = Option(content='Rome', question_id=q3.id)
            
            db.session.add_all([o9, o10, o11, o12])
            db.session.commit()
            
            # Science Quiz
            q4 = Question(content='What is the chemical symbol for water?', quiz_id=science_quiz.id, correct_option_id=2)
            db.session.add(q4)
            db.session.commit()
            
            o13 = Option(content='WA', question_id=q4.id)
            o14 = Option(content='H2O', question_id=q4.id)
            o15 = Option(content='HO', question_id=q4.id)
            o16 = Option(content='W', question_id=q4.id)
            
            db.session.add_all([o13, o14, o15, o16])
            db.session.commit()

# Add this route after the submit_quiz route

@app.route('/results/<int:quiz_id>')
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user_scores = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).order_by(Score.date.desc()).all()
    
    # Get the total number of questions for this quiz
    total_questions = Question.query.filter_by(quiz_id=quiz_id).count()
    
    return render_template('results.html', quiz=quiz, scores=user_scores, total_questions=total_questions)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)