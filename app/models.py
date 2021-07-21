from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)


class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True, nullable=False)
    address = db.Column(db.Float, unique=False, nullable=False)


