from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from extensions import db
from models import User
from flask_login import login_user, logout_user, login_required
import sqlalchemy as sa
from flask_login import current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    # Check if the user has an active session via Flask-Login
    if current_user.is_authenticated:
        user_data = UserSchema.model_validate(current_user).model_dump()
        return jsonify({
            "isAuthenticated": True,
            "user": user_data
        }), 200
        
    return jsonify({
        "isAuthenticated": false,
        "error": "Not authenticated"
    }), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = (data.get("username") or "").strip()
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = db.session.scalar(
        sa.select(User).where(User.username == username)
    )

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)

    user_data = UserSchema.model_validate(user).model_dump()

    return jsonify({
        "message": "Login successful",
        "user": user_data
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200