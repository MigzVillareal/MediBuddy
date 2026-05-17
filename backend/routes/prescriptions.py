from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Prescription, Prescription_Detail, Alarm, Med_Lookup

prescriptions_bp = Blueprint("prescriptions", __name__)


# ── LIST ──────────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/", methods=["GET"])
@login_required
def list_prescriptions():
    """Return all prescriptions belonging to the current user."""
    rxs = Prescription.query.filter_by(user_id=current_user.user_id).order_by(
        Prescription.prescription_id.desc()
    ).all()
    return jsonify([
        {
            "prescription_id": rx.prescription_id,
            "name":   rx.name,
            "date":   rx.date.isoformat() if rx.date else None,
            "doctor": rx.doctor,
            "detail": rx.detail,
        }
        for rx in rxs
    ])


# ── CREATE ────────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/", methods=["POST"])
@login_required
def create_prescription():
    """Create a new prescription for the current user."""
    data = request.get_json()
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Prescription name is required."}), 400

    rx = Prescription(
        name=name,
        date=data.get("date") or None,
        doctor=(data.get("doctor") or "").strip() or None,
        detail=(data.get("detail") or "").strip() or None,
        user_id=current_user.user_id,
    )
    db.session.add(rx)
    db.session.commit()
    return jsonify({"message": "Prescription created", "prescription_id": rx.prescription_id}), 201


# ── DELETE ────────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>", methods=["DELETE"])
@login_required
def delete_prescription(prescription_id):
    """Delete a prescription and all its details + alarms."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    # Cascade: delete alarms first, then details, then the prescription
    details = Prescription_Detail.query.filter_by(prescription_id=prescription_id).all()
    for d in details:
        Alarm.query.filter_by(prescription_detail_id=d.prescription_detail_id).delete()
    Prescription_Detail.query.filter_by(prescription_id=prescription_id).delete()
    db.session.delete(rx)
    db.session.commit()
    return jsonify({"message": "Prescription deleted"})


# ── LIST DETAILS ──────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details", methods=["GET"])
@login_required
def list_details(prescription_id):
    """Return all prescription_details (medicines) for a prescription."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    details = Prescription_Detail.query.filter_by(prescription_id=prescription_id).all()
    result = []
    for d in details:
        med = db.session.get(Med_Lookup, d.lookup_id)
        alarm = Alarm.query.filter_by(prescription_detail_id=d.prescription_detail_id).first()
        result.append({
            "prescription_detail_id": d.prescription_detail_id,
            "lookup_id":    d.lookup_id,
            "brand_name":   med.brand_name   if med else None,
            "generic_name": med.generic_name if med else None,
            "dosage_form":  med.dosage_form  if med else None,
            "date_start":   d.date_start.isoformat() if d.date_start else None,
            "date_end":     d.date_end.isoformat()   if d.date_end   else None,
            "time_taken":   d.time_taken,
            "days_taken":   d.days_taken,
            "alarm_id":     alarm.alarm_id  if alarm else None,
            "alarm_active": alarm.is_active if alarm else False,
        })
    return jsonify(result)


# ── ADD DETAIL ────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details", methods=["POST"])
@login_required
def add_detail(prescription_id):
    """Add a medicine to a prescription and auto-create its alarm."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()

    lookup_id = data.get("lookup_id")
    if not lookup_id or not db.session.get(Med_Lookup, lookup_id):
        return jsonify({"error": "Invalid medicine selected."}), 400

    date_start = data.get("date_start")
    time_taken = (data.get("time_taken") or "").strip()
    days_taken = (data.get("days_taken") or "").strip()

    if not date_start:
        return jsonify({"error": "date_start is required."}), 400
    if not time_taken:
        return jsonify({"error": "time_taken is required."}), 400
    if not days_taken:
        return jsonify({"error": "days_taken is required."}), 400

    detail = Prescription_Detail(
        date_start=date_start,
        date_end=data.get("date_end") or None,
        time_taken=time_taken,
        days_taken=days_taken,
        prescription_id=prescription_id,
        lookup_id=lookup_id,
        user_id=current_user.user_id,
    )
    db.session.add(detail)
    db.session.flush()   # get prescription_detail_id before commit

    # Auto-create an alarm for this detail
    alarm = Alarm(
        is_active=True,
        prescription_detail_id=detail.prescription_detail_id,
    )
    db.session.add(alarm)
    db.session.commit()

    return jsonify({
        "message": "Medicine added and alarm created",
        "prescription_detail_id": detail.prescription_detail_id,
        "alarm_id": alarm.alarm_id,
    }), 201


# ── REMOVE DETAIL ─────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details/<int:detail_id>", methods=["DELETE"])
@login_required
def remove_detail(prescription_id, detail_id):
    """Remove a medicine from a prescription and delete its alarm."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    detail = db.session.get(Prescription_Detail, detail_id)
    if not detail or detail.prescription_id != prescription_id:
        return jsonify({"error": "Detail not found"}), 404

    Alarm.query.filter_by(prescription_detail_id=detail_id).delete()
    db.session.delete(detail)
    db.session.commit()
    return jsonify({"message": "Medicine and alarm removed"})
