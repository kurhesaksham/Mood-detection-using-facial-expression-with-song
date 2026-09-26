import os
import random
import streamlit as st
from googleapiclient.discovery import build


# =========================================================
# YOUTUBE CLIENT
# =========================================================

@st.cache_resource
def get_youtube():
    api_key = st.secrets["YOUTUBE_API_KEY"]

    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is missing.")

    return build(
        "youtube",
        "v3",
        developerKey=api_key
    )


# =========================================================
# MOOD SEARCH QUERIES
# =========================================================

QUERIES = {

    "English": {
        "happy": [
            "happy english songs",
            "feel good english songs",
            "happy english music",
            "uplifting english songs"
        ],

        "sad": [
            "sad english songs",
            "emotional english songs",
            "heartbreak english songs",
            "melancholy english songs"
        ],

        "angry": [
            "calm english songs",
            "relaxing english music",
            "stress relief english songs",
            "peaceful english songs"
        ],

        "fear": [
            "relaxing english songs",
            "calm english music",
            "peaceful english songs",
            "stress relief music english"
        ],

        "surprise": [
            "uplifting english songs",
            "energetic english songs",
            "exciting english songs",
            "feel good english music"
        ],

        "neutral": [
            "lofi english songs",
            "chill english songs",
            "relaxing english music",
            "calm english songs"
        ]
    },

    "Hindi": {
        "happy": [
            "happy hindi songs",
            "feel good hindi songs",
            "energetic hindi songs",
            "uplifting hindi songs"
        ],

        "sad": [
            "sad hindi songs",
            "emotional hindi songs",
            "heartbreak hindi songs",
            "sad bollywood songs"
        ],

        "angry": [
            "calm hindi songs",
            "relaxing hindi songs",
            "peaceful hindi music",
            "stress relief hindi songs"
        ],

        "fear": [
            "relaxing hindi songs",
            "calm hindi music",
            "peaceful hindi songs",
            "soothing hindi songs"
        ],

        "surprise": [
            "uplifting hindi songs",
            "energetic hindi songs",
            "exciting hindi songs",
            "feel good hindi songs"
        ],

        "neutral": [
            "lofi hindi songs",
            "chill hindi songs",
            "relaxing hindi music",
            "calm hindi songs"
        ]
    },

    "Marathi": {
        "happy": [
            "happy marathi songs",
            "feel good marathi songs",
            "energetic marathi songs",
            "uplifting marathi songs"
        ],

        "sad": [
            "sad marathi songs",
            "emotional marathi songs",
            "heartbreak marathi songs",
            "sad marathi music"
        ],

        "angry": [
            "calm marathi songs",
            "relaxing marathi songs",
            "peaceful marathi music",
            "stress relief marathi songs"
        ],

        "fear": [
            "relaxing marathi songs",
            "calm marathi music",
            "peaceful marathi songs",
            "soothing marathi songs"
        ],

        "surprise": [
            "uplifting marathi songs",
            "energetic marathi songs",
            "exciting marathi songs",
            "feel good marathi songs"
        ],

        "neutral": [
            "lofi marathi songs",
            "chill marathi songs",
            "relaxing marathi music",
            "calm marathi songs"
        ]
    }
}


# =========================================================
# GET MOOD VIDEO
# =========================================================

def get_mood_video(mood, language):

    youtube = get_youtube()

    # Create session state for played videos
    if "played_videos" not in st.session_state:
        st.session_state.played_videos = {}

    # Create key for mood + language
    history_key = f"{language}_{mood}"

    if history_key not in st.session_state.played_videos:
        st.session_state.played_videos[history_key] = []

    played_videos = st.session_state.played_videos[history_key]

    # Get available queries
    language_queries = QUERIES.get(
        language,
        QUERIES["English"]
    )

    mood_queries = language_queries.get(
        mood,
        language_queries["neutral"]
    )

    # Randomly select a search query
    query = random.choice(mood_queries)

    try:

        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=10
        )

        response = request.execute()

        items = response.get("items", [])

        if not items:
            return None

        # Get video IDs
        videos = []

        for item in items:

            video_id = item.get("id", {}).get("videoId")

            if video_id:
                videos.append(video_id)

        if not videos:
            return None

        # Remove videos that were already played
        available_videos = [
            video_id
            for video_id in videos
            if video_id not in played_videos
        ]

        # If all videos were already played,
        # clear history and start again
        if not available_videos:

            played_videos.clear()

            available_videos = videos

        # Pick a random video
        selected_video = random.choice(
            available_videos
        )

        # Save it to history
        played_videos.append(
            selected_video
        )

        # Keep only last 20 videos
        if len(played_videos) > 20:
            played_videos.pop(0)

        return (
            f"https://www.youtube.com/watch?v={selected_video}"
        )

    except Exception as e:

        st.error(
            f"YouTube error: {str(e)}"
        )

        return None
