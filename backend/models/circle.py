from models import db

class Circle(db.Model):
    __tablename__ = "circles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    members = db.relationship("CircleMember", backref="circle", lazy=True)