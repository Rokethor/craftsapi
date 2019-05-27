#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_expects_json import expects_json
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from config import DevelopmentConfig as test
from models import db, Product, ImageProduct
import json

app = Flask(__name__)
app.config.from_object(test)

schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'sku': {'type': 'string'},
        'description': {'type': 'string'},
        'stock': {'type': 'number'},
        'price': {'type': 'number'},
        'pictures': {'type': 'array'}
    },
    'required': ['name', 'sku', 'price']
}

@app.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/products', methods=['GET', 'POST'])
#@expects_json(schema)
def products(id=None):
    if request.method == 'GET':
        if not id:
            products = db.session.query(Product).filter(Product.deleted_at.is_(None))
            formatted_products = list()
            for product in products:
                formatted_products.append(product.convertToJSON())
            return json.dumps({ 'products': formatted_products }), 200, {'Content-Type': 'application/json'}
        else:
            product = db.session.query(Product).filter_by(id=id).filter(Product.deleted_at.is_(None)).first()
            if not product:
                return json.dumps({'errors': 'Product not found'}), 404
            return json.dumps({ 'product': product.convertToJSON() }), 200, {'Content-Type': 'application/json'}
    elif request.method == 'POST':
        content = request.get_json()
        if not content.has_key('name'):
            return json.dumps({'errors': 'Bad request - you must send the product name'}), 400
        if not content.has_key('sku'):
            return json.dumps({'errors': 'Bad request - you must send the product sku'}), 400
        if content.has_key('pictures') and len(content.get('pictures', [])) > 10:
            return json.dumps({'errors': 'Bad request - you can send up to 10 images'}), 400
        if not content.has_key('price'):
            return json.dumps({'errors': 'Bad request - you must send the product price'}), 400
        try:
            product = Product(**content)
            db.session.add(product)
            db.session.flush()
            db.session.commit()
            if content.has_key('pictures'):
                pictures = content.get('pictures', [])
                for pic in pictures:
                    imageProduct = ImageProduct()
                    imageProduct.product_id = product.id
                    imageProduct.real_uri = pic
                    imageProduct.custom_uri = imageProduct.formatCustomPath(product)
                    imageProduct.saveImage()
                    db.session.add(imageProduct)
                    db.session.commit()
            return json.dumps({'success': 'Product was created!', 'product': product.convertToJSON()}), 203
        except SQLAlchemyError as e:
            return json.dumps({'errors': str(e)}), 400
        except Exception as e:
            return json.dumps({'errors': str(e)}), 400
    elif request.method == 'PUT':
        if not id:
            return json.dumps({'errors': 'Bad request - you must specify the product id'}), 400
        content = request.get_json()
        try:
            product = db.session.query(Product).filter_by(id=id).first()
            if not product:
                return json.dumps({'errors': 'Product not found'}), 404
            if content.has_key('name'):
                product.name = Product.formatName(content.get('name', ''))
            if content.has_key('sku'):
                product.sku = Product.formatSKU(content.get('sku', ''))
            if content.has_key('description'):
                product.description = content.get('description', '')
            if content.has_key('stock'):
                product.stock = int(content.get('stock', ''))
            if content.has_key('price'):
                product.price = float(content.get('price', ''))
            db.session.add(product)
            db.session.commit()
            return json.dumps({'success': 'Product was updated!', 'product': product.convertToJSON()}), 200
        except SQLAlchemyError as e:
            return json.dumps({'errors': str(e)}), 400
        except TypeError:
            return json.dumps({'errors': 'The field does not have the correct format'}), 400
    elif request.method == 'DELETE':
        if not id:
            return json.dumps({'errors': 'Bad request - you must specify the product id'}), 400
        try:
            product = db.session.query(Product).filter_by(id=id).first()
            product.close()
            db.session.add(product)
            db.session.commit()
            for pic in product.pictures:
                pic.removeImage()
                db.session.delete(pic)
                db.session.commit()
            return json.dumps({'success': 'Product was deleted!'}), 200
        except IntegrityError as e:
            return json.dumps({'errors': str(e)}), 400
        except SQLAlchemyError as e:
            return json.dumps({'errors': str(e)}), 400
    return json.dumps({'errors': 'Resource not found'}), 404

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()
