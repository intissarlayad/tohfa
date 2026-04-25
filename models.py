from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id      = db.Column(db.Integer, primary_key=True)
    full_name    = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role         = db.Column(db.String(20), nullable=False, default='client')  # 'client' | 'designer'
    margin_pct   = db.Column(db.Float, default=0.15)   # designer margin (15% default)
    bio          = db.Column(db.Text)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    selection = db.relationship('Selection', backref='client', uselist=False,
                                foreign_keys='Selection.client_id')
    designs   = db.relationship('Design', backref='designer',
                                foreign_keys='Design.designer_id')

    def get_id(self):
        return str(self.user_id)

    @property
    def is_designer(self):
        return self.role == 'designer'

    @property
    def is_client(self):
        return self.role == 'client'

    # ── Designer earnings ──────────────────────────────────────
    def total_earnings(self):
        """Sum of commissions from clients who picked this designer's designs."""
        total = 0.0
        for design in self.designs:
            for sel in design.selections:
                total += design.price * self.margin_pct
        return round(total, 2)

    def total_selections(self):
        """Number of clients who chose at least one of this designer's designs."""
        count = 0
        for design in self.designs:
            count += len(design.selections)
        return count


class Fabric(db.Model):
    __tablename__ = 'fabrics'
    fabric_id    = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    description  = db.Column(db.Text)
    image_url    = db.Column(db.String(255))
    availability = db.Column(db.Boolean, default=True)


class Design(db.Model):
    __tablename__ = 'designs'
    design_id   = db.Column(db.Integer, primary_key=True)
    designer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url   = db.Column(db.String(255))
    price       = db.Column(db.Float, default=500.0)   # base price in MAD
    is_active   = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    selections = db.relationship('Selection', backref='design',
                                 foreign_keys='Selection.design_id')


class Selection(db.Model):
    __tablename__ = 'user_selections'
    selection_id = db.Column(db.Integer, primary_key=True)
    client_id    = db.Column(db.Integer, db.ForeignKey('users.user_id'),
                             unique=True, nullable=False)
    fabric_id    = db.Column(db.Integer, db.ForeignKey('fabrics.fabric_id'), nullable=True)
    design_id    = db.Column(db.Integer, db.ForeignKey('designs.design_id'), nullable=True)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fabric = db.relationship('Fabric', foreign_keys=[fabric_id])
