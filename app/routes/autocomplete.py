import csv
import os
from flask import Blueprint, request, jsonify, make_response

autocomplete_bp = Blueprint("autocomplete", __name__, url_prefix="/api")

# CSV path (safe version)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "data", "drugs.csv")


def load_drugs():
    items = []
    with open("app/data/drug_lookup_table.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)
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

        if (
            query in brand
            or query in generic
            or query in form
        ):
            results.append({
                "brand_name": drug.get("brand_name"),
                "generic_name": drug.get("generic_name"),
                "dosage_form": drug.get("dosage_form"),
            })

    return jsonify(results[:10])