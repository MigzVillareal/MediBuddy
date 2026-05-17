from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Circle, CircleMember, User

circle_bp = Blueprint("circle", __name__)


# ─────────────────────────────────────────────────────────────────────────────
# CIRCLES — owned by the current user
# ─────────────────────────────────────────────────────────────────────────────

@circle_bp.route("/mine", methods=["GET"])
@login_required
def get_my_circles():
    """All circles the current user owns."""
    circles = Circle.query.filter_by(owner_id=current_user.user_id).all()
    result = []
    for c in circles:
        accepted = CircleMember.query.filter_by(circle_id=c.circle_id, status="accepted").all()
        pending_sent = CircleMember.query.filter_by(circle_id=c.circle_id, status="pending").all()
        result.append({
            "circle_id": c.circle_id,
            "circle_name": c.circle_name,
            "member_count": len(accepted),
            "pending_count": len(pending_sent),
        })
    return jsonify(result)


@circle_bp.route("/create", methods=["POST"])
@login_required
def create_circle():
    """Create a new named circle owned by the logged-in user."""
    data = request.get_json()
    name = (data.get("circle_name") or "").strip()
    if not name:
        return jsonify({"error": "Circle name is required."}), 400
    circle = Circle(circle_name=name, owner_id=current_user.user_id)
    db.session.add(circle)
    db.session.commit()
    return jsonify({"message": "Circle created", "circle_id": circle.circle_id, "circle_name": circle.circle_name}), 201


@circle_bp.route("/<int:circle_id>/rename", methods=["PUT"])
@login_required
def rename_circle(circle_id):
    """Rename a circle — owner only."""
    circle = db.session.get(Circle, circle_id)
    if not circle:
        return jsonify({"error": "Circle not found"}), 404
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403
    data = request.get_json()
    name = (data.get("circle_name") or "").strip()
    if not name:
        return jsonify({"error": "Circle name is required."}), 400
    circle.circle_name = name
    db.session.commit()
    return jsonify({"message": "Renamed", "circle_name": circle.circle_name})


@circle_bp.route("/<int:circle_id>", methods=["DELETE"])
@login_required
def delete_circle(circle_id):
    """Delete a circle and all its member records — owner only."""
    circle = db.session.get(Circle, circle_id)
    if not circle:
        return jsonify({"error": "Circle not found"}), 404
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403
    # Remove all member/invite rows first
    CircleMember.query.filter_by(circle_id=circle_id).delete()
    db.session.delete(circle)
    db.session.commit()
    return jsonify({"message": "Circle deleted"})


# ─────────────────────────────────────────────────────────────────────────────
# MEMBERS (accepted only)
# ─────────────────────────────────────────────────────────────────────────────

@circle_bp.route("/<int:circle_id>/members", methods=["GET"])
@login_required
def get_members(circle_id):
    """Accepted members of a circle. Visible to owner or any accepted member."""
    circle = db.session.get(Circle, circle_id)
    if not circle:
        return jsonify({"error": "Circle not found"}), 404

    is_owner = circle.owner_id == current_user.user_id
    is_member = CircleMember.query.filter_by(
        circle_id=circle_id, user_id=current_user.user_id, status="accepted"
    ).first()
    if not is_owner and not is_member:
        return jsonify({"error": "Not authorized"}), 403

    rows = CircleMember.query.filter_by(circle_id=circle_id, status="accepted").all()
    result = []
    for m in rows:
        user = db.session.get(User, m.user_id)
        result.append({
            "user_id": m.user_id,
            "username": user.username if user else f"User {m.user_id}",
            "permission": m.permission,
        })
    return jsonify(result)


@circle_bp.route("/update_permission", methods=["POST"])
@login_required
def update_permission():
    """Owner updates an accepted member's permission level."""
    data = request.get_json()
    circle = db.session.get(Circle, data.get("circle_id"))
    if not circle:
        return jsonify({"error": "Circle not found"}), 404
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    member = CircleMember.query.filter_by(
        circle_id=data["circle_id"], user_id=data["user_id"], status="accepted"
    ).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404

    member.permission = data.get("permission", member.permission)
    db.session.commit()
    return jsonify({"message": "Permission updated"})


