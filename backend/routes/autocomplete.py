import csv
import os
from flask import Blueprint, request, jsonify

autocomplete_bp = Blueprint("autocomplete", __name__, url_prefix="/api")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "data", "drug_lookup_table.csv")


def load_drugs():
    items = []

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            items.append({
                "generic_name": row.get("Generic Name") or row.get("generic_name"),
                "brand_name": row.get("Brand Name") or row.get("brand_name"),
                "dosage_strength": row.get("Dosage Strength") or row.get("dosage_strength"),
                "dosage_form": row.get("Dosage Form") or row.get("dosage_form"),
            })

    return items


DATA = load_drugs()


@autocomplete_bp.route("/autocomplete")
def autocomplete():
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([])

    results = []

    for drug in DATA:
        brand = (drug.get("brand_name") or "").lower()
        generic = (drug.get("generic_name") or "").lower()
        form = (drug.get("dosage_form") or "").lower()

        if query in brand or query in generic or query in form:
            results.append(drug)

    return jsonify(results[:10])