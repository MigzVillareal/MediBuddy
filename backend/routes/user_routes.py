from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import User
from extensions import db

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

def get_user_data(user):
    """
    Helper function to manually serialize the User object.
    Replaces Pydantic/UserSchema.model_dump()
    """
    return {
        "id": user.id,
        "username": user.username,
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        # Add any other fields from your User model you want sent to the frontend
    }

# For fetching public data, searching other users
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(get_user_data(user)), 200

# Returns info about currently logged in user
@user_bp.route('/me', methods=['GET'])
@login_required
def get_me():
    return jsonify(get_user_data(current_user)), 200

# Endpoint for profile management: GSET(fetch) and POST(update)
@user_bp.route("/profile", methods=["GET", "POST"]) # Fixed: Added "GET" to accepted methods
@login_required
def profile():
    if request.method == "GET":
        # manually serialize using helper function
        return jsonify(get_user_data(current_user)), 200

    if request.method == "POST":
        data = request.get_json()
        
        # update logic
        current_user.first_name = data.get("first_name", current_user.first_name)
        current_user.last_name = data.get("last_name", current_user.last_name)
        
        db.session.commit()
        
        # Return the updated user data back to the frontend so it can refresh its state
        return jsonify({
            "message": "Profile updated successfully",
            "user": get_user_data(current_user)
        }), 200