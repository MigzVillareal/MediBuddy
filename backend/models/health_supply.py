from models import db

class HealthSupply(db.Model):
    __tablename__ = "health_supply"

    supply_id = db.Column(db.Integer, primary_key=True)

    brand_info = db.relationship("Brand", backref="supplies", lazy=True)

    def to_dict(self):
        return {
            "supply_id": self.supply_id,
        }