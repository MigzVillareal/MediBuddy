from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Prescription, Prescription_Detail, Med_Lookup
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import os

prescriptions_bp = Blueprint("prescriptions", __name__)

def check_reminders():
    # to be added
    pass

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

ONESIGNAL_APP_ID  = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

# ── HELPERS ───────────────────────────────────────────────────────────────────

def parse_days(days_taken):
    mapping = {
        'daily':  'mon,tue,wed,thu,fri,sat,sun',
        'MWF':    'mon,wed,fri',
        'TTS':    'tue,thu,sat',
        'MTWTHF': 'mon,tue,wed,thu,fri',
        'SS':     'sat,sun',
    }
    return mapping.get(days_taken, 'mon,tue,wed,thu,fri,sat,sun')

def send_notification(onesignal_id, medication):
    requests.post(
        'https://onesignal.com/api/v1/notifications',
        headers={'Authorization': f'Basic {ONESIGNAL_API_KEY}'},
        json={
            'app_id': ONESIGNAL_APP_ID,
            'include_subscription_ids': [onesignal_id],
            'contents': {'en': f'Time to take your {medication}!'},
            'headings': {'en': 'MediBuddy Reminder'},
        }
    )

# ── LIST ──────────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/", methods=["GET"])
@login_required
def list_prescriptions():
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
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    details = Prescription_Detail.query.filter_by(prescription_id=prescription_id).all()
    for d in details:
        # cancel any scheduled jobs
        if d.job_reference:
            for job_id in d.job_reference.split(','):
                try: scheduler.remove_job(job_id.strip())
                except: pass

    Prescription_Detail.query.filter_by(prescription_id=prescription_id).delete()
    db.session.delete(rx)
    db.session.commit()
    return jsonify({"message": "Prescription deleted"})


# ── LIST DETAILS ──────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details", methods=["GET"])
@login_required
def list_details(prescription_id):
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    details = Prescription_Detail.query.filter_by(prescription_id=prescription_id).all()
    result = []
    for d in details:
        med = db.session.get(Med_Lookup, d.lookup_id)
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
            "alarm_active": d.is_active,
            "onesignal_id": d.onesignal_id,
        })
    return jsonify(result)


# ── ADD DETAIL ────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details", methods=["POST"])
@login_required
def add_detail(prescription_id):
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()

    lookup_id = data.get("lookup_id")
    # if not lookup_id or not db.session.get(Med_Lookup, lookup_id):
    #     return jsonify({"error": "Invalid medicine selected."}), 400

    date_start = data.get("date_start")
    time_taken = (data.get("time_taken") or "").strip()
    days_taken = (data.get("days_taken") or "").strip()
    onesignal_id = data.get("onesignal_id")

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
        # lookup_id=lookup_id,
        onesignal_id=onesignal_id,
        is_active=bool(onesignal_id),
    )
    db.session.add(detail)
    db.session.flush()

    # Schedule a job for each time if onesignal_id is present
    if onesignal_id:
        med = db.session.get(Med_Lookup, lookup_id)
        med_name = med.brand_name if med else 'your medicine'
        job_ids = []
        for time_str in time_taken.split(','):
            hour, minute = map(int, time_str.strip().split(':'))
            job_id = f"reminder_{detail.prescription_detail_id}_{time_str.strip()}"
            scheduler.add_job(
                send_notification,
                'cron',
                day_of_week=parse_days(days_taken),
                hour=hour,
                minute=minute,
                args=[onesignal_id, med_name],
                id=job_id,
                replace_existing=True,
            )
            job_ids.append(job_id)
        detail.job_reference = ','.join(job_ids)

    db.session.commit()
    return jsonify({
        "message": "Medicine added and alarm scheduled" if onesignal_id else "Medicine added",
        "prescription_detail_id": detail.prescription_detail_id,
    }), 201


# ── REMOVE DETAIL ─────────────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details/<int:detail_id>", methods=["DELETE"])
@login_required
def remove_detail(prescription_id, detail_id):
    rx = db.session.get(Prescription, prescription_id)
    if not rx:
        return jsonify({"error": "Prescription not found"}), 404
    if rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    detail = db.session.get(Prescription_Detail, detail_id)
    if not detail or detail.prescription_id != prescription_id:
        return jsonify({"error": "Detail not found"}), 404

    # Cancel scheduled jobs
    if detail.job_reference:
        for job_id in detail.job_reference.split(','):
            try: scheduler.remove_job(job_id.strip())
            except: pass

    db.session.delete(detail)
    db.session.commit()
    return jsonify({"message": "Medicine and alarm removed"})