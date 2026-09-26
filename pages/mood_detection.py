import streamlit as st
import cv2
import numpy as np
from PIL import Image
from collections import Counter

from utils.model_loader import load_emotion_model
from auth.backend import update_user_mood
from youtube.youtubePlayer import get_mood_video


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Mood Detection",
    page_icon="🎭",
    layout="centered"
)


# =========================================================
# LOGIN CHECK
# =========================================================

if "uid" not in st.session_state or not st.session_state.uid:
    st.error("Please login first.")
    st.stop()

uid = st.session_state.uid


# =========================================================
# LOAD EMOTION MODEL
# =========================================================

@st.cache_resource
def get_model():
    return load_emotion_model()


try:
    emotion_detector = get_model()

except Exception as e:
    st.error("Emotion model failed to load.")
    st.error(str(e))
    st.stop()


if emotion_detector is None:
    st.error("Emotion model failed to load.")
    st.stop()


# =========================================================
# SESSION STATES
# =========================================================

defaults = {
    "language_selected": False,
    "preferred_language": None,
    "final_mood": None,
    "detecting": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOGOUT
# =========================================================

if st.button("🚪 Logout"):

    st.session_state.clear()

    st.switch_page("app.py")


# =========================================================
# LANGUAGE SELECTION
# =========================================================

if not st.session_state.language_selected:

    st.title("🎭 Mood Detection")

    st.subheader("Select Preferred Language")

    language = st.selectbox(
        "Preferred Music Language",
        [
            "English",
            "Hindi",
            "Marathi"
        ]
    )

    st.write("")

    if st.button(
        "Continue",
        use_container_width=True
    ):

        st.session_state.preferred_language = language
        st.session_state.language_selected = True
        st.session_state.detecting = True
        st.session_state.final_mood = None

        st.rerun()


# =========================================================
# MOOD DETECTION
# =========================================================

elif st.session_state.detecting:

    st.title("🎭 Detect Your Mood")

    st.write(
        "Take a clear photo of your face. "
        "The system will analyze your facial expression "
        "and detect your mood."
    )

    st.info(
        f"🎵 Music language: "
        f"**{st.session_state.preferred_language}**"
    )

    st.write("")

    # -----------------------------------------------------
    # CAMERA INPUT
    # -----------------------------------------------------

    camera_image = st.camera_input(
        "📷 Take a picture"
    )

    if camera_image is not None:

        with st.spinner(
            "🔍 Detecting your mood..."
        ):

            try:

                # -------------------------------------------------
                # READ IMAGE
                # -------------------------------------------------

                image = Image.open(
                    camera_image
                ).convert("RGB")

                frame = np.array(image)

                # -------------------------------------------------
                # RGB → BGR
                # -------------------------------------------------

                frame_bgr = cv2.cvtColor(
                    frame,
                    cv2.COLOR_RGB2BGR
                )

                # -------------------------------------------------
                # RESIZE IMAGE
                # -------------------------------------------------

                original_height, original_width = (
                    frame_bgr.shape[:2]
                )

                detection_width = 320
                detection_height = 240

                small = cv2.resize(
                    frame_bgr,
                    (
                        detection_width,
                        detection_height
                    )
                )

                # -------------------------------------------------
                # DETECT EMOTIONS
                # -------------------------------------------------

                emotions = (
                    emotion_detector.detect_emotions(
                        small
                    )
                )

                detected_emotions = []

                # -------------------------------------------------
                # SCALE FACTORS
                # -------------------------------------------------

                scale_x = (
                    original_width /
                    detection_width
                )

                scale_y = (
                    original_height /
                    detection_height
                )

                # -------------------------------------------------
                # PROCESS DETECTED FACES
                # -------------------------------------------------

                for face in emotions:

                    emotion_scores = face.get(
                        "emotions",
                        {}
                    )

                    if not emotion_scores:
                        continue

                    mood = max(
                        emotion_scores,
                        key=emotion_scores.get
                    )

                    confidence = emotion_scores[mood]

                    # ---------------------------------------------
                    # CONFIDENCE THRESHOLD
                    # ---------------------------------------------

                    if confidence < 0.30:
                        continue

                    detected_emotions.append(
                        mood
                    )

                    # ---------------------------------------------
                    # FACE COORDINATES
                    # ---------------------------------------------

                    x, y, w, h = face["box"]

                    x = int(x * scale_x)
                    y = int(y * scale_y)
                    w = int(w * scale_x)
                    h = int(h * scale_y)

                    # Prevent coordinates from going outside image
                    x = max(0, x)
                    y = max(0, y)

                    w = min(
                        w,
                        original_width - x
                    )

                    h = min(
                        h,
                        original_height - y
                    )

                    # ---------------------------------------------
                    # DRAW FACE BOX
                    # ---------------------------------------------

                    cv2.rectangle(
                        frame_bgr,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        3
                    )

                    # ---------------------------------------------
                    # EMOTION LABEL
                    # ---------------------------------------------

                    label = (
                        f"{mood.upper()} "
                        f"({confidence:.0%})"
                    )

                    text_y = max(
                        y - 10,
                        25
                    )

                    cv2.putText(
                        frame_bgr,
                        label,
                        (x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2,
                        cv2.LINE_AA
                    )

                # =================================================
                # FINAL MOOD
                # =================================================

                if detected_emotions:

                    # Find most frequently detected emotion
                    final_mood = Counter(
                        detected_emotions
                    ).most_common(1)[0][0]

                    # ---------------------------------------------
                    # SAVE MOOD
                    # ---------------------------------------------

                    st.session_state.final_mood = (
                        final_mood
                    )

                    # ---------------------------------------------
                    # UPDATE FIREBASE
                    # ---------------------------------------------

                    try:

                        update_user_mood(
                            uid,
                            final_mood
                        )

                    except Exception as firebase_error:

                        st.warning(
                            "Mood detected, but the mood "
                            "could not be saved to the database."
                        )

                        st.caption(
                            str(firebase_error)
                        )

                    # ---------------------------------------------
                    # STOP DETECTION
                    # ---------------------------------------------

                    st.session_state.detecting = False

                    # ---------------------------------------------
                    # SHOW RESULT IMAGE
                    # ---------------------------------------------

                    result_image = cv2.cvtColor(
                        frame_bgr,
                        cv2.COLOR_BGR2RGB
                    )

                    st.success(
                        f"🎭 Detected Mood: "
                        f"**{final_mood.upper()}**"
                    )

                    st.image(
                        result_image,
                        caption="Detected Emotion",
                        use_container_width=True
                    )

                    # ---------------------------------------------
                    # REFRESH PAGE
                    # ---------------------------------------------

                    st.rerun()

                else:

                    st.warning(
                        "😕 No stable emotion was detected."
                    )

                    st.info(
                        "Please make sure your face is clearly "
                        "visible, well lit, and looking toward "
                        "the camera."
                    )

            except Exception as e:

                st.error(
                    "An error occurred while detecting "
                    "your mood."
                )

                st.exception(e)


# =========================================================
# RESULT PAGE
# =========================================================

else:

    st.title("🎵 Mood Detection Result")

    mood = st.session_state.final_mood

    language = (
        st.session_state.preferred_language
    )

    # =====================================================
    # MOOD RESULT
    # =====================================================

    if mood:

        st.success(
            f"🎭 Detected Mood: "
            f"**{mood.upper()}**"
        )

        st.info(
            f"🌐 Music Language: "
            f"**{language}**"
        )

        st.write("")

        # =================================================
        # FETCH SONG
        # =================================================

        with st.spinner(
            "🎵 Finding a song for your mood..."
        ):

            try:

                video_url = get_mood_video(
                    mood,
                    language
                )

            except Exception as e:

                video_url = None

                st.error(
                    "Unable to fetch a song from YouTube."
                )

                st.exception(e)

        # =================================================
        # SHOW SONG
        # =================================================

        if video_url:

            st.subheader(
                "🎵 Recommended Song"
            )

            st.video(
                video_url
            )

        else:

            st.warning(
                "No suitable song was found."
            )

    else:

        st.warning(
            "😕 No stable emotion detected."
        )


    # =====================================================
    # DETECT AGAIN
    # =====================================================

    st.write("")

    if st.button(
        "🔄 Detect Again",
        use_container_width=True
    ):

        # Clear previous result
        st.session_state.final_mood = None

        # Start camera again
        st.session_state.detecting = True

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.write("")

st.caption(
    "🎭 Mood Detection Using Facial Expression With Songs"
)
