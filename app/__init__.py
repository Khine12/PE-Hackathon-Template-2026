from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import init_db
from app.routes import register_routes


def create_app():
    load_dotenv()

    app = Flask(__name__)

    init_db(app)

    from app.logging_config import setup_logging
    setup_logging(app)

    from app import models  # noqa: F401 - registers models with Peewee
    from app.models.product import Product
    from app.database import db
    db.connect(reuse_if_open=True)
    db.create_tables([Product], safe=True)
    db.close()

    register_routes(app)

    from app.routes.metrics import metrics_bp
    app.register_blueprint(metrics_bp)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app