from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from backend.extensions import db
from flask_login import UserMixin
from backend.extensions import login
from werkzeug.security import check_password_hash, generate_password_hash

# @login.user_loader
# def load_user(id):
#     return db.session.get(User, int(id))

class Drug_Lookup(db.Model):
    __tablename__ = "drug_lookup"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))

class Drug_Stock(db.Model):
    __tablename__ = "drug_stock"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))

    quantity: so.Mapped[int] = so.mapped_column(sa.Integer)

class Circle(db.Model):
    __tablename__ = "circles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    members = db.relationship("CircleMember", backref="circle", lazy=True)

class CircleMember(db.Model):
    __tablename__ = "circle_members"

    id = db.Column(db.Integer, primary_key=True)

    circle_id = db.Column(db.Integer, db.ForeignKey("circles.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    permission = db.Column(db.String(20), nullable=False)