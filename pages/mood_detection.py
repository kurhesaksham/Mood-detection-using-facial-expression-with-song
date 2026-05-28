import streamlit as st
import cv2
import time
from collections import Counter
from utils.model_loader import load_emotion_model
from auth.backend import update_user_mood
from youtube.youtubePlayer import get_mood_video

st.set_page_config(page_title="Mood Detection", page_icon="🎭")

# ---------------- LOGIN CHECK ----------------
if "uid" not in st.session_state or not st.session_state.uid:
    st.error("Please login first.")
    st.stop()

uid = st.session_state.uid

# ---------------- LOAD MODEL (CACHED) ----------------
@st.cache_resource
def get_model():
    return load_emotion_model()

emotion_detector = get_model()

if emotion_detector is None:
    st.error("Emotion model failed to load.")
    st.stop()

# ---------------- SESSION STATES ----------------
defaults = {
    "language_selected": False,
    "preferred_language": None,
    "detecting": False,
    "final_mood": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- LOGOUT ----------------
if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

# ---------------- LANGUAGE SELECTION ----------------
if not st.session_state.language_selected:

    st.title("Select Preferred Language")

    language = st.selectbox("Language", ["English", "Hindi", "Marathi"])

    if st.button("Continue"):
        st.session_state.preferred_language = language
        st.session_state.language_selected = True
        st.session_state.detecting = True
        st.rerun()

# ---------------- MOOD DETECTION ----------------
elif st.session_state.detecting:

    st.title("Detecting Mood...")

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        st.error("Camera not accessible.")
        st.stop()

    detected_emotions = []
    frame_placeholder = st.empty()

    DETECTION_TIME = 8
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 🔥 Use better resolution (important fix)
            small = cv2.resize(frame, (320, 240))
            scale_x = frame.shape[1] / 320
            scale_y = frame.shape[0] / 240

            emotions = emotion_detector.detect_emotions(small)

            for face in emotions:
                mood = max(face["emotions"], key=face["emotions"].get)
                confidence = face["emotions"][mood]

                # 🔥 Lower confidence threshold (important fix)
                if confidence > 0.3:
                    detected_emotions.append(mood)

                    x, y, w, h = face["box"]

                    x = int(x * scale_x)
                    y = int(y * scale_y)
                    w = int(w * scale_x)
                    h = int(h * scale_y)

                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"{mood} ({confidence:.2f})",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2,
                    )

            frame_placeholder.image(
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )

            if time.time() - start_time > DETECTION_TIME:
                break

    finally:
        cap.release()

    # ---------------- FINAL MOOD ----------------
    if detected_emotions:
        final_mood = Counter(detected_emotions).most_common(1)[0][0]
        st.session_state.final_mood = final_mood
        update_user_mood(uid, final_mood)
    else:
        st.session_state.final_mood = None

    st.session_state.detecting = False
    st.rerun()

# ---------------- RESULT PAGE ----------------
else:

    st.title("Detection Result")

    mood = st.session_state.final_mood
    language = st.session_state.preferred_language

    if mood:
        st.success(f"Detected Mood: {mood.upper()}")
        st.write(f"Preferred Language: {language}")

        with st.spinner("Fetching music..."):
            video_url = get_mood_video(mood, language)

        if video_url:
            st.video(video_url)
        else:
            st.error("No video found for this mood.")

    else:
        st.warning("No stable emotion detected.")

    if st.button("Detect Again"):
        st.session_state.detecting = True
        st.session_state.final_mood = None
        st.rerun()