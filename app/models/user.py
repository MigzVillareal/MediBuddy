from models import db

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

    drug_stocks = db.relationship("Drug_Stock", backref="user", lazy=True)

    circles = db.relationship("Circle", backref="owner", lazy=True)
    memberships = db.relationship("CircleMember", backref="user", lazy=True)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,

        }