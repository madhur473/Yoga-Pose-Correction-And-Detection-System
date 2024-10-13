import os
import subprocess

import mysql.connector
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__, static_url_path='/static', template_folder='Templates')

# Route for the root URL
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/plan.html')
def diet_plan():
    return render_template('plan.html')

@app.route('/BreathWork.html')
def BreathWork():
    return render_template('BreathWork.html')

@app.route('/login.html')
def login():
    return render_template('login.html', error=None)

@app.route('/signup.html')
def signup():
    return render_template('signup.html', error=None)

@app.route('/Analyze.html')
def analyze():
    return render_template('Analyze.html')

@app.route('/contactUs.html')
def contactUs():
    return render_template('contactUs.html')

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
    return render_template('trainers.html')

@app.route('/trainer-details/trainer1.html')
def trainer1():
    return render_template('trainer-details/trainer1.html')

@app.route('/trainer-details/trainer2.html')
def trainer2():
    return render_template('/trainer-details/trainer2.html')

@app.route('/trainer-details/trainer3.html')
def trainer3():
    return render_template('/trainer-details/trainer3.html')

# New 7-Day Challenge Routes
@app.route('/7dayChallenge.html')
def challenge():
    return render_template('7dayChallenge.html')

@app.route('/login', methods=['POST'])
def login_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')

        if email and password:
            try:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="yoga_db"
                )

                mycursor = mydb.cursor()
                mycursor.execute("SELECT id, firstname, lastname, email FROM users WHERE email = %s AND password = %s", (email, password))
                user = mycursor.fetchone()

                if user:
                    return redirect(url_for('home'))
                else:
                    return render_template("login.html", error="Invalid email or password")
            except mysql.connector.Error as err:
                return render_template("login.html", error=f"Database error: {err}")
        else:
            return render_template("login.html", error="Please provide both email and password")

    return render_template('login.html', error=None)

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
