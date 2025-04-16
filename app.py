from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB Atlas Connection
client = MongoClient("mongodb+srv://flask0001:flask0001@cluster0.qwc770i.mongodb.net/flask_auth_db?retryWrites=true&w=majority&appName=Cluster0")
db = client['flask_auth_db']
users = db.users
admins = db.admins

# ====================== HOME PAGE =========================
@app.route('/')
def home():
    # If the user is logged in, redirect to the dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    # If the admin is logged in, redirect to the admin dashboard
    elif 'admin' in session:
        return redirect(url_for('admin_dashboard'))
    # If no one is logged in, show the homepage with login and register options
    return render_template('home.html')

# ====================== USER AUTH =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if users.find_one({'email': email}):
            flash('Email already exists!')
            return redirect(url_for('register'))

        users.insert_one({'name': name, 'email': email, 'password': password})
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']
        user = users.find_one({'email': email})

        if user and check_password_hash(user['password'], password_input):
            session['user'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', name=session['user'])
    return redirect(url_for('login'))

# ====================== ADMIN AUTH =========================
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']
        admin = admins.find_one({'username': username})

        if admin and check_password_hash(admin['password'], password_input):
            session['admin'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!')

    return render_template('admin_login.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        flash('Admin access only.')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        search_name = request.form['search']
        all_users = users.find({'name': {'$regex': search_name, '$options': 'i'}})
    else:
        all_users = users.find()

    return render_template('admin_dashboard.html', users=all_users)

@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    if 'admin' not in session:
        flash('Unauthorized access.')
        return redirect(url_for('admin_login'))

    users.delete_one({'_id': ObjectId(user_id)})
    flash('User deleted successfully!')
    return redirect(url_for('admin_dashboard'))

# ====================== LOGOUT =========================
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Use Render's port or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
