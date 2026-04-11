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
    __tablename__="users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    username: so.Mapped[str] = so.mapped_column(
        sa.String(36), index=True, unique=True
    )
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(256)
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
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