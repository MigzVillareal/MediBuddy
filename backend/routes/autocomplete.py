from flask import Blueprint, request, jsonify
from sqlalchemy import case
from extensions import db
from models import Med_Lookup

autocomplete_bp = Blueprint("autocomplete", __name__)

@autocomplete_bp.route("/", strict_slashes=False)
def autocomplete():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    like      = f"%{q}%"
    starts    = f"{q}%"

    # Single query — results ordered by relevance:
    #   rank 1 → brand_name or generic_name starts with query
    #   rank 2 → brand_name or generic_name contains query anywhere
    #   rank 3 → dosage_form or category contains query (fallback)
    priority = case(
        (
            db.or_(
                Med_Lookup.brand_name.ilike(starts),
                Med_Lookup.generic_name.ilike(starts),
            ),
            1,
        ),
        (
            db.or_(
                Med_Lookup.brand_name.ilike(like),
                Med_Lookup.generic_name.ilike(like),
            ),
            2,
        ),
        else_=3,
    )

    results = (
        Med_Lookup.query
        .filter(
            db.or_(
                Med_Lookup.brand_name.ilike(like),
                Med_Lookup.generic_name.ilike(like),
                Med_Lookup.dosage_form.ilike(like),
                Med_Lookup.category.ilike(like),
            )
        )
        .order_by(priority)
        .limit(10)
        .all()
    )

    return jsonify([
        {
            "lookup_id":       m.lookup_id,
            "brand_name":      m.brand_name,
            "generic_name":    m.generic_name,
            "dosage_strength": m.dosage_strength,
            "dosage_form":     m.dosage_form,
            "category":        m.category,
        }
        for m in results
    ])