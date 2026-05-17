from datetime import datetime, date, timezone
from flask import Blueprint
from extensions import db
from models import Prescription_Detail, Med_Lookup, User
import requests
import os

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api")

def should_take_today(days_taken: str) -> bool:
    day = datetime.now(timezone.utc).weekday()  # 0=Monday, 6=Sunday

    if days_taken == "daily":
        return True
    elif days_taken == "MWF":
        return day in [0, 2, 4]
    elif days_taken == "TTH":
        return day in [1, 3]
    elif days_taken == "weekly":
        return day == 0
    elif days_taken == "every_other_day":
        return True
    return False

def send_onesignal_notification(user, medicine, time_str):
    requests.post(
        "https://onesignal.com/api/v1/notifications",
        headers={
            "Authorization": f"Basic {os.environ.get('ONESIGNAL_REST_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "app_id": os.environ.get("ONESIGNAL_APP_ID"),
            "filters": [{"field": "tag", "key": "user_id", "relation": "=", "value": str(user.user_id)}],
            "contents": {"en": f"Time to take: {medicine.brand_name} ({medicine.generic_name}) {medicine.dosage_form}"},
            "headings": {"en": "MediBuddy Reminder"},
        }
    )

def check_med_schedules():
    now = datetime.now(timezone.utc)
    today = date.today()
    current_time = now.strftime("%H:%M")

    due = Prescription_Detail.query.filter(
        Prescription_Detail.date_start <= today,
        db.or_(
            Prescription_Detail.date_end == None,
            Prescription_Detail.date_end >= today
        )
    ).all()

    for detail in due:
        if not should_take_today(detail.days_taken):
            continue

        # time_taken is comma-separated e.g. "08:00,14:00,20:00"
        times = [t.strip() for t in detail.time_taken.split(",")]
        if current_time not in times:
            continue

        send_onesignal_notification(detail.user, detail.medicine, current_time)

@notifications_bp.route("/check-reminders", methods=["GET", "POST"])
def check_reminders():
    check_med_schedules()
    return {"message": "checked"}, 200