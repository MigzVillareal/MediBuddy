from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import requests
import os
from models import Prescription, Prescription_Detail, Med_Supply

prescriptions_bp = Blueprint("prescriptions", __name__)

ONESIGNAL_APP_ID  = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")
DATABASE_URL      = os.getenv("DATABASE_URL", "sqlite:///app.db")

# ── SCHEDULER (persistent job store so jobs survive restarts) ─────────────────
jobstores = {
    'default': SQLAlchemyJobStore(url=DATABASE_URL)
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

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

# ── SENDER ───────────────────────────────────────────────────────────────────

def send_notification(onesignal_id, medication, detail_id):
    from models import Prescription_Detail, Prescription
    from extensions import db
    from run import app

    with app.app_context():
        detail = db.session.get(Prescription_Detail, detail_id)
        if not detail or not detail.alarm_active:
            print(f"Detail alarm inactive, skipping notification")
            return

        rx = db.session.get(Prescription, detail.prescription_id)
        if not rx or not rx.alarm_active:
            print(f"Prescription alarm inactive, skipping notification")
            return

        app_id  = os.getenv("ONESIGNAL_APP_ID")
        api_key = os.getenv("ONESIGNAL_API_KEY")
        try:
            response = requests.post(
                'https://onesignal.com/api/v1/notifications',
                headers={
                    'Authorization': f'Key {api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'app_id': app_id,
                    'target_channel': 'push',
                    'include_subscription_ids': [onesignal_id],
                    'contents': {'en': f'Time to take your {medication}!'},
                    'headings': {'en': 'MediBuddy Reminder'},
                }
            )
            print(f"OneSignal response: {response.status_code} {response.text}")
        except Exception as e:
            print(f"OneSignal notification failed: {e}")

# ── ONESIGNAL DEBUG ───────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/debug/key", methods=["GET"])
def debug_key():
    return jsonify({
        "app_id": ONESIGNAL_APP_ID,
        "api_key_prefix": ONESIGNAL_API_KEY[:6] if ONESIGNAL_API_KEY else None,
        "api_key_length": len(ONESIGNAL_API_KEY) if ONESIGNAL_API_KEY else 0,
    })

@prescriptions_bp.route("/debug/onesignal-ids", methods=["GET"])
@login_required
def debug_onesignal_ids():
    details = Prescription_Detail.query.join(Prescription).filter(
        Prescription.user_id == current_user.user_id
    ).all()
    return jsonify([{
        "detail_id": d.prescription_detail_id,
        "onesignal_id": d.onesignal_id,
        "job_reference": d.job_reference,
    } for d in details])

def schedule_detail_jobs(detail, onesignal_id):
    """Schedule cron jobs for every time in detail.time_taken. Returns job_reference string."""
    supply   = db.session.get(Med_Supply, detail.supply_id) if detail.supply_id else None
    med_name = supply.medicine.brand_name if supply and supply.medicine else 'your medicine'
    job_ids  = []
    for time_str in detail.time_taken.split(','):
        hour, minute = map(int, time_str.strip().split(':'))
        job_id = f"reminder_{detail.prescription_detail_id}_{time_str.strip()}"
        scheduler.add_job(
            send_notification, 'cron',
            day_of_week=parse_days(detail.days_taken),
            hour=hour, minute=minute,
            args=[onesignal_id, med_name, detail.prescription_detail_id],
            id=job_id, replace_existing=True,
)
        job_ids.append(job_id)
    detail.alarm_active = True 
    return ','.join(job_ids)

def cancel_detail_jobs(detail):
    if detail.job_reference:
        for job_id in detail.job_reference.split(','):
            try:
                scheduler.remove_job(job_id.strip())
            except Exception:
                pass
    detail.job_reference = None
    detail.onesignal_id  = None
    detail.alarm_active  = False

# ── LIST ──────────────────────────────────────────────────────────────────────

@prescriptions_bp.route("/", methods=["GET"])
@login_required
def list_prescriptions():
    rxs = Prescription.query.filter_by(user_id=current_user.user_id).order_by(
        Prescription.prescription_id.desc()
    ).all()
    result = []
    for rx in rxs:
        has_alarm = db.session.query(Prescription_Detail).filter_by(
            prescription_id=rx.prescription_id
        ).filter(Prescription_Detail.job_reference.isnot(None)).first() is not None

        result.append({
            "prescription_id": rx.prescription_id,
            "name":         rx.name,
            "date":         rx.date.isoformat() if rx.date else None,
            "doctor":       rx.doctor,
            "detail":       rx.detail,
            "alarm_active": has_alarm,
        })
    return jsonify(result)
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

    for d in rx.prescription_details:
        cancel_detail_jobs(d)

    db.session.delete(rx)
    db.session.commit()
    return jsonify({"message": "Prescription deleted"})

# ── TOGGLE PRESCRIPTION ALARM (header bell — mirrors detail alarms) ────────────

@prescriptions_bp.route("/<int:prescription_id>/alarm", methods=["PATCH"])
@login_required
def toggle_prescription_alarm(prescription_id):
    rx = db.session.get(Prescription, prescription_id)
    if not rx or rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    rx.alarm_active = not rx.alarm_active
    db.session.commit()
    return jsonify({"alarm_active": rx.alarm_active})

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
    result  = []
    for d in details:
        supply = db.session.get(Med_Supply, d.supply_id) if d.supply_id else None
        med    = supply.medicine if supply else None
        result.append({
            "prescription_detail_id": d.prescription_detail_id,
            "supply_id":    d.supply_id,
            "brand_name":   med.brand_name   if med else None,
            "generic_name": med.generic_name if med else None,
            "dosage_form":  med.dosage_form  if med else None,
            "quantity":     supply.supply_stock if supply else None,
            "date_start":   d.date_start.isoformat() if d.date_start else None,
            "date_end":     d.date_end.isoformat()   if d.date_end   else None,
            "time_taken":   d.time_taken,
            "days_taken":   d.days_taken,
            "alarm_active": bool(d.job_reference),
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

    data         = request.get_json()
    supply_id    = data.get("supply_id")
    date_start   = data.get("date_start")
    time_taken   = (data.get("time_taken") or "").strip()
    days_taken   = (data.get("days_taken") or "").strip()
    onesignal_id = data.get("onesignal_id")

    print(f">>> onesignal_id received: {onesignal_id}")

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
        onesignal_id=onesignal_id,
    )
    db.session.add(detail)
    db.session.flush()  # get prescription_detail_id before scheduling

    if onesignal_id:
        detail.job_reference = schedule_detail_jobs(detail, onesignal_id)

    db.session.commit()
    return jsonify({
        "message": "Medicine added and alarm scheduled" if onesignal_id else "Medicine added",
        "prescription_detail_id": detail.prescription_detail_id,
    }), 201

# ── TOGGLE DETAIL ALARM ───────────────────────────────────────────────────────

@prescriptions_bp.route("/<int:prescription_id>/details/<int:detail_id>/alarm", methods=["PATCH"])
@login_required
def toggle_detail_alarm(prescription_id, detail_id):
    rx = db.session.get(Prescription, prescription_id)
    if not rx or rx.user_id != current_user.user_id:
        return jsonify({"error": "Not authorized"}), 403

    detail = db.session.get(Prescription_Detail, detail_id)
    if not detail or detail.prescription_id != prescription_id:
        return jsonify({"error": "Detail not found"}), 404

    if detail.job_reference:
        cancel_detail_jobs(detail)
        db.session.commit()
        return jsonify({"alarm_active": False})
    else:
        data         = request.get_json() or {}
        onesignal_id = data.get("onesignal_id")
        if not onesignal_id:
            return jsonify({"error": "onesignal_id required"}), 400

        detail.onesignal_id  = onesignal_id
        detail.job_reference = schedule_detail_jobs(detail, onesignal_id)
        db.session.commit()
        return jsonify({"alarm_active": True})

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

    cancel_detail_jobs(detail)
    db.session.delete(detail)
    db.session.commit()
    return jsonify({"message": "Medicine and alarm removed"})