@circle_bp.route("/remove_member", methods=["POST"])
@login_required
def remove_member():
    """Owner removes an accepted member."""
    data = request.get_json()
    circle = db.session.get(Circle, data.get("circle_id"))
    if not circle:
        return jsonify({"error": "Circle not found"}), 404
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    member = CircleMember.query.filter_by(
        circle_id=data["circle_id"], user_id=data["user_id"], status="accepted"
    ).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed"})


# ─────────────────────────────────────────────────────────────────────────────
# INVITES — using CircleMember with status='pending'
# ─────────────────────────────────────────────────────────────────────────────

@circle_bp.route("/invite", methods=["POST"])
@login_required
def send_invite():
    """Owner sends an invite to a user by username."""
    data = request.get_json()
    circle = db.session.get(Circle, data.get("circle_id"))
    if not circle:
        return jsonify({"error": "Circle not found"}), 404
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    invitee = User.query.filter_by(username=(data.get("username") or "").strip()).first()
    if not invitee:
        return jsonify({"error": "User not found"}), 404
    if invitee.user_id == current_user.user_id:
        return jsonify({"error": "You cannot invite yourself"}), 400

    # Already an accepted member?
    already = CircleMember.query.filter_by(
        circle_id=circle.circle_id, user_id=invitee.user_id, status="accepted"
    ).first()
    if already:
        return jsonify({"error": "User is already a member"}), 409

    # Already has a pending invite?
    pending = CircleMember.query.filter_by(
        circle_id=circle.circle_id, user_id=invitee.user_id, status="pending"
    ).first()
    if pending:
        return jsonify({"error": "Invite already sent to this user"}), 409

    invite_row = CircleMember(
        circle_id=circle.circle_id,
        user_id=invitee.user_id,
        inviter_id=current_user.user_id,
        permission=data.get("permission", "canview"),
        status="pending",
    )
    db.session.add(invite_row)
    db.session.commit()
    return jsonify({"message": "Invite sent"}), 201


@circle_bp.route("/invites/pending", methods=["GET"])
@login_required
def get_pending_invites():
    """Return all pending invites received by the current user."""
    rows = CircleMember.query.filter_by(
        user_id=current_user.user_id, status="pending"
    ).all()
    result = []
    for m in rows:
        circle = db.session.get(Circle, m.circle_id)
        inviter = db.session.get(User, m.inviter_id) if m.inviter_id else None
        result.append({
            "circle_member_id": m.circle_member_id,
            "circle_id": m.circle_id,
            "circle_name": circle.circle_name if circle else f"Circle {m.circle_id}",
            "inviter_username": inviter.username if inviter else "Unknown",
            "permission": m.permission,
        })
    return jsonify(result)


@circle_bp.route("/invites/sent", methods=["GET"])
@login_required
def get_sent_invites():
    """Return all pending invites the current user has sent (as owner)."""
    # Find all circles owned by the current user
    owned_ids = [c.circle_id for c in Circle.query.filter_by(owner_id=current_user.user_id).all()]
    if not owned_ids:
        return jsonify([])

    rows = CircleMember.query.filter(
        CircleMember.circle_id.in_(owned_ids),
        CircleMember.inviter_id == current_user.user_id,
    ).all()

    result = []
    for m in rows:
        circle = db.session.get(Circle, m.circle_id)
        invitee = db.session.get(User, m.user_id)
        result.append({
            "circle_member_id": m.circle_member_id,
            "circle_id": m.circle_id,
            "circle_name": circle.circle_name if circle else f"Circle {m.circle_id}",
            "invitee_username": invitee.username if invitee else f"User {m.user_id}",
            "permission": m.permission,
            "status": m.status,
        })
    return jsonify(result)


@circle_bp.route("/invite/<int:circle_member_id>/respond", methods=["POST"])
@login_required
def respond_invite(circle_member_id):
    """Invitee accepts or rejects an invite. Body: { action: 'accept'|'reject' }"""
    row = db.session.get(CircleMember, circle_member_id)
    if not row:
        return jsonify({"error": "Invite not found"}), 404
    if row.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403
    if row.status != "pending":
        return jsonify({"error": "Already responded to this invite"}), 409

    action = (request.get_json() or {}).get("action")
    if action not in ("accept", "reject"):
        return jsonify({"error": "action must be 'accept' or 'reject'"}), 400

    if action == "accept":
        row.status = "accepted"
    else:
        row.status = "rejected"

    db.session.commit()
    return jsonify({"message": f"Invite {row.status}"})