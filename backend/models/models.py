from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from extensions import db
from flask_login import UserMixin
from extensions import login
from werkzeug.security import check_password_hash, generate_password_hash

# @login.user_loader
# def load_user(id):
#     return db.session.get(User, int(id))

# USER

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(36), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)


# MED_LOOKUP

class Med_Lookup(db.Model):
    __tablename__ = "Med_Lookup"

    lookup_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_strength: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))


# MED_SUPPLY

class Med_Supply(db.Model):
    __tablename__ = "Med_Supply"

    supply_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    quantity: so.Mapped[int] = so.mapped_column(sa.Integer)
    # to put: [intakes_left(supply_left/ dosage_strength)]
    expiration_date: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))


# MED_LOOKUP

class CircleMember(db.Model):
    __tablename__ = "circle_members"

    id = db.Column(db.Integer, primary_key=True)

    circle_id = db.Column(db.Integer, db.ForeignKey("circles.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    permission = db.Column(db.String(20), nullable=False)