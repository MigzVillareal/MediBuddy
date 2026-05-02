from models import db

class Brand(db.Model):
    __tablename__ = "brand"

    brand_id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(100), nullable=False)

    brand_supply = db.relationship("HealthSupply", backref="Brand", lazy=True)
    