from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    base_price_per_sqft = db.Column(db.Float, nullable=False)
    growth_rate = db.Column(db.Float, default=0.05)  # Annual growth rate
    population = db.Column(db.Integer)
    tier = db.Column(db.String(20))  # Tier 1, Tier 2, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    localities = db.relationship('Locality', backref='city', lazy=True)

class Locality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    price_per_sqft = db.Column(db.Float, nullable=False)
    location_multiplier = db.Column(db.Float, default=1.0)
    area_type = db.Column(db.String(50))  # residential, commercial, agricultural
    pin_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class InfrastructureMultiplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factor_type = db.Column(db.String(50), nullable=False)  # road_width, metro, school, etc.
    factor_value = db.Column(db.String(50), nullable=False)  # value range or category
    multiplier = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PriceEstimate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(100))
    plot_size_sqft = db.Column(db.Float, nullable=False)
    road_width_ft = db.Column(db.Float)
    nearby_schools = db.Column(db.Boolean, default=False)
    nearby_metro = db.Column(db.Boolean, default=False)
    commercial_area = db.Column(db.Boolean, default=False)
    year = db.Column(db.Integer, nullable=False)
    estimated_price_per_sqft = db.Column(db.Float, nullable=False)
    total_estimated_price = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    api_key = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    rate_limit = db.Column(db.Integer, default=50)  # requests per hour
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
