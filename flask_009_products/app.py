from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Charan@#1998'
app.config['MYSQL_DB'] = 'flask_001'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html', title='Home', active_page='home')


@app.route('/about')
def about():
    return render_template('about.html', title='About', active_page='about')


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact', active_page='contact')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            flash('You have successfully registered!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cursor.close()

    return render_template('register.html', title='Register', active_page='register')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('admin_success'))
        else:
            return render_template('admin.html', title='Admin', error='Invalid credentials. Please try again.', active_page='admin')
    return render_template('admin.html', title='Admin', active_page='admin')


@app.route('/admin_success')
def admin_success():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username, password FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin_success.html', title='Admin Success', users=users, active_page='admin')


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['username'] = username
            return redirect(url_for('user_success'))
        else:
            return render_template('user.html', title='User', error='Invalid credentials. Please try again.')
    return render_template('user.html', title='User', active_page='user')


@app.route('/user_success')
def user_success():
    if 'username' not in session:
        return redirect(url_for('user'))
    username = session['username']
    return render_template('user_success.html', title='User Success', username=username, active_page='user_success')


@app.route('/users')
def list_users():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username, password FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('users.html', title='All Users', users=users, active_page='users')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET username = %s, password = %s WHERE id = %s", (username, hashed_password, user_id))
        mysql.connection.commit()
        cursor.close()
        flash('User updated successfully!', 'success')
        return redirect(url_for('list_users'))

    return render_template('edit_user.html', title='Edit User', user=user, active_page='edit_user')


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('list_users'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
