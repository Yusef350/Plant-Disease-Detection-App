"""
Article model for the Knowledge Base.
Categories: Guide, Tips, Organic, Science
"""
from datetime import datetime, timezone
from bson import ObjectId
from marshmallow import Schema, fields, post_load
from models.db import get_db

class Article:
    def __init__(self, title, category, content, additional_info=None, icon=None, _id=None):
        self._id = _id
        self.title = title
        self.category = category  # Guide, Tips, Organic, Science
        self.content = content
        self.additional_info = additional_info or ""
        self.icon = icon
        self.created_at = datetime.now(timezone.utc)

class ArticleSchema(Schema):
    id = fields.Str(dump_only=True, attribute="_id")
    title = fields.Str(required=True)
    category = fields.Str(required=True)
    content = fields.Str(required=True)
    additional_info = fields.Str()
    icon = fields.Str()
    created_at = fields.DateTime(dump_only=True)

    @post_load
    def make_article(self, data, **kwargs):
        return Article(**data)

def _col():
    return get_db().articles

def serialize(doc):
    if not doc: return None
    doc["id"] = str(doc.pop("_id"))
    return doc

def create_article(data):
    doc = ArticleSchema().load(data)
    # Convert object to dict for mongo
    doc_dict = vars(doc)
    doc_dict.pop("_id", None)
    result = _col().insert_one(doc_dict)
    doc_dict["_id"] = result.inserted_id
    return serialize(doc_dict)

def list_articles(category=None, search=None):
    query = {}
    if category and category.lower() != "all":
        query["category"] = category
    if search:
        query["title"] = {"$regex": search, "$options": "i"}
    
    cursor = _col().find(query).sort("created_at", -1)
    return [serialize(doc) for doc in cursor]

def find_by_id(article_id):
    try:
        return serialize(_col().find_one({"_id": ObjectId(article_id)}))
    except:
        return None

def update_article(article_id, data):
    try:
        _col().update_one({"_id": ObjectId(article_id)}, {"$set": data})
        return find_by_id(article_id)
    except:
        return None

def delete_article(article_id):
    try:
        _col().delete_one({"_id": ObjectId(article_id)})
        return True
    except:
        return False
