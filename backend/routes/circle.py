from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Circle, CircleMember, CircleInvite, User

circle_bp = Blueprint("circle", __name__)

# ─────────────────────────────────────────────────────────────────────────────
# CIRCLES — owned by the current user
# ─────────────────────────────────────────────────────────────────────────────

@circle_bp.route("/mine", methods=["GET"])
@login_required
def get_my_circles():
    """Return all circles owned by the logged-in user."""
    circles = Circle.query.filter_by(owner_id=current_user.user_id).all()
    result = []
    for c in circles:
        accepted_members = CircleMember.query.filter_by(circle_id=c.circle_id).all()
        result.append({
            "circle_id": c.circle_id,
            "circle_name": c.circle_name,
            "member_count": len(accepted_members),
        })
    return jsonify(result)


@circle_bp.route("/create", methods=["POST"])
@login_required
def create_circle():
    """Create a new circle owned by the current user."""
    data = request.get_json()
    name = (data.get("circle_name") or "").strip()
    if not name:
        return jsonify({"error": "Circle name is required."}), 400

    circle = Circle(circle_name=name, owner_id=current_user.user_id)
    db.session.add(circle)
    db.session.commit()
    return jsonify({"message": "Circle created", "circle_id": circle.circle_id, "circle_name": circle.circle_name})


@circle_bp.route("/<int:circle_id>/rename", methods=["PUT"])
@login_required
def rename_circle(circle_id):
    """Rename a circle (owner only)."""
    circle = Circle.query.get_or_404(circle_id)
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403
    data = request.get_json()
    name = (data.get("circle_name") or "").strip()
    if not name:
        return jsonify({"error": "Circle name is required."}), 400
    circle.circle_name = name
    db.session.commit()
    return jsonify({"message": "Circle renamed", "circle_name": circle.circle_name})


@circle_bp.route("/<int:circle_id>", methods=["DELETE"])
@login_required
def delete_circle(circle_id):
    """Delete a circle (owner only). Cascades to members and invites."""
    circle = Circle.query.get_or_404(circle_id)
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403
    db.session.delete(circle)
    db.session.commit()
    return jsonify({"message": "Circle deleted"})


# ─────────────────────────────────────────────────────────────────────────────
# MEMBERS
# ─────────────────────────────────────────────────────────────────────────────

@circle_bp.route("/<int:circle_id>/members", methods=["GET"])
@login_required
def get_members(circle_id):
    """Return accepted members of a circle."""
    circle = Circle.query.get_or_404(circle_id)
    # Only the owner or an accepted member may view the list
    is_owner = circle.owner_id == current_user.user_id
    is_member = CircleMember.query.filter_by(
        circle_id=circle_id, user_id=current_user.user_id
    ).first()
    if not is_owner and not is_member:
        return jsonify({"error": "Not authorized"}), 403

    members = CircleMember.query.filter_by(circle_id=circle_id).all()
    result = []
    for m in members:
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
    """Owner updates an existing member's permission."""
    data = request.get_json()
    circle = Circle.query.get_or_404(data["circle_id"])
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    member = CircleMember.query.filter_by(
        circle_id=data["circle_id"], user_id=data["user_id"]
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
    circle = Circle.query.get_or_404(data["circle_id"])
    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    member = CircleMember.query.filter_by(
        circle_id=data["circle_id"], user_id=data["user_id"]
    ).first()
    if not member:
        return jsonify({"error": "Member not found"}), 404
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed"})


# ─────────────────────────────────────────────────────────────────────────────
# INVITES
# ─────────────────────────────────────────────────────────────────────────────

@circle_bp.route("/invite", methods=["POST"])
@login_required
def send_invite():
    """Send an invite to a user to join a circle (owner only)."""
    data = request.get_json()
    circle = Circle.query.get_or_404(data["circle_id"])

    if circle.owner_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    invitee = User.query.filter_by(username=data.get("username", "").strip()).first()
    if not invitee:
        return jsonify({"error": "User not found"}), 404
    if invitee.user_id == current_user.user_id:
        return jsonify({"error": "You cannot invite yourself"}), 400

    # Check already a member
    already_member = CircleMember.query.filter_by(
        circle_id=circle.circle_id, user_id=invitee.user_id
    ).first()
    if already_member:
        return jsonify({"error": "User is already a member"}), 409

    # Check pending invite already exists
    pending = CircleInvite.query.filter_by(
        circle_id=circle.circle_id,
        invitee_id=invitee.user_id,
        status="pending"
    ).first()
    if pending:
        return jsonify({"error": "Invite already sent to this user"}), 409

    invite = CircleInvite(
        circle_id=circle.circle_id,
        inviter_id=current_user.user_id,
        invitee_id=invitee.user_id,
        permission=data.get("permission", "canview"),
        status="pending",
    )
    db.session.add(invite)
    db.session.commit()
    return jsonify({"message": "Invite sent", "invite_id": invite.invite_id})


@circle_bp.route("/invites/pending", methods=["GET"])
@login_required
def get_pending_invites():
    """Return all pending invites received by the current user."""
    invites = CircleInvite.query.filter_by(
        invitee_id=current_user.user_id, status="pending"
    ).all()
    result = []
    for inv in invites:
        circle = db.session.get(Circle, inv.circle_id)
        inviter = db.session.get(User, inv.inviter_id)
        result.append({
            "invite_id": inv.invite_id,
            "circle_id": inv.circle_id,
            "circle_name": circle.circle_name if circle else f"Circle {inv.circle_id}",
            "inviter_username": inviter.username if inviter else f"User {inv.inviter_id}",
            "permission": inv.permission,
        })
    return jsonify(result)


@circle_bp.route("/invites/sent", methods=["GET"])
@login_required
def get_sent_invites():
    """Return all invites the current user has sent."""
    invites = CircleInvite.query.filter_by(inviter_id=current_user.user_id).all()
    result = []
    for inv in invites:
        circle = db.session.get(Circle, inv.circle_id)
        invitee = db.session.get(User, inv.invitee_id)
        result.append({
            "invite_id": inv.invite_id,
            "circle_id": inv.circle_id,
            "circle_name": circle.circle_name if circle else f"Circle {inv.circle_id}",
            "invitee_username": invitee.username if invitee else f"User {inv.invitee_id}",
            "permission": inv.permission,
            "status": inv.status,
        })
    return jsonify(result)


@circle_bp.route("/invite/<int:invite_id>/respond", methods=["POST"])
@login_required
def respond_invite(invite_id):
    """Accept or reject an invite. Body: { action: 'accept' | 'reject' }"""
    invite = CircleInvite.query.get_or_404(invite_id)
    if invite.invitee_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403
    if invite.status != "pending":
        return jsonify({"error": "Invite already responded to"}), 409

    data = request.get_json()
    action = data.get("action")
    if action not in ("accept", "reject"):
        return jsonify({"error": "action must be 'accept' or 'reject'"}), 400

    if action == "accept":
        invite.status = "accepted"
        member = CircleMember(
            circle_id=invite.circle_id,
            user_id=current_user.user_id,
            permission=invite.permission,
        )
        db.session.add(member)
    else:
        invite.status = "rejected"

    db.session.commit()
    return jsonify({"message": f"Invite {invite.status}"})