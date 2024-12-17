import requests
from flask import Blueprint, request, jsonify, flash, redirect, render_template, session, url_for
from models import User, db, bcrypt

auth_bp = Blueprint('auth', __name__)

# API Endpoint: Check if user exists
@auth_bp.route('/api/check_user', methods=['POST'])
def check_user():
    data = request.get_json()
    username = data.get('username')

    if User.query.filter_by(username=username).first():
        return jsonify({"exists": True}), 200
    return jsonify({"exists": False}), 200


# API Endpoint: User registration
@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists!"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful!"}), 201


# API Endpoint: User login
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials!"}), 401

    return jsonify({"message": "Login successful!", "username": username}), 200


# Render Register Page - Calls API
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Make HTTP request to the API
        response = requests.post(
            url_for('auth.api_register', _external=True),
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 201:
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash(response.json().get("error", "Registration failed!"), "error")

    return render_template('register.html')


# Render Login Page - Calls API
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Make HTTP request to the API
        response = requests.post(
            url_for('auth.api_login', _external=True),
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for('product.index'))
        else:
            flash(response.json().get("error", "Invalid credentials!"), "error")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('auth.login'))
