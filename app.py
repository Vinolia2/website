from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_session import Session
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ADMIN_CREDENTIALS = {
    'Admin': 'admin123',
    'vino': '12345'
}

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mail TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    mail = request.form['mail']
    date_str = request.form['date']

    appointment_date = datetime.strptime(date_str, '%Y-%m-%d')
    current_date = datetime.now()

    if appointment_date < current_date:
        flash("Error: Appointment date cannot be in the past.")
        return redirect(url_for('index'))

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, mail, date) VALUES (?, ?, ?)', (name, mail, date_str))
        conn.commit()

    flash(f"Appointment confirmed for {name} on {date_str}. A confirmation email will be sent to {mail}.")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if ADMIN_CREDENTIALS.get(username) == password:
            session['logged_in'] = True
            flash('Successfully logged in!')
            return redirect(url_for('result'))
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/result')
def result():
    if not session.get('logged_in'):
        flash('You need to log in to access this page.')
        return redirect(url_for('login'))
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        data = cursor.fetchall()

    return render_template('result.html', data=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
