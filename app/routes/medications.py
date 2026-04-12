from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Drug_Stock

meds_bp = Blueprint('meds', __name__)

def safe_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return "", 200
        return login_required(fn)(*args, **kwargs)
    return wrapper

@meds_bp.route('/drug_search', methods=['GET'])
def drug_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    results = Drug_Lookup.query.filter(
        (Drug_Lookup.brand_name.ilike(f"%{query}%")) |
        (Drug_Lookup.generic_name.ilike(f"%{query}%"))
    ).all()

    return jsonify([
        {
            "id": d.id,
            "brand_name": d.brand_name,
            "generic_name": d.generic_name,
            "dosage_form": d.dosage_form
        }
        for d in results
    ])

@meds_bp.route('/drug_stock', methods=['POST'])
@login_required
def add_drug():
    data = request.get_json(force=True)

    drug = Drug_Stock(
        user_id=current_user.id,
        brand_name=data.get("brand_name", ""),
        generic_name=data.get("generic_name", ""),
        dosage_form=data.get("dosage_form", ""),
        quantity=int(data.get("quantity")),
    )

    db.session.add(drug)
    db.session.commit()

    return jsonify({'message': 'Drug Added', 'id': drug.id}), 201

@meds_bp.route('/drug_stock/<int:drug_id>', methods=['PATCH', 'OPTIONS'])
@safe_login_required
def update_stock(drug_id):
    drug = Drug_Stock.query.filter_by(id=drug_id, user_id=current_user.id).first()
 
    if not drug:
        return jsonify({"error": "Not found"}), 404
 
    data = request.get_json()
    new_qty = data.get("quantity")
 
    if new_qty is None:
        return jsonify({"error": "quantity required"}), 400
 
    drug.quantity = max(0, int(new_qty))   # never go below 0
    db.session.commit()
 
    return jsonify({"message": "Updated", "quantity": drug.quantity}), 200
 
 
@meds_bp.route('/drug_stock/<int:drug_id>', methods=['DELETE', 'OPTIONS'])
@safe_login_required
def delete_drug(drug_id):
    drug = Drug_Stock.query.filter_by(id=drug_id, user_id=current_user.id).first()
 
    if not drug:
        return jsonify({"error": "Not found"}), 404
 
    db.session.delete(drug)
    db.session.commit()
 
    return jsonify({"message": "Deleted"}), 200

@meds_bp.route('/drug_stock', methods=['GET'])
@login_required
def get_drug_stock():
    drugs = Drug_Stock.query.all()

    return jsonify([
        {
            "id": d.id,
            "brand_name": d.brand_name,
            "generic_name": d.generic_name,
            "dosage_form": d.dosage_form,
            "quantity": d.quantity
        }
        for d in drugs
    ])