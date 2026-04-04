from flask import Blueprint, jsonify, request
from peewee import IntegrityError
from playhouse.shortcuts import model_to_dict

from app.models.product import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET"])
def list_products():
    products = Product.select().where(Product.is_active == True)
    return jsonify([model_to_dict(p) for p in products])


@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = Product.get_by_id(product_id)
    except Product.DoesNotExist:
        return jsonify({"error": "Product not found"}), 404

    if not product.is_active:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(model_to_dict(product))


@products_bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = ["name", "category", "price"]
    missing = [f for f in required_fields if f not in data or data[f] is None]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    if not isinstance(data["name"], str) or len(data["name"].strip()) == 0:
        return jsonify({"error": "Name must be a non-empty string"}), 400

    if not isinstance(data["category"], str) or len(data["category"].strip()) == 0:
        return jsonify({"error": "Category must be a non-empty string"}), 400

    try:
        price = float(data["price"])
        if price < 0:
            return jsonify({"error": "Price must be non-negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Price must be a number"}), 400

    stock = data.get("stock", 0)
    try:
        stock = int(stock)
        if stock < 0:
            return jsonify({"error": "Stock must be non-negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Stock must be an integer"}), 400

    try:
        product = Product.create(
            name=data["name"].strip(),
            category=data["category"].strip(),
            price=price,
            stock=stock,
        )
    except IntegrityError:
        return jsonify({"error": "A product with that name already exists"}), 409

    return jsonify(model_to_dict(product)), 201


@products_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        product = Product.get_by_id(product_id)
    except Product.DoesNotExist:
        return jsonify({"error": "Product not found"}), 404

    if not product.is_active:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "name" in data:
        if not isinstance(data["name"], str) or len(data["name"].strip()) == 0:
            return jsonify({"error": "Name must be a non-empty string"}), 400
        product.name = data["name"].strip()

    if "category" in data:
        if not isinstance(data["category"], str) or len(data["category"].strip()) == 0:
            return jsonify({"error": "Category must be a non-empty string"}), 400
        product.category = data["category"].strip()

    if "price" in data:
        try:
            price = float(data["price"])
            if price < 0:
                return jsonify({"error": "Price must be non-negative"}), 400
            product.price = price
        except (ValueError, TypeError):
            return jsonify({"error": "Price must be a number"}), 400

    if "stock" in data:
        try:
            stock = int(data["stock"])
            if stock < 0:
                return jsonify({"error": "Stock must be non-negative"}), 400
            product.stock = stock
        except (ValueError, TypeError):
            return jsonify({"error": "Stock must be an integer"}), 400

    try:
        product.save()
    except IntegrityError:
        return jsonify({"error": "A product with that name already exists"}), 409

    return jsonify(model_to_dict(product))


@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        product = Product.get_by_id(product_id)
    except Product.DoesNotExist:
        return jsonify({"error": "Product not found"}), 404

    product.is_active = False
    product.save()
    return jsonify({"message": "Product deleted"}), 200