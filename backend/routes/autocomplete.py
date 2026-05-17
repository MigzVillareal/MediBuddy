from flask import Blueprint, request, jsonify
from extensions import db
from models import Med_Lookup

autocomplete_bp = Blueprint("autocomplete", __name__)

@autocomplete_bp.route("/", strict_slashes=False)
def autocomplete():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    like = f"%{query}%"

    # Priority 1: brand_name or generic_name starts with the query
    starts = Med_Lookup.query.filter(
        db.or_(
            Med_Lookup.brand_name.ilike(f"{query}%"),
            Med_Lookup.generic_name.ilike(f"{query}%"),
        )
    ).limit(10).all()

    # Priority 2: brand_name or generic_name contains the query (anywhere)
    contains = []
    if len(starts) < 10:
        seen_ids = {m.lookup_id for m in starts}
        extra = Med_Lookup.query.filter(
            db.and_(
                Med_Lookup.lookup_id.notin_(seen_ids),
                db.or_(
                    Med_Lookup.brand_name.ilike(like),
                    Med_Lookup.generic_name.ilike(like),
                )
            )
        ).limit(10 - len(starts)).all()
        contains = extra

    results = starts + contains

    # Priority 3: fill remaining slots from dosage_form / category if still under 10
    if len(results) < 10:
        seen_ids = {m.lookup_id for m in results}
        fallback = Med_Lookup.query.filter(
            db.and_(
                Med_Lookup.lookup_id.notin_(seen_ids),
                db.or_(
                    Med_Lookup.dosage_form.ilike(like),
                    Med_Lookup.category.ilike(like),
                )
            )
        ).limit(10 - len(results)).all()
        results += fallback

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