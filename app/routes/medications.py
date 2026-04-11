from flask import Blueprint, jsonify, request
from app import db
from app.models import Drug

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

    generic_name = (data.get("Generic_Name") or "").strip()
    dosage_strength = (data.get("Dosage_Strength") or "").strip()

    if not drug_name:
        return jsonify({"error": "Generic_Name is required"}), 400

    drug = Drug(
        drug_name=drug_name,
        dosage_strength=dosage_strength
    )

    db.session.add(drug)
    db.session.commit()

    return jsonify({'message': 'Drug Added'}), 201