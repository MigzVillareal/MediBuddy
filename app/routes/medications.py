from flask import Blueprint, jsonify, request
from app import db
from app.models import Drug_Stock

meds_bp = Blueprint('meds', __name__)


@meds_bp.route('/drug_search', methods=['GET'])
def drug_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    results = Drug.query.filter(
        Drug.name.ilike(f"%{query}%")
    ).all()

    return jsonify([
        {
            "id": d.id,
            "drug_name": d.name,
            "dosage_strength": d.strength
        }
        for d in results
    ])

@meds_bp.route('/drug_stock', methods=['POST'])
def add_drug():
    data = request.get_json()

    brand_name = (data.get("Brand_Name") or "").strip()
    generic_name = (data.get("Generic_Name") or "").strip()
    dosage_form = (data.get("Dosage_Form") or "").strip()
    quantity = (data.get("Quantity") or "").strip()

    if not drug_name:
        return jsonify({"error": "Generic_Name is required"}), 400

    drug = Drug_Stock(
        brand_name=brand_name,
        generic_name=generic_name,
        dosage_form=dosage_form,
        quantity=quantity,
    )

    db.session.add(drug)
    db.session.commit()

    return jsonify({'message': 'Drug Added'}), 201