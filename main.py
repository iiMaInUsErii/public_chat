from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime
import sqlite3
import time

global access
global login
global password
app = Flask(__name__)
app.secret_key = b'fw!pk4[2f4%#g&bh".<t'
dbconn = sqlite3.connect('users.db', check_same_thread=False)
cursor = dbconn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    text TEXT NOT NULL,
    time INT NOT NULL
)''')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    name = request.form['name']
    cursor.execute("SELECT * FROM messages ORDER BY time")
    messages = cursor.fetchall()
    return render_template("chat.html", name=name, messages=messages)

@app.route('/new', methods=['POST'])
def add():
    name = request.form['name']
    text = request.form['text']

    insert = f"INSERT INTO messages (name, text, time) VALUES (?, ?, ?)"
    cursor.execute(insert, (name, text, int(time.time())))
    dbconn.commit()

    return render_template("add.html", name=name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True, threaded=True, use_reloader=True)
    dbconn.close()