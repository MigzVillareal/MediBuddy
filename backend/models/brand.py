from models import db

class Brand(db.Model):
    __tablename__ = "brand"

    brand_id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(100), nullable=False)
    
    generic_info = db.relationship("Generic", backref="brands", lazy=True)
    
    def to_dict(self):
        return {
            "brand_id": self.brand_id,
            "brand_name": self.brand_name,
        }