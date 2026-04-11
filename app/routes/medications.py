from flask import Blueprint, jsonify, request
from app import db
from app.models import Medication

meds_bp = Blueprint('meds', __name__)

@meds_bp.route('/drug_search', methods=['GET'])
def drug_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query required"}), 400

    results = Medication.query.filter(
        Medication.Drug_Name.ilike(f"%{query}%")
    ).all()

    return jsonify([
        {
            "id": drug.id,
            "name": drug.Drug_Name,
            "dosage": drug.Dosage_Strength
        }
        for drug in results
    ])

@meds_bp.route('/drug_stock', methods=['POST'])
def add_drug():
    data = request.get_json()

    generic_name = (data.get("Generic_Name") or "").strip()
    dosage_strength = (data.get("Dosage_Strength") or "").strip()

    if not generic_name:
        return jsonify({"error": "Generic_Name is required"}), 400

    drug = Medication(
        Drug_Name=generic_name,
        Dosage_Strength=dosage_strength
    )

    db.session.add(drug)
    db.session.commit()

    return jsonify({'message': 'Drug Registered'}), 201