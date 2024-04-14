from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import time

app = Flask(__name__)
app.secret_key = b'fw!pk4[2f4%#g&bh".<t'
dbconn = sqlite3.connect('db.db', check_same_thread=False)
cursor = dbconn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room TEXT NOT NULL,
    name TEXT NOT NULL,
    text TEXT NOT NULL,
    time INTEGER NOT NULL,
    read INTEGER NOT NULL DEFAULT 0
)''')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=['POST', 'GET', 'SESSION'])
def chat():
    if 'name' in request.form:
        name = request.form['name']
        session['name'] = name
    elif 'name' in session:
        name = session['name']
    else:
        return index()
    if 'room' in request.form:
        room = request.form['room']
        session['room'] = room
    elif 'room' in session:
        room = session['room']
    else:
        return index()
    if 'password' in request.form:
        password = request.form['password']
        session['password'] = password
    elif 'password' in session:
        password = session['password']
    else:
        return index()

    cursor.execute("SELECT COUNT(*) FROM rooms WHERE name = ?", [room])
    if cursor.fetchone()[0] < 1:
        cursor.execute("INSERT INTO rooms (name, password) VALUES (?, ?)", (room, password))
        dbconn.commit()
        cursor.execute("SELECT * FROM messages WHERE room = ? ORDER BY id DESC", [room])
        messages = cursor.fetchall()
        return render_template("chat.html", name=name, messages=messages, room=room)
    else:
        cursor.execute("SELECT * FROM rooms WHERE name = ?", [room])
        if cursor.fetchall()[0][2] == password:
            cursor.execute("SELECT * FROM messages WHERE room = ? ORDER BY id", [room])
            messages = cursor.fetchall()
            return render_template("chat.html", name=name, messages=messages, room=room)
        else:
            error = 'Invalid Password'
            return render_template("error.html", error=error)

@app.route('/new', methods=['POST'])
def add():
    cursor.execute("INSERT INTO messages (room, name, text, time) VALUES (?, ?, ?, ?)",
                   (session['room'], session['name'], request.form['text'], int(time.time())))
    dbconn.commit()

    return redirect(url_for('chat'))

@app.route('/logout')
def logout():
    session.clear()
    return index()

@app.route('/admin', methods=['GET'])
def admin():
    if request.args.get("command"):
        command = request.args.get("command")
        cursor.execute(command)
        output = cursor.fetchall()
    else:
        output = []
    return render_template("admin.html", output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True, threaded=True, use_reloader=True)
    dbconn.close()