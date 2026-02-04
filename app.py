from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from flask import send_from_directory


app = Flask(__name__)
app.secret_key = "mysecretkey"


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Create database
def create_db():
    conn = sqlite3.connect('database.db')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT, password TEXT)''')

    conn.execute('''CREATE TABLE IF NOT EXISTS memories
                 (filename TEXT, album TEXT)''')

    conn.close()

create_db()

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/gallery')
        else:
            return "Invalid Username or Password"

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')





@app.route('/delete/<filename>')
def delete_file(filename):

    conn = sqlite3.connect('database.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS memories
             (filename TEXT, album TEXT)''')

    conn.commit()
    conn.close()

    # Delete file from uploads folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




@app.route('/gallery')
def gallery():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT filename, album FROM memories")
    files = cursor.fetchall()

    conn.close()

    return render_template('gallery.html', files=files)



@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':

        file = request.files['file']
        album = request.form['album']

        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = sqlite3.connect('database.db')
            conn.execute("INSERT INTO memories VALUES (?, ?)", (filename, album))
            conn.commit()
            conn.close()

            return redirect('/gallery')

    return render_template('upload.html')



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)



