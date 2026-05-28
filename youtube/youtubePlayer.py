import os
import streamlit as st
from googleapiclient.discovery import build

@st.cache_resource
def get_youtube():
    api_key = os.getenv("YOUTUBE_API_KEY")
    return build("youtube", "v3", developerKey=api_key)

def get_mood_video(mood, language):

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

    query = queries.get(language, queries["English"]).get(mood, "music")

    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=1
    )

    response = request.execute()
    items = response.get("items", [])

    if items:
        vid = items[0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={vid}"

    return None
