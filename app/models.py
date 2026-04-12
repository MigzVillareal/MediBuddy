from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from .extensions import db
from flask_login import UserMixin
from .extensions import login
from werkzeug.security import check_password_hash, generate_password_hash

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(36), unique=True, index=True, nullable=False)

    password_hash = db.Column(db.String(256))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)

    circles = db.relationship("Circle", backref="owner", lazy=True)
    memberships = db.relationship("CircleMember", backref="user", lazy=True)
    
class Drug_Lookup(db.Model):
    __tablename__ = "drug_lookup"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))


class Drug_Stock(db.Model):
    __tablename__ = "drug_stock"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    drug_lookup_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("drug_lookup.id")
    )

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