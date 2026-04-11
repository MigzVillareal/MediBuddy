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
        Drug.drug_name.ilike(f"%{query}%")
    ).all()

    return jsonify([
        {
            "id": d.id,
            "drug_name": d.drug_name,
            "dosage_strength": d.dosage_strength
        }
        for d in results
    ])

@meds_bp.route('/drug_stock', methods=['POST'])
def add_drug():
    data = request.get_json()

    drug_name = (data.get("drug_name") or "").strip()
    dosage_strength = (data.get("dosage_strength") or "").strip()

    if not drug_name:
        return jsonify({"error": "drug_name is required"}), 400

    drug = Drug(
        drug_name=drug_name,
        dosage_strength=dosage_strength
    )

    db.session.add(drug)
    db.session.commit()

    return jsonify({"message": "Drug added successfully"}), 201