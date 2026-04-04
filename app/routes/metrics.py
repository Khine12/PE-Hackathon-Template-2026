import os
import psutil
from flask import Blueprint, jsonify

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/metrics")
def metrics():
    process = psutil.Process(os.getpid())
    memory = process.memory_info()

    return jsonify({
        "cpu": {
            "system_percent": psutil.cpu_percent(interval=0.1),
            "process_percent": process.cpu_percent()
        },
        "memory": {
            "system_total_mb": round(psutil.virtual_memory().total / 1024 / 1024, 1),
            "system_used_percent": psutil.virtual_memory().percent,
            "process_rss_mb": round(memory.rss / 1024 / 1024, 1),
            "process_vms_mb": round(memory.vms / 1024 / 1024, 1)
        },
        "disk": {
            "total_gb": round(psutil.disk_usage("/").total / 1024 / 1024 / 1024, 1),
            "used_percent": psutil.disk_usage("/").percent
        }
    })