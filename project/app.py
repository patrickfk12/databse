
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'project'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM data')
        records = cursor.fetchall()
        return render_template('dashboard.html', records=records)
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST' and 'name' in request.form:
        name = request.form['name']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO data (name) VALUES (%s)', [name])
        mysql.connection.commit()
        return redirect(url_for('dashboard'))

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        name = request.form['name']
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE data SET name = %s WHERE id = %s', (name, id))
        mysql.connection.commit()
        return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM data WHERE id = %s', [id])
    mysql.connection.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
