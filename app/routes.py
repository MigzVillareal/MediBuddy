from flask import jsonify, request, Blueprint
from werkzeug.security import generate_password_hash
from app.models import User
from . import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
import sqlalchemy as sa

api_bp = Blueprint('api', __name__)

@api_bp.route("/")
def home():
    return render_template("LoginPage")

@api_bp.route('/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )

        if user is None or not user.check_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        login_user(user)

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()

        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        password = data.get("password")

        # validate rquired fields
        if not username or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        # check dupes
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

        return jsonify({
            "message": "User registered successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})