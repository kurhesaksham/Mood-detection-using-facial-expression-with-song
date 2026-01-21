import os
import requests
from firebase_admin import auth
from auth.db import db

API_KEY = os.getenv("FIREBASE_API_KEY")

def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email})
        return {"success": True, "uid": user.uid}
    except Exception as e:
        return {"success": False, "message": str(e)}

def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload).json()

    if "localId" in res:
        return {"success": True, "uid": res["localId"]}
    return {"success": False, "message": "Login failed"}
