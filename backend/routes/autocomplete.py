import csv
import os
from flask import Blueprint, request, jsonify

autocomplete_bp = Blueprint("autocomplete", __name__, url_prefix="/api")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "data", "drug_lookup_table.csv")

DATA = None

def load_drugs():
    global DATA
    if DATA is not None:
        return DATA
    
    if not os.path.exists(CSV_PATH):
        DATA = []
        return DATA

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
    DATA = items
    return DATA


@autocomplete_bp.route("/autocomplete")
def autocomplete():
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify([])

    results = []
    for drug in load_drugs():
        brand = (drug.get("brand_name") or "").lower()
        generic = (drug.get("generic_name") or "").lower()
        form = (drug.get("dosage_form") or "").lower()

        if query in brand or query in generic or query in form:
            results.append(drug)

    return jsonify(results[:10])