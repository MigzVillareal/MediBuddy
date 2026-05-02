from models import db

class Generic(db.Model):
    __tablename__ = "generic"

    generic_id = db.Column(db.Integer, primary_key=True)
    generic_name = db.Column(db.String(100), nullable=False)
    dosage_strength = db.Column(db.String(50), nullable=False)

    GenericBrand = db.relationship("Brand", backref="Generic", lazy=True)