from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from schemas import UserSchema
from models import User
from app.extensions import db

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

# reduce pydantics serialization code redundancy and drier code
def get_user_data(user):
    return UserSchema.model_validate(user).model_dump()

# for fetching public data, searching other users
@user_bp.route("/<int:user_id>", methods = ["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(get_user_data(user)), 200

# returns info about currently logged in user
@user_bp.route('/me', methods=['GET'])
@login_required
def get_me():
    return jsonify(get_user_data(current_user)), 200

# endpoint for profile management: GET(fetch) and POST(update) 
@user_bp.route("/profile", methods=["POST"])
@login_required
def profile():
    if request.method == "GET":
        user_data = UserSchema.model_validate(current_user)
        return jsonify(user_data.model_dump()), 200

    if request.method == "POST":
        data = request.get_json()
        
        # update logic
        current_user.first_name = data.get("first_name", current_user.first_name)
        current_user.last_name = data.get("last_name", current_user.last_name)
        
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200