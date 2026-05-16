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


# PRESCRIPTION

class Prescription(db.Model):
    __tablename__ = "prescriptions"

    prescription_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    Description:
    # to put: duration(date_start, date_end)
    # to put: {schedule(set_day, set_time,set_frequency)}


# PRESCRIPTION_DETAIL

class Prescription_Detail(db.Model):
    __tablename__ = "prescription_details"

    prescription_detail_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    Description: so.Mapped[str] = so.mapped_column(sa.String(120))
    # to put: duration(date_start, date_end)
    # to put: {schedule(set_day, set_time,set_frequency)}


# MED_LOOKUP

class Med_Lookup(db.Model):
    __tablename__ = "med_lookup"

    lookup_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_strength: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))


# MED_SUPPLY

class Med_Supply(db.Model):
    __tablename__ = "med_supply"

    supply_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    quantity: so.Mapped[int] = so.mapped_column(sa.Integer)
    # to put: [intakes_left(supply_left/ dosage_strength)]
    expiration_date: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))


# CIRCLE

class Circle(db.Model):
    __tablename__ = "circles"

    circle_id = db.Column(db.Integer, primary_key=True)
    circle_name = db.Column(db.String(100), nullable=False)

    members = db.relationship("CircleMember", backref="circle", lazy=True)


# CIRCLE_MEMBER

class CircleMember(db.Model):
    __tablename__ = "circle_members"

    circle_member_id = db.Column(db.Integer, primary_key=True)

    circle_id = db.Column(db.Integer, db.ForeignKey("circles.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))