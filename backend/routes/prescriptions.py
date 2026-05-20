from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Prescription, Prescription_Detail, Alarm, Med_Supply

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
            "name":         rx.name,
            "date":         rx.date.isoformat() if rx.date else None,
            "doctor":       rx.doctor,
            "detail":       rx.detail,
            "alarm_active": rx.alarm.is_active if rx.alarm else False,
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

    Alarm.query.filter_by(prescription_id=prescription_id).delete()
    Prescription_Detail.query.filter_by(prescription_id=prescription_id).delete()
    db.session.delete(rx)
    db.session.commit()
    return jsonify({"message": "Prescription deleted"})


# ── TOGGLE ALARM ──────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/alarm", methods=["PATCH"])
@login_required
def toggle_alarm(prescription_id):
    """Toggle alarm is_active for a prescription."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    alarm = Alarm.query.filter_by(prescription_id=prescription_id).first()
    if not alarm:
        alarm = Alarm(is_active=False, prescription_id=prescription_id)
        db.session.add(alarm)
        db.session.flush()

    alarm.is_active = not alarm.is_active
    db.session.commit()
    return jsonify({"alarm_active": alarm.is_active})


# ── LIST DETAILS ──────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details", methods=["GET"])
@login_required
def list_details(prescription_id):
    """Return all prescription_details for a prescription, including stock."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    details = Prescription_Detail.query.filter_by(prescription_id=prescription_id).all()
    alarm   = Alarm.query.filter_by(prescription_id=prescription_id).first()

    result = []
    for d in details:
        supply = db.session.get(Med_Supply, d.supply_id) if d.supply_id else None
        med    = supply.medicine if supply else None
        result.append({
            "prescription_detail_id": d.prescription_detail_id,
            "supply_id":    d.supply_id,
            "brand_name":   med.brand_name    if med    else None,
            "generic_name": med.generic_name  if med    else None,
            "dosage_form":  med.dosage_form   if med    else None,
            "supply_stock": supply.supply_stock if supply else None,
            "date_start":   d.date_start.isoformat() if d.date_start else None,
            "date_end":     d.date_end.isoformat()   if d.date_end   else None,
            "time_taken":   d.time_taken,
            "days_taken":   d.days_taken,
            "alarm_active": alarm.is_active if alarm else False,
        })
    return jsonify(result)


# ── ADD DETAIL (from shelf, requires supply_id) ───────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details", methods=["POST"])
@login_required
def add_detail(prescription_id):
    """Add a supply from the user's shelf to a prescription and ensure an alarm exists."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    data       = request.get_json()
    supply_id  = data.get("supply_id")
    date_start = (data.get("date_start") or "").strip()
    time_taken = (data.get("time_taken") or "").strip()
    days_taken = (data.get("days_taken") or "").strip()

    if not supply_id:
        return jsonify({"error": "supply_id is required."}), 400

    supply = db.session.get(Med_Supply, supply_id)
    if not supply or supply.user_id != current_user.user_id:
        return jsonify({"error": "Invalid supply."}), 400
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
        supply_id=supply_id,
    )
    db.session.add(detail)
    db.session.flush()

    # Ensure the prescription has an alarm (create one if missing)
    alarm = Alarm.query.filter_by(prescription_id=prescription_id).first()
    if not alarm:
        alarm = Alarm(is_active=True, prescription_id=prescription_id)
        db.session.add(alarm)

    db.session.commit()
    return jsonify({
        "message": "Medicine added",
        "prescription_detail_id": detail.prescription_detail_id,
    }), 201


# ── REMOVE DETAIL ─────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details/<int:detail_id>", methods=["DELETE"])
@login_required
def remove_detail(prescription_id, detail_id):
    """Remove a medicine from a prescription."""
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    detail = db.session.get(Prescription_Detail, detail_id)
    if not detail or detail.prescription_id != prescription_id:
        return jsonify({"error": "Detail not found"}), 404

    db.session.delete(detail)
    db.session.commit()
    return jsonify({"message": "Medicine removed"})
