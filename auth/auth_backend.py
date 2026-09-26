import requests
import streamlit as st
from firebase_admin import auth
from auth.db import db


API_KEY = st.secrets["FIREBASE_API_KEY"]

def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email})
        return {"success": True, "uid": user.uid}
    except Exception as e:
        return {"success": False, "message": str(e)}

def login_user(email, password):
    try:
        url = (
            "https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithPassword?key={API_KEY}"
        )

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if "localId" in data:
            return {
                "success": True,
                "uid": data["localId"]
            }

        error = data.get("error", {})
        message = error.get("message", "Unknown Firebase error")

        return {
            "success": False,
            "message": message
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

def reset_password(email):
    try:
        link = auth.generate_password_reset_link(email)
        return {
            "success": True,
            "link": link
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
