# swagger_server/controllers/product_controller.py

import connexion
from flask import jsonify
from swagger_server.database import db
from swagger_server.models.product import Product
from swagger_server.logger import logger
from opentelemetry import trace

# Получаем трейсер
tracer = trace.get_tracer(__name__)


def add_product(body):
    """Создать товар"""
    if connexion.request.is_json:
        data = connexion.request.get_json()
        new_product = Product(
            name=data.get('name'),
            quantity=data.get('quantity'),
            price=data.get('price'),
            category=data.get('category'),
            description=data.get('description'),
            sku=data.get('sku')
        )
        # Создаем спан для добавления продукта
        with tracer.start_span("add_product") as span:
            try:
                db.session.add(new_product)
                db.session.commit()
                logger.info("Товар создан ")
                span.set_attribute("product.name", new_product.name)
                return jsonify(new_product.to_dict()), 201
            except Exception as e:
                logger.error("Ошибка при добавлении товара: %s", str(e))
                span.record_exception(e)
                return {"message": "Ошибка при добавлении товара"}, 500
    return {"message": "Неверный формат"}, 400


def get_product_by_id(id_):
    """Получить продукт по ID"""
    with tracer.start_span("get_product_by_id") as span:
        product = Product.query.get(id_)
        if product:
            return jsonify(product.to_dict()), 200

        logger.error("Товар не найден, ID: %s", id_)
        span.set_attribute("product.id", id_)
        span.add_event("Товар не найден")
        return {"message": "Товар не найден"}, 404


def update_product(body, id_):
    """Обновить существующий товар"""
    product = Product.query.get(id_)
    if not product:
        logger.error("Товар для обновления не найден")
        return {"message": "Товар не найден"}, 404

    if connexion.request.is_json:
        data = connexion.request.get_json()
        product.name = data.get('name', product.name)
        product.quantity = data.get('quantity', product.quantity)
        product.price = data.get('price', product.price)
        product.category = data.get('category', product.category)
        product.description = data.get('description', product.description)
        product.sku = data.get('sku', product.sku)

        db.session.commit()
        logger.info("Товар обновлен, ID: %s", id_)
        return jsonify(product.to_dict()), 200
    return {"message": "Неверный формат"}, 400


def delete_product(id_):
    """Удалить товар"""
    product = Product.query.get(id_)
    if not product:
        logger.error("Товар для удаления не найден")
        return {"message": "Товар не найден"}, 404

    db.session.delete(product)
    db.session.commit()
    logger.info("Товар удален")
    return {"message": "Товар успешно удален"}, 204


def search_products_by_category(category):
    """Поиск товаров по категории"""
    products = Product.query.filter_by(category=category).all()
    if products:
        return jsonify([product.to_dict() for product in products]), 200
    return {"message": "Товары не найдены"}, 404


def get_all_categories():
    """Получить все категории товаров"""
    categories = db.session.query(Product.category).distinct().all()
    categories_list = [category[0] for category in categories]
    if categories_list:
        return jsonify(categories_list), 200
    return {"message": "Категории не найдены"}, 404
