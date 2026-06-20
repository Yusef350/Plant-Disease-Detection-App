"""
Flask application factory.
Registers all blueprints, CORS, error handlers, and static file serving.
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from models.db import init_db
from routes.auth import auth_bp
from routes.scans import scans_bp
from routes.diseases import diseases_bp
from routes.users import users_bp
from routes.admin import admin_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── CORS (allow Flutter dev & production origins) ────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Register blueprints ──────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(scans_bp)
    app.register_blueprint(diseases_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)

    # ── Serve uploaded files (local fallback) ────────────────────────
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    # ── Health check ─────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "message": "Plant Disease Detection API"}), 200

    # ── Global error handlers ────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large (max 16 MB)"}), 413

    # ── Max upload size: 16 MB ───────────────────────────────────────
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # ── Initialize DB indexes on startup ─────────────────────────────
    with app.app_context():
        init_db()

    return app


# ── Entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
