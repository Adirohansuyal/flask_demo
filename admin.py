from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb+srv://flask0001:flask0001@cluster0.qwc770i.mongodb.net/flask_auth_db?retryWrites=true&w=majority&appName=Cluster0")
db = client['flask_auth_db']
admins = db.admins

admin_user = {
    "username": "admin",
    "password": generate_password_hash("admin123")
}

admins.insert_one(admin_user)
print("✅ Admin user created.")
