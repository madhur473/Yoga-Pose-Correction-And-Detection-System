import os
import subprocess
import mysql.connector
from flask import Flask, jsonify, redirect, render_template, request, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path='/static', template_folder='Templates')
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Database connection function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="4730",
            database="yoga_db"
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Function to check and update streak
def check_and_update_streak(user_id, last_login):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            print("Failed to establish database connection")
            return 0

        cursor = conn.cursor()

        now = datetime.now()
        
        # Fetch current streak and last login
        cursor.execute("SELECT streak, last_login FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if result is None:
            print(f"No user found with id {user_id}")
            return 0

        current_streak, db_last_login = result

        # If last_login is None (first time login), use db_last_login
        last_login = last_login or db_last_login

        # Check if it's a new day since last login
        if last_login and now.date() > last_login.date():
            # It's a new day, increment streak
            new_streak = current_streak + 1
        elif last_login and now.date() == last_login.date():
            # Same day login, maintain current streak
            new_streak = current_streak
        else:
            # More than a day has passed, reset streak
            new_streak = 1

        # Update streak and last login
        cursor.execute("UPDATE users SET streak = %s, last_login = %s WHERE id = %s", (new_streak, now, user_id))
        conn.commit()

        return new_streak
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return 0
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()

# Route for the root URL
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/index.html')
def home():
    user_email = session.get('user_email')
    streak_count = None
    if user_email:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT streak FROM users WHERE email = %s", (user_email,))
        user = cursor.fetchone()
        if user:
            streak_count = user['streak']
        cursor.close()
        conn.close()
    return render_template('index.html', user_email=user_email, streak_count=streak_count)

@app.route('/plan.html')
def diet_plan():
    return render_template('plan.html')

@app.route('/BreathWork.html')
def BreathWork():
    return render_template('BreathWork.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html', error=None)

@app.route('/signup.html')
def signup_page():
    return render_template('signup.html', error=None)

@app.route('/Analyze.html')
def analyze():
    user_email = session.get('user_email')
    return render_template('Analyze.html', user_email=user_email)

@app.route('/contactUs.html')
def contactUs():
    user_email = session.get('user_email')
    return render_template('contactUs.html', user_email=user_email)

@app.route('/Begineer.html')
def begineer():
    return render_template('Begineer.html')

@app.route('/intermediate.html')
def intermediate():
    return render_template('intermediate.html')

@app.route('/pro.html')
def pro():
    return render_template('pro.html')

@app.route('/trainers.html')
def trainers():
    user_email = session.get('user_email')
    return render_template('trainers.html', user_email=user_email)

@app.route('/trainer-details/trainer1.html')
def trainer1():
    return render_template('trainer-details/trainer1.html')

@app.route('/trainer-details/trainer2.html')
def trainer2():
    return render_template('/trainer-details/trainer2.html')

@app.route('/trainer-details/trainer3.html')
def trainer3():
    return render_template('/trainer-details/trainer3.html')

@app.route('/7dayChallenge.html')
def challenge():
    return render_template('7dayChallenge.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match")

        hashed_password = generate_password_hash(password)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if user already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return render_template('signup.html', error="Email already registered")

            # Insert new user
            cursor.execute("INSERT INTO users (firstname, lastname, email, password, streak, last_login) VALUES (%s, %s, %s, %s, %s, %s)",
                           (firstname, lastname, email, hashed_password, 0, None))
            conn.commit()

            # Redirect to home page after successful signup
            return redirect(url_for('home'))
        except mysql.connector.Error as err:
            return render_template('signup.html', error=f"Database error: {err}")
        finally:
            if conn is not None and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('signup.html', error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = get_db_connection()
            if conn is None:
                return render_template('login.html', error="Unable to connect to the database")

            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_email'] = user['email']
                
                # Check and update streak
                new_streak = check_and_update_streak(user['id'], user['last_login'])
                
                # Set a flash message for the streak
                if new_streak > 1:
                    flash(f"You've maintained a {new_streak}-day streak! Keep it up!", 'success')
                else:
                    flash("Welcome back! You've started a new streak!", 'info')
                
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error="Invalid email or password")
        except mysql.connector.Error as err:
            return render_template('login.html', error=f"Database error: {err}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('home'))

@app.route('/execute-script', methods=['POST'])
def execute_script():
    data = request.get_json()
    script_name = data.get('scriptName')

    if not script_name:
        return jsonify({'error': 'Script name not provided'}), 400

    script_path = os.path.join(os.path.dirname(__file__), script_name)

    if not os.path.isfile(script_path):
        return jsonify({'error': 'Script not found'}), 404

    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        return jsonify({'output': result.stdout}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)