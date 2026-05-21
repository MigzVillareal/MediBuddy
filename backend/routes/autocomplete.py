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

    words = q.split()
    starts = f"{words[0]}%"
    like_first = f"%{words[0]}%"

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
                Med_Lookup.brand_name.ilike(like_first),
                Med_Lookup.generic_name.ilike(like_first),
            ),
            2,
        ),
        else_=3,
    )

    word_filters = [
        db.or_(
            Med_Lookup.brand_name.ilike(f"%{w}%"),
            Med_Lookup.generic_name.ilike(f"%{w}%"),
            Med_Lookup.dosage_form.ilike(f"%{w}%"),
            Med_Lookup.category.ilike(f"%{w}%"),
        )
        for w in words
    ]

    results = (
        Med_Lookup.query
        .filter(db.and_(*word_filters))
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