from auth.db import db

def update_user_mood(uid, mood):
    db.collection("users").document(uid).set(
        {"mood": mood},
        merge=True
    )
