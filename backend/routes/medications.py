from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import Med_Supply

meds_bp = Blueprint('meds', __name__)

def safe_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200
        return login_required(fn)(*args, **kwargs)
    return wrapper

@meds_bp.route('/drug_stock', methods=['POST'])
@login_required
def add_drug():
    data = request.get_json(force=True)
    lookup_id = data.get("lookup_id")

    existing = Med_Supply.query.filter_by(
        user_id=current_user.user_id,
        lookup_id=lookup_id
    ).first()
    if existing:
        return jsonify({"error": "This medicine is already on your shelf."}), 409

    supply = Med_Supply(
        user_id=current_user.user_id,
        lookup_id=lookup_id,
        supply_stock=int(data.get("supply_stock", 0)),
        expiration_date=data.get("expiration_date"),
    )

    db.session.add(supply)
    db.session.commit()

    return jsonify({'message': 'Drug Added', 'supply_id': supply.supply_id}), 201

@meds_bp.route('/drug_stock/<int:supply_id>', methods=['PATCH', 'OPTIONS'])
@safe_login_required
def update_stock(supply_id):
    supply = Med_Supply.query.filter_by(supply_id=supply_id, user_id=current_user.user_id).first()

    if not supply:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    new_qty = data.get("supply_stock")

    if new_qty is None:
        return jsonify({"error": "supply_stock required"}), 400

    supply.supply_stock = max(0, int(new_qty))
    db.session.commit()

    return jsonify({"message": "Updated", "supply_stock": supply.supply_stock}), 200

@meds_bp.route('/drug_stock/<int:supply_id>', methods=['DELETE', 'OPTIONS'])
@safe_login_required
def delete_drug(supply_id):
    supply = Med_Supply.query.filter_by(supply_id=supply_id, user_id=current_user.user_id).first()

    if not supply:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(supply)
    db.session.commit()

    return jsonify({"message": "Deleted"}), 200

@meds_bp.route('/drug_stock', methods=['GET'])
@login_required
def get_drug_stock():
    supplies = Med_Supply.query.filter_by(user_id=current_user.user_id).all()

    return jsonify([
        {
            "supply_id": s.supply_id,
            "lookup_id": s.lookup_id,
            "brand_name": s.medicine.brand_name if s.medicine else None,
            "generic_name": s.medicine.generic_name if s.medicine else None,
            "dosage_strength": s.medicine.dosage_strength if s.medicine else None,
            "dosage_form": s.medicine.dosage_form if s.medicine else None,
            "category": s.medicine.category if s.medicine else None,
            "supply_stock": s.supply_stock,
            "expiration_date": str(s.expiration_date) if s.expiration_date else None,
            "intakes_left": s.intakes_left,
        }
        for s in supplies
    ])