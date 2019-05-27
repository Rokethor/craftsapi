from flask_sqlalchemy import SQLAlchemy
import datetime
import os

db = SQLAlchemy()


class Product(db.Model):

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(100))
    sku = db.Column(db.String(60))
    description = db.Column(db.Text(), nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    pictures = db.relationship('ImageProduct')

    def __init__(self, **kwargs):
        self.name = self.formatName(kwargs.get('name', ''))
        self.sku = self.formatSKU(kwargs.get('sku', ''))
        self.description = kwargs.get('description', '')
        self.stock = kwargs.get('stock', 0)
        self.price = kwargs.get('price', 0.)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def close(self):
        self.deleted_at = datetime.datetime.now

    def convertToJSON(self):
        formatted_product = {
            'id': self.id,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'stock': self.stock,
            'price': self.price
        }
        for i, pic in enumerate(self.pictures, start=1):
            if not formatted_product.has_key('pictures'):
                formatted_product['pictures'] = list()
            formatted_product['pictures'].append({i: pic.custom_uri})
        return formatted_product

    @classmethod
    def formatName(obj, name):
        return name.strip(' ').lower().title()

    @classmethod
    def formatSKU(obj, sku):
        return sku.replace(' ', '')

FOLDER = os.path.abspath('images/products/')


class ImageProduct(db.Model):

    __tablename__ = 'images_product'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now)
    deleted_at = db.Column(db.DateTime, nullable=True)
    real_uri = db.Column(db.String(256), nullable=False)
    custom_uri = db.Column(db.String(256), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    def saveImage(self):
        fileName = FOLDER + "/" + self.custom_uri
        with open(fileName, 'wb') as f:
            f.write(self.readImage(self.real_uri))
            f.close()

    def readImage(self, url):
        from urllib import urlopen
        response = urlopen(url)
        return response.read()

    def removeImage(self):
        fileName = FOLDER + "/" + self.custom_uri
        try:
            os.remove(fileName)
        except Exception as e:
            pass

    def formatCustomPath(self, product):
        from functions import convertToBase62
        return datetime.datetime.today().strftime('%Y%m%d%H%M%S') + "_" + product.sku + "_" + convertToBase62(product.id) + "." + self.real_uri.split('.')[-1]
