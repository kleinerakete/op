from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)

# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String, nullable=False)
    payload = db.Column(JSONB, nullable=False)
    context = db.Column(JSONB, default={})
    status = db.Column(db.String, default='INTAKE')
    price = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String, default='NONE')
    payment_reference = db.Column(db.String, nullable=True)
    flow_name = db.Column(db.String, nullable=True)
    result = db.Column(JSONB, nullable=True)
    error = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Operator(db.Model):
    __tablename__ = 'operators'
    name = db.Column(db.String, primary_key=True)
    description = db.Column(db.String)
    input_type = db.Column(db.String, default='generic')
    output_type = db.Column(db.String, default='generic')
    builtin = db.Column(db.String, nullable=True)
    success_count = db.Column(db.Integer, default=0)
    fail_count = db.Column(db.Integer, default=0)

class Flow(db.Model):
    __tablename__ = 'flows'
    name = db.Column(db.String, primary_key=True)
    problem_type = db.Column(db.String, nullable=False)
    base_price = db.Column(db.Float, default=10.0)
    price_per_complexity = db.Column(db.Float, default=1.0)
    steps = db.Column(JSONB, nullable=False) # List of steps

class RevenueEntry(db.Model):
    __tablename__ = 'revenue'
    id = db.Column(db.String, primary_key=True)
    problem_id = db.Column(db.String, db.ForeignKey('problems.id'))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String, default='EUR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
