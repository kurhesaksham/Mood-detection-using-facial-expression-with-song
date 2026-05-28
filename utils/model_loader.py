import os
import streamlit as st

# Reduce TensorFlow logs (faster startup feel)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

@st.cache_resource
def load_emotion_model():
    # 🔥 Lazy import (VERY IMPORTANT)
    from fer import FER
    return FER(mtcnn=False)
