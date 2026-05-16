from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash
from app.models import User
from app.extensions import db
from flask_login import login_user, login_required, logout_user, current_user
import sqlalchemy as sa

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = (data.get("username") or "").strip()
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing fields"}), 400
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)
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

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

@auth_bp.route('/me', methods=['GET'])
def get_me():
    if current_user.is_authenticated:
        return jsonify({
            "id": current_user.id,
            "username": current_user.username,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
        }), 200
    return jsonify({"error": "Not logged in"}), 401

@auth_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()

    first_name = (data.get("first_name") or "").strip()
    last_name  = (data.get("last_name") or "").strip()

    current_user.first_name = first_name
    current_user.last_name  = last_name

    db.session.commit()

    return jsonify({"message": "Profile updated"})

@auth_bp.route('/profile', methods=['GET', 'POST', 'OPTIONS'])
def profile():

    if request.method == "OPTIONS":
        return make_response("", 200)

    if request.method == "GET":
        return jsonify({
            "username": current_user.username,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
        })

    if request.method == "POST":
        data = request.get_json()

        current_user.first_name = data.get("first_name")
        current_user.last_name = data.get("last_name")

        db.session.commit()

        return jsonify({"message": "Profile updated"})