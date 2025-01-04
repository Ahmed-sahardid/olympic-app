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
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

# User class for login management
class User(UserMixin):
    def __init__(self, id, name, email, password_hash):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['name'], user_data['email'], user_data['password_hash'])
    return None

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        age = int(request.form['age'])
        experience = request.form['experience']
        goals = request.form['goals']

        # Hash password before saving to DB
        password_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                age INTEGER NOT NULL,
                experience TEXT DEFAULT 'beginner',
                goals TEXT DEFAULT 'strength',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, age, experience, goals) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, password_hash, age, experience, goals))
        conn.commit()
        conn.close()

        flash('User created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user_data = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user_data:
            if check_password_hash(user_data['password_hash'], password):
                user = User(user_data['id'], user_data['name'], user_data['email'], user_data['password_hash'])
                login_user(user)  # Logs in the user
                return redirect(url_for('home'))
            else:
                flash('Invalid password', 'danger')
        else:
            flash('Invalid email', 'danger')

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Home Route
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    program = None
    if request.method == "POST":
        name = request.form.get("name")
        age = int(request.form.get("age"))
        experience = request.form.get("experience")
        goals = request.form.get("goals")
        program = generate_program(age, experience, goals)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, age, experience, goals) VALUES (?, ?, ?, ?)",
            (name, age, experience, goals),
        )
        user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO programs (user_id, program) VALUES (?, ?)",
            (user_id, "\n".join(program)),
        )
        conn.commit()
        conn.close()

    return render_template("index.html", program=program)

# Programs Route to view all programs
@app.route("/programs")
@login_required
def programs():
    conn = get_db_connection()
    programs_data = conn.execute("""
        SELECT users.name, users.age, users.experience, users.goals, programs.program, programs.created_at
        FROM programs
        JOIN users ON programs.user_id = users.id
        ORDER BY programs.created_at DESC
    """).fetchall()
    conn.close()

    return render_template("programs.html", programs=programs_data)

# Helper function to generate program
def generate_program(age, experience, goals):
    program = []
    if experience == "beginner":
        program = [
            "Week 1: Basic technique drills and light lifts",
            "Week 2: Increase weight gradually; focus on squats and cleans",
            "Week 3: Add snatch practice and overhead presses",
            "Week 4: Combine all lifts with moderate intensity",
        ]
    elif experience == "intermediate":
        program = [
            "Week 1: Heavy back squats and snatch drills",
            "Week 2: Work on clean & jerk variations",
            "Week 3: Emphasize volume with moderate intensity",
            "Week 4: Perform mock competition lifts with increased intensity",
        ]
    elif experience == "advanced":
        program = [
            "Week 1: High-intensity max-out sessions",
            "Week 2: Rest and recovery-focused drills",
            "Week 3: Combine volume with heavy lifts",
            "Week 4: Peak with a mock competition or PR day",
        ]

    if goals == "strength":
        program.append("Add extra squats and deadlift variations each week.")
    elif goals == "technique":
        program.append("Focus on lower weights and perfecting form.")
    elif goals == "endurance":
        program.append("Include circuit training with Olympic lifts.")
    return program

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))  # Use 5002 for local testing
    app.run(host="0.0.0.0", port=port)
