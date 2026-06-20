"""
Seeder script to update database with new scientific names, 
prevention tips, and Knowledge Base articles.
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone

load_dotenv()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.get_database("plant_disease_db")

def seed_scientific_names_and_prevention():
    print("Updating 38 diseases with metadata...")
    diseases = list(db.diseases.find())
    
    # Sample scientific names mapping (first few as example)
    scientific_names = {
        "Apple___Apple_scab": "Venturia inaequalis",
        "Apple___Black_rot": "Botryosphaeria obtusa",
        "Apple___Cedar_apple_rust": "Gymnosporangium juniperi-virginianae",
        "Tomato___Late_blight": "Phytophthora infestans",
        "Tomato___Early_blight": "Alternaria solani",
        "Potato___Early_blight": "Alternaria solani",
        "Grape___Black_rot": "Guignardia bidwellii"
    }

    for d in diseases:
        name = d.get("name", "")
        update_data = {
            "scientific_name": scientific_names.get(name, "Species unknown"),
            "prevention": [
                "Ensure proper spacing for air circulation.",
                "Remove and destroy infected plant debris.",
                "Avoid overhead watering to keep leaves dry."
            ]
        }
        db.diseases.update_one({"_id": d["_id"]}, {"$set": update_data})
    
    print(f"Updated {len(diseases)} diseases.")

def seed_articles():
    print("Seeding Knowledge Base articles...")
    articles = [
        {
            "title": "How to Identify Common Plant Diseases",
            "category": "Guide",
            "content": "Learn the key signs and symptoms of common diseases like blights and rots. Early identification is crucial for effective treatment.",
            "additional_info": "LeafGuard AI uses advanced machine learning to provide accurate plant disease detection.",
            "icon": "search",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "Best Practices for Healthy Plants",
            "category": "Tips",
            "content": "Discover the fundamental practices like proper watering and soil management to keep your plants thriving.",
            "additional_info": "Our database is regularly updated with the latest research from agricultural institutions.",
            "icon": "leaf",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "Natural Ways to Protect Plants",
            "category": "Organic",
            "content": "Explore organic and natural methods to protect your plants from diseases and pests without harsh chemicals.",
            "additional_info": "Follow organic standards for better soil health and long-term sustainability.",
            "icon": "shield",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "Understanding Soil Health",
            "category": "Science",
            "content": "Healthy soil is the foundation of healthy plants. Learn about composition, pH, and improvement methods.",
            "additional_info": "Soil testing is the first step towards a productive garden.",
            "icon": "earth",
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Clear old articles to avoid duplicates
    db.articles.delete_many({})
    db.articles.insert_many(articles)
    print("Inserted 4 Knowledge Base articles.")

if __name__ == "__main__":
    seed_scientific_names_and_prevention()
    seed_articles()
    print("\n✅ Database update complete!")
