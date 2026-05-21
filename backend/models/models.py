from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from extensions import db
from flask_login import UserMixin
from extensions import login
from werkzeug.security import check_password_hash, generate_password_hash


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


# ── USER ──────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(36), unique=True, index=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    first_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    last_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))

    # relationships
    prescriptions: so.Mapped[List["Prescription"]] = so.relationship("Prescription", back_populates="user")
    med_supplies: so.Mapped[List["Med_Supply"]] = so.relationship("Med_Supply", back_populates="user")
    circle_memberships: so.Mapped[List["CircleMember"]] = so.relationship(
        "CircleMember",
        primaryjoin="CircleMember.user_id == User.user_id",
        foreign_keys="[CircleMember.user_id]",
        back_populates="user",
    )
    sent_invites: so.Mapped[List["CircleMember"]] = so.relationship(
        "CircleMember",
        primaryjoin="CircleMember.inviter_id == User.user_id",
        foreign_keys="[CircleMember.inviter_id]",
        back_populates="inviter",
    )

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ── PRESCRIPTION ──────────────────────────────────────────────────────────────

class Prescription(db.Model):
    __tablename__ = "prescriptions"

    prescription_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(120))
    date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    doctor: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    detail: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    alarm_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.user_id"))

    # relationships
    user: so.Mapped["User"] = so.relationship("User", back_populates="prescriptions")
    prescription_details: so.Mapped[List["Prescription_Detail"]] = so.relationship("Prescription_Detail", back_populates="prescription", cascade="all, delete-orphan")
    circle: so.Mapped[Optional["Circle"]] = so.relationship("Circle", back_populates="prescription", cascade="all, delete-orphan", uselist=False)


# ── PRESCRIPTION_DETAIL ───────────────────────────────────────────────────────

class Prescription_Detail(db.Model):
    __tablename__ = "prescription_details"

    prescription_detail_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date_start: so.Mapped[sa.Date] = so.mapped_column(sa.Date)
    date_end: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)
    time_taken: so.Mapped[str] = so.mapped_column(sa.String(100))
    days_taken: so.Mapped[str] = so.mapped_column(sa.String(20))
    onesignal_id: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    job_reference: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))

    prescription_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("prescriptions.prescription_id"))
    supply_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("med_supply.supply_id"))

    # relationships
    prescription: so.Mapped["Prescription"] = so.relationship("Prescription", back_populates="prescription_details")
    supply: so.Mapped[Optional["Med_Supply"]] = so.relationship("Med_Supply", back_populates="prescription_details")


# ── MED_LOOKUP ────────────────────────────────────────────────────────────────

class Med_Lookup(db.Model):
    __tablename__ = "med_lookup"

    lookup_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    brand_name: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    generic_name: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    dosage_strength: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    dosage_form: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    category: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)


# ── MED_SUPPLY ────────────────────────────────────────────────────────────────

class Med_Supply(db.Model):
    __tablename__ = "med_supply"

    supply_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    supply_stock: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    expiration_date: so.Mapped[Optional[sa.Date]] = so.mapped_column(sa.Date)

    lookup_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("med_lookup.lookup_id"))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.user_id"))

    # relationships
    medicine: so.Mapped["Med_Lookup"] = so.relationship("Med_Lookup")
    user: so.Mapped["User"] = so.relationship("User", back_populates="med_supplies")
    prescription_details: so.Mapped[list["Prescription_Detail"]] = so.relationship("Prescription_Detail", back_populates="supply")

    @property
    def intakes_left(self):
        try:
            strength = float(self.medicine.dosage_strength)
            return self.supply_stock / strength
        except (TypeError, ValueError, ZeroDivisionError):
            return None


# ── CIRCLE ────────────────────────────────────────────────────────────────────

class Circle(db.Model):
    __tablename__ = "circles"

    circle_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # owner of the circle
    owner_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.user_id"))
    prescription_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("prescriptions.prescription_id"))

    # relationships
    owner: so.Mapped["User"] = so.relationship("User", foreign_keys=[owner_id])
    prescription: so.Mapped["Prescription"] = so.relationship("Prescription", back_populates="circle")
    members: so.Mapped[List["CircleMember"]] = so.relationship("CircleMember", back_populates="circle", cascade="all, delete-orphan")

    @property
    def circle_name(self):
        return f"{self.prescription.user.username}'s {self.prescription.name}"


# ── CIRCLE_MEMBER ─────────────────────────────────────────────────────────────
# Doubles as both invite record and accepted-member record.
# status: 'pending' | 'accepted' | 'rejected'
# permission: 'canview' | 'canedit'
# inviter_id: user who sent the invite (the circle owner)

class CircleMember(db.Model):
    __tablename__ = "circle_members"

    circle_member_id: so.Mapped[int] = so.mapped_column(primary_key=True)

    circle_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("circles.circle_id"))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.user_id"))
    inviter_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("users.user_id"), nullable=True)

    permission: so.Mapped[str] = so.mapped_column(sa.String(20), default="canview")
    status: so.Mapped[str] = so.mapped_column(sa.String(20), default="pending")

    # relationships
    circle: so.Mapped["Circle"] = so.relationship("Circle", back_populates="members")
    user: so.Mapped["User"] = so.relationship(
        "User",
        primaryjoin="CircleMember.user_id == User.user_id",
        foreign_keys="[CircleMember.user_id]",
        back_populates="circle_memberships",
    )
    inviter: so.Mapped[Optional["User"]] = so.relationship(
        "User",
        primaryjoin="CircleMember.inviter_id == User.user_id",
        foreign_keys="[CircleMember.inviter_id]",
        back_populates="sent_invites",
    )