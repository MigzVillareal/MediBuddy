from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.models import User
from app import db
from flask_login import login_user, login_required, logout_user, current_user
import sqlalchemy as sa

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
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

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.user_id,
            "username": user.username,
            "email": user.email
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

# @auth_bp.route('/me', methods=['GET'])
# @login_required
# def me():
#     return jsonify({
#         "id": current_user.user_id,
#         "username": current_user.username,
#         "email": current_user.email
#     })