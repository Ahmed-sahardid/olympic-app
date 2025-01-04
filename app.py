import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a secure key for session management
login_manager = LoginManager()
login_manager.init_app(app)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# User class for login management
class User(UserMixin):
    def __init__(self, id, name, email, password_hash, age, experience, goals):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.age = age
        self.experience = experience
        self.goals = goals

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['name'], user_data['email'], user_data['password_hash'], user_data['age'], user_data['experience'], user_data['goals'])
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                password_hash TEXT,
                age INTEGER NOT NULL,
                experience TEXT DEFAULT 'beginner',
                goals TEXT DEFAULT 'strength',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('INSERT INTO users (name, email, password_hash, age) VALUES (?, ?, ?, ?)',
                       (name, email, password_hash, request.form['age']))
        conn.commit()
        conn.close()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user_data = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['name'], user_data['email'], user_data['password_hash'], user_data['age'], user_data['experience'], user_data['goals'])
            login_user(user)
            return redirect(url_for('main'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/main')
@login_required
def main():
    return render_template('main.html')

@app.route('/weightlifting')
@login_required
def weightlifting():
    return render_template('weightlifting.html')

@app.route('/blog')
@login_required
def blog():
    return render_template('blog.html')

@app.route('/blog/ask', methods=['GET', 'POST'])
@login_required
def ask_for_advice():
    if request.method == 'POST':
        question = request.form['question']
        flash('Your question has been submitted.', 'success')
        return redirect(url_for('blog'))
    return render_template('ask_advice.html')

if __name__ == '__main__':
    app.run(debug=True)
