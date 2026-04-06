"""Flask dashboard for GarmentScan analytics."""

import logging
from flask import Flask, render_template, jsonify
from bot import db

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__, template_folder="../templates")

    @app.route("/")
    def index():
        return render_template(
            "dashboard.html",
            stats=db.get_stats(),
            top_materials=db.get_top_materials(),
            recent=db.get_recent_scans(),
            users=db.get_users(),
        )

    @app.route("/api/stats")
    def api_stats():
        return jsonify(db.get_stats())

    @app.route("/user/<int:user_id>")
    def user_dashboard(user_id):
        user = db.get_user(user_id)
        if not user:
            return "User not found", 404
        return render_template(
            "user_dashboard.html",
            user=user,
            scans=db.get_user_scans(user_id),
        )

    return app
