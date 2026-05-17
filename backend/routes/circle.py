from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Circle, CircleMember, User

circle_bp = Blueprint("circle", __name__, url_prefix="/api")

@circle_bp.route("/circle", methods=["POST"])
@login_required
def create_circle():
    data = request.get_json()
    circle = Circle(circle_name=data["circle_name"])
    db.session.add(circle)
    db.session.commit()
    return jsonify({"message": "circle created", "circle_id": circle.circle_id})

@circle_bp.route("/circle/mine", methods=["GET"])
@login_required
def get_my_circle():
    member = CircleMember.query.filter_by(user_id=current_user.user_id).first()
    if not member:
        circle = Circle(circle_name=f"{current_user.username}'s circle")
        db.session.add(circle)
        db.session.commit()
        member = CircleMember(circle_id=circle.circle_id, user_id=current_user.user_id)
        db.session.add(member)
        db.session.commit()
    return jsonify({"circle_id": member.circle_id})

@circle_bp.route("/circle/add_member", methods=["POST"])
@login_required
def add_member():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.user_id == current_user.user_id:
        return jsonify({"error": "You cannot add yourself"}), 400
    existing = CircleMember.query.filter_by(
        circle_id=data["circle_id"],
        user_id=user.user_id
    ).first()
    if existing:
        return jsonify({"error": "User already in circle"}), 409
    member = CircleMember(circle_id=data["circle_id"], user_id=user.user_id)
    db.session.add(member)
    db.session.commit()
    return jsonify({"message": "member added"})

@circle_bp.route("/circle/<int:circle_id>/members", methods=["GET"])
def get_members(circle_id):
    members = CircleMember.query.filter_by(circle_id=circle_id).all()
    result = []
    for m in members:
        user = User.query.get(m.user_id)
        result.append({
            "user_id": m.user_id,
            "username": user.username if user else f"User {m.user_id}",
        })
    return jsonify(result)

@circle_bp.route("/circle/remove_member", methods=["POST"])
@login_required
def remove_member():
    data = request.get_json()
    member = CircleMember.query.filter_by(
        circle_id=data["circle_id"],
        user_id=data["user_id"]
    ).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed"})