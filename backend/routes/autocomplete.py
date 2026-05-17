from flask import Blueprint, request, jsonify
from extensions import db
from models import Med_Lookup

autocomplete_bp = Blueprint("autocomplete", __name__)

@autocomplete_bp.route("/", strict_slashes=False)
def autocomplete():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    results = Med_Lookup.query.filter(
        db.or_(
            Med_Lookup.brand_name.ilike(f"%{query}%"),
            Med_Lookup.generic_name.ilike(f"%{query}%"),
            Med_Lookup.dosage_form.ilike(f"%{query}%"),
            Med_Lookup.category.ilike(f"%{query}%"),
        )
    ).limit(10).all()

    return jsonify([
        {
            "lookup_id": m.lookup_id,
            "brand_name": m.brand_name,
            "generic_name": m.generic_name,
            "dosage_strength": m.dosage_strength,
            "dosage_form": m.dosage_form,
            "category": m.category,
        }
        for m in results
    ])