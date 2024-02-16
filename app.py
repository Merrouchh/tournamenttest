from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)
db = sqlite3.connect('tournament.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, epic_id TEXT)')
db.commit()

# Maximum number of registrations
MAX_REGISTRATIONS = 60

@app.route('/')
def home():
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    remaining_spots = MAX_REGISTRATIONS - len(users)
    return render_template('index.html', users=users, remaining_spots=remaining_spots)

@app.route('/register', methods=['POST'])
def register():
    cursor.execute('SELECT COUNT(*) FROM users')
    registrations = cursor.fetchone()[0]
    if registrations >= MAX_REGISTRATIONS:
        return "Registration limit reached"

    name = request.form.get('name')
    email = request.form.get('email')
    epic_id = request.form.get('epic_id')

    cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
    existing_user = cursor.fetchone()
    if existing_user:
        return "Name already registered"

    cursor.execute('INSERT INTO users (name, email, epic_id) VALUES (?, ?, ?)', (name, email, epic_id))
    db.commit()

    return redirect(url_for('home'))

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('home'))
    else:
        return render_template('index.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return render_template('admin_dashboard.html', users=users)


@app.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        epic_id = request.form.get('epic_id')

        cursor.execute('UPDATE users SET name = ?, email = ?, epic_id = ? WHERE id = ?', (name, email, epic_id, user_id))
        db.commit()

        return redirect(url_for('admin_dashboard'))
    else:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        return render_template('edit_user.html', user=user)

@app.route('/admin/delete/<int:user_id>')
def delete_user(user_id):
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
