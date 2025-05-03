# swagger_server/models/product.py
# coding: utf-8

from swagger_server.database import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sku = db.Column(db.String(50), nullable=True)

    def __init__(self, name, quantity, price, category, description, sku, id=None):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.category = category
        self.description = description
        self.sku = sku

    @classmethod
    def from_dict(cls, dikt):

        return cls(
            id=dikt.get('id'),
            name=dikt.get('name'),
            quantity=dikt.get('quantity'),
            price=dikt.get('price'),
            category=dikt.get('category'),
            description=dikt.get('description'),
            sku=dikt.get('sku')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category,
            'description': self.description,
            'sku': self.sku
        }
