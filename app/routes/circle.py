from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Circle, CircleMember, User

circle_bp = Blueprint("circle", __name__, url_prefix="/api")

@circle_bp.route("/circle", methods=["POST"])
def create_circle():
    data = request.get_json()

    circle = Circle(
        name=data["name"],
        owner_id=data["owner_id"]
    )

    db.session.add(circle)
    db.session.commit()

    return jsonify({"message": "circle created", "circle_id": circle.id})

# ─────────────────────────────────────────────────────────────────
# ADDED: returns the logged-in user's circle, creating it if needed
# ─────────────────────────────────────────────────────────────────
@circle_bp.route("/circle/mine", methods=["GET"])
@login_required
def get_my_circle():
    circle = Circle.query.filter_by(owner_id=current_user.id).first()
    if not circle:
        circle = Circle(name=f"{current_user.username}'s circle", owner_id=current_user.id)
        db.session.add(circle)
        db.session.commit()
    return jsonify({"circle_id": circle.id})


@circle_bp.route("/circle/add_member", methods=["POST"])
@login_required
def add_member():
    data = request.get_json()

    user = User.query.filter_by(username=data["username"]).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.id == current_user.id:
        return jsonify({"error": "You cannot add yourself to your circle"}), 400

    existing = CircleMember.query.filter_by(
        circle_id=data["circle_id"],
        user_id=user.id
    ).first()
    if existing:
        return jsonify({"error": "User is already in this circle"}), 409

    member = CircleMember(
        circle_id=data["circle_id"],
        user_id=user.id,
        permission=data["permission"]
    )

    db.session.add(member)
    db.session.commit()

    return jsonify({"message": "member added"})

# ─────────────────────────────────────────────────────────────────
# CHANGED: now joins User table to return username in each member
# ─────────────────────────────────────────────────────────────────
@circle_bp.route("/circle/<int:circle_id>/members", methods=["GET"])
def get_members(circle_id):
    members = CircleMember.query.filter_by(circle_id=circle_id).all()

    result = []
    for m in members:
        user = User.query.get(m.user_id)
        result.append({
            "user_id": m.user_id,
            "username": user.username if user else f"User {m.user_id}",  # ADDED
            "permission": m.permission
        })

    return jsonify(result)

# ─────────────────────────────────────────────────────────────────
# ADDED: update an existing member's permission
# ─────────────────────────────────────────────────────────────────
@circle_bp.route("/circle/update_permission", methods=["POST"])
def update_permission():
    data = request.get_json()

    member = CircleMember.query.filter_by(
        circle_id=data["circle_id"],
        user_id=data["user_id"]
    ).first()

    if not member:
        return jsonify({"error": "Member not found"}), 404

    member.permission = data.get("permission", member.permission)
    db.session.commit()

    return jsonify({"message": "Permission updated"})

# ─────────────────────────────────────────────────────────────────
# ADDED: remove a member from the circle
# ─────────────────────────────────────────────────────────────────
@circle_bp.route("/circle/remove_member", methods=["POST"])
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