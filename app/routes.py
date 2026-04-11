from flask import jsonify, request
from werkzeug.security import generate_password_hash
from app.models import User
from . import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
from .forms import LoginForm
import sqlalchemy as sa

@app.route("/")
def home():
    return render_template("LoginPage")

@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('LoginPage'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('Home'))

    return render_template('LoginPage', title='Sign In', form=form)

@app.route('/users', methods=['POST'])
def register_user():
    try:
        data = request.get_json() or request.form
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        password = data.get("password", "")
        
        # validate rquired fields
        if not username or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        #check if user/email already exits#
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User Registered Successfully"}), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500