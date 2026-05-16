from models import db

class Generic(db.Model):
    __tablename__ = "generic"

    generic_id = db.Column(db.Integer, primary_key=True)
    generic_name = db.Column(db.String(100), nullable=False)
    dosage_strength = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "generic_id": self.generic_id,
            "generic_name": self.generic_name,
            "dosage_strength": self.dosage_strength,
        }