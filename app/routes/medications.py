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

    drug_lookup_id = data.get("drug_lookup_id")
    quantity = data.get("quantity")

    if not drug_lookup_id:
        return jsonify({"error": "drug_lookup_id is required"}), 400

    if quantity is None:
        return jsonify({"error": "quantity is required"}), 400

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return jsonify({"error": "quantity must be a number"}), 400

    lookup_drug = db.session.get(Drug_Lookup, drug_lookup_id)

    if not lookup_drug:
        return jsonify({"error": "Drug not found"}), 404

    drug = Drug_Stock(
        drug_lookup_id=lookup_drug.id,
        brand_name=lookup_drug.brand_name,
        generic_name=lookup_drug.generic_name,
        dosage_form=lookup_drug.dosage_form,
        quantity=quantity
    )

    db.session.add(drug)
    db.session.commit()

    return jsonify({
        "message": "Drug added to stock",
        "drug": {
            "id": drug.id,
            "brand_name": drug.brand_name,
            "generic_name": drug.generic_name,
            "dosage_form": drug.dosage_form,
            "quantity": drug.quantity
        }
    }), 201