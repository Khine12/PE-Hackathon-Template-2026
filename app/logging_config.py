import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging(app):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.handlers = []
    logger.addHandler(handler)

    app.logger.handlers = []
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info("Application started", extra={
        "component": "app",
        "event": "startup"
    })