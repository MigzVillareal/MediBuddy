from flask import Blueprint, jsonify

meds_bp = Blueprint('meds', __name__)

@meds_bp.route('/medications', methods=['POST'])
def search():
    return jsonify({'message': 'endpoint'}), 200

@meds_bp.route('/medications', methods=['DELETE'])
def add_medication():
    data = request.get_json()

    Generic = (data.get("Generic_Name") or "").strip()
    
    Drug = Medication(
        Drug_Name=Generic_Name,
        Dosage_Strength=Dosage_Strength
    )

    db.session.add(Drug)
    db.session.commit()

    return jsonify({'message': 'Drug Registered'}), 200
