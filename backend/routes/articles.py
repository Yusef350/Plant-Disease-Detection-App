from flask import Blueprint, request, jsonify
from middleware.auth import require_auth, require_admin
from models.article import list_articles, find_by_id, create_article, update_article, delete_article

articles_bp = Blueprint("articles", __name__)

# --- PUBLIC ROUTES ---

@articles_bp.route("", methods=["GET"])
def get_articles():
    category = request.args.get("category")
    search = request.args.get("search")
    articles = list_articles(category, search)
    return jsonify({
        "articles": articles,
        "total": len(articles)
    }), 200

@articles_bp.route("/<article_id>", methods=["GET"])
def get_article(article_id):
    article = find_by_id(article_id)
    if not article:
        return jsonify({"message": "Article not found"}), 404
    return jsonify({"article": article}), 200

# --- ADMIN ROUTES ---

@articles_bp.route("", methods=["POST"])
@require_admin
def add_article():
    data = request.json
    try:
        new_article = create_article(data)
        return jsonify({"article": new_article, "message": "Article created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@articles_bp.route("/<article_id>", methods=["PUT"])
@require_admin
def edit_article(article_id):
    data = request.json
    updated = update_article(article_id, data)
    if not updated:
        return jsonify({"message": "Update failed"}), 404
    return jsonify({"article": updated, "message": "Article updated"}), 200

@articles_bp.route("/<article_id>", methods=["DELETE"])
@require_admin
def remove_article(article_id):
    if delete_article(article_id):
        return jsonify({"message": "Article deleted"}), 200
    return jsonify({"message": "Delete failed"}), 404
