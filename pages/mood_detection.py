import streamlit as st
import cv2
import numpy as np
from PIL import Image
from collections import Counter

from utils.model_loader import load_emotion_model
from auth.backend import update_user_mood
from youtube.youtubePlayer import get_mood_video


st.set_page_config(
    page_title="Mood Detection",
    page_icon="🎭"
)


# ---------------- LOGIN CHECK ----------------
if "uid" not in st.session_state or not st.session_state.uid:
    st.error("Please login first.")
    st.stop()

uid = st.session_state.uid


# ---------------- LOAD MODEL ----------------
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
    "final_mood": None,
    "detecting": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- LOGOUT ----------------
if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("app.py")


# =========================================================
# LANGUAGE SELECTION
# =========================================================

if not st.session_state.language_selected:

    st.title("🎭 Mood Detection")

    st.subheader("Select Preferred Language")

    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Marathi"]
    )

    if st.button("Continue"):

        st.session_state.preferred_language = language
        st.session_state.language_selected = True
        st.session_state.detecting = True

        st.rerun()


# =========================================================
# CAMERA / MOOD DETECTION
# =========================================================

elif st.session_state.detecting:

    st.title("🎭 Mood Detection")

    st.write(
        "Allow camera access and take a photo so we can detect your mood."
    )

    camera_image = st.camera_input(
        "Take a picture"
    )

    if camera_image is not None:

        with st.spinner("Detecting your mood..."):

            # Read uploaded camera image
            image = Image.open(camera_image)

            # Convert PIL image to NumPy
            frame = np.array(image)

            # Convert RGB → BGR for OpenCV / FER
            frame_bgr = cv2.cvtColor(
                frame,
                cv2.COLOR_RGB2BGR
            )

            # Resize for faster detection
            small = cv2.resize(
                frame_bgr,
                (320, 240)
            )

            # Detect emotions
            emotions = emotion_detector.detect_emotions(
                small
            )

            detected_emotions = []

            # Scale coordinates back to original image
            scale_x = frame_bgr.shape[1] / 320
            scale_y = frame_bgr.shape[0] / 240

            for face in emotions:

                mood = max(
                    face["emotions"],
                    key=face["emotions"].get
                )

                confidence = face["emotions"][mood]

                if confidence > 0.3:

                    detected_emotions.append(mood)

                    x, y, w, h = face["box"]

                    x = int(x * scale_x)
                    y = int(y * scale_y)
                    w = int(w * scale_x)
                    h = int(h * scale_y)

                    cv2.rectangle(
                        frame_bgr,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame_bgr,
                        f"{mood} ({confidence:.2f})",
                        (x, max(y - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

            # ---------------- FINAL MOOD ----------------

            if detected_emotions:

                final_mood = Counter(
                    detected_emotions
                ).most_common(1)[0][0]

                st.session_state.final_mood = final_mood

                update_user_mood(
                    uid,
                    final_mood
                )

                st.session_state.detecting = False

                st.success(
                    f"Detected Mood: {final_mood.upper()}"
                )

                # Show detected image
                result_image = cv2.cvtColor(
                    frame_bgr,
                    cv2.COLOR_BGR2RGB
                )

                st.image(
                    result_image,
                    caption="Detected Emotion",
                    use_container_width=True
                )

                st.rerun()

            else:

                st.warning(
                    "No face or stable emotion was detected. "
                    "Please try again with your face clearly visible."
                )


# =========================================================
# RESULT PAGE
# =========================================================

else:

    st.title("🎵 Detection Result")

    mood = st.session_state.final_mood
    language = st.session_state.preferred_language

    if mood:

        st.success(
            f"Detected Mood: {mood.upper()}"
        )

        st.write(
            f"Preferred Language: {language}"
        )

        with st.spinner("Fetching music..."):

            video_url = get_mood_video(
                mood,
                language
            )

        if video_url:

            st.subheader("🎵 Recommended Song")

            st.video(video_url)

        else:

            st.error(
                "No video found for this mood."
            )

    else:

        st.warning(
            "No stable emotion detected."
        )

    if st.button("🔄 Detect Again"):

        st.session_state.detecting = True
        st.session_state.final_mood = None

        st.rerun()
