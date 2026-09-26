import random
import streamlit as st
from googleapiclient.discovery import build


@st.cache_resource
def get_youtube():
    api_key = st.secrets["YOUTUBE_API_KEY"]

    return build(
        "youtube",
        "v3",
        developerKey=api_key,
        cache_discovery=False
    )


def get_mood_video(mood, language, previous_video_id=None):

    youtube = get_youtube()

    queries = {
        "English": {
            "happy": "happy english songs",
            "sad": "sad english songs",
            "angry": "calm english songs",
            "fear": "relaxing english songs",
            "surprise": "uplifting english songs",
            "neutral": "lofi english songs"
        },

        "Hindi": {
            "happy": "happy hindi songs",
            "sad": "sad hindi songs",
            "angry": "calm hindi songs",
            "fear": "relaxing hindi songs",
            "surprise": "uplifting hindi songs",
            "neutral": "lofi hindi songs"
        },

        "Marathi": {
            "happy": "happy marathi songs",
            "sad": "sad marathi songs",
            "angry": "calm marathi songs",
            "fear": "relaxing marathi songs",
            "surprise": "uplifting marathi songs",
            "neutral": "lofi marathi songs"
        }
    }

    query = queries.get(
        language,
        queries["English"]
    ).get(
        mood.lower(),
        "music"
    )

    try:

        response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=10
        ).execute()

        items = response.get("items", [])

        videos = []

        for item in items:

            video_id = item.get("id", {}).get("videoId")

            if video_id:

                # Don't use the previous song
                if video_id != previous_video_id:
                    videos.append(video_id)

        if not videos:
            return None

        # Pick a different video
        selected_video = random.choice(videos)

        return f"https://www.youtube.com/watch?v={selected_video}"

    except Exception as e:

        st.error(f"YouTube API error: {e}")

        return None
