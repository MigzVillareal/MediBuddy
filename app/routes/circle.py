from flask import Blueprint, request, jsonify
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

@circle_bp.route("/circle/add_member", methods=["POST"])
def add_member():
    data = request.get_json()

    user = User.query.filter_by(username=data["username"]).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

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