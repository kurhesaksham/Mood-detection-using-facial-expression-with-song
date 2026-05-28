import streamlit as st
from auth.auth_backend import login_user, register_user
from utils.model_loader import load_emotion_model

st.set_page_config(
    page_title="Mood Detection",
    page_icon="🎭"
)

st.title("🎭Mood Detection Using Facial Expressions with Song")

if "uid" not in st.session_state:
    st.session_state.uid = None

tab1, tab2 = st.tabs(["Login", "Sign Up"])

# ---------------- LOGIN ----------------
with tab1:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        with st.spinner("Preparing your experience..."):
            result = login_user(email, password)

            if result.get("success"):
                # 🔥 Preload model during login
                load_emotion_model()

                st.session_state.uid = result["uid"]
                st.switch_page("pages/mood_detection.py")
            else:
                st.error(result.get("message", "Login failed"))

# ---------------- SIGNUP ----------------
with tab2:
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pass")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm:
            st.error("Passwords do not match")
        else:
            result = register_user(email, password)

            if result.get("success"):
                st.success("Account created successfully. Please login.")
            else:
                st.error(result.get("message", "Registration failed"))
