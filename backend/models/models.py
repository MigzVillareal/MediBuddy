from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from extensions import db
from flask_login import UserMixin
from extensions import login
from werkzeug.security import check_password_hash, generate_password_hash

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# USER

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(36), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# PRESCRIPTION

class Prescription(db.Model):
    __tablename__ = "prescriptions"

    prescription_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    Description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    Date: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    Doctor: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    Detail: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))


# PRESCRIPTION_DETAIL

class Prescription_Detail(db.Model):
    __tablename__ = "prescription_details"

    prescription_detail_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    Description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    date_start: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, nullable=True)
    date_end: so.Mapped[Optional[sa.DateTime]] = so.mapped_column(sa.DateTime, nullable=True)


# ALARM

# class ALARM


# MED_LOOKUP

class Med_Lookup(db.Model):
    __tablename__ = "med_lookup"

    lookup_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_strength: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))


# MED_SUPPLY

class Med_Supply(db.Model):
    __tablename__ = "med_supply"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    quantity: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    expiration_date: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))


# CIRCLE
# owner_id identifies who created/owns the circle and can manage members/permissions

class Circle(db.Model):
    __tablename__ = "circles"

    circle_id = db.Column(db.Integer, primary_key=True)
    circle_name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    members = db.relationship("CircleMember", backref="circle", lazy=True, cascade="all, delete-orphan")
    invites = db.relationship("CircleInvite", backref="circle", lazy=True, cascade="all, delete-orphan")


# CIRCLE_MEMBER
# Stores accepted members only; permission = 'canview' | 'canedit'

class CircleMember(db.Model):
    __tablename__ = "circle_members"

    circle_member_id = db.Column(db.Integer, primary_key=True)
    circle_id = db.Column(db.Integer, db.ForeignKey("circles.circle_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    permission = db.Column(db.String(20), nullable=False, default="canview")


# CIRCLE_INVITE
# Represents a pending invite from a circle owner to another user.
# status: 'pending' | 'accepted' | 'rejected'

class CircleInvite(db.Model):
    __tablename__ = "circle_invites"

    invite_id = db.Column(db.Integer, primary_key=True)
    circle_id = db.Column(db.Integer, db.ForeignKey("circles.circle_id"), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    permission = db.Column(db.String(20), nullable=False, default="canview")
    status = db.Column(db.String(20), nullable=False, default="pending")