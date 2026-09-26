
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


@st.cache_resource
def get_youtube():
    """
    Create YouTube API client using only the API key.
    No Firebase/Google OAuth credentials are used here.
    """

    # Read API key from Streamlit secrets
    try:
        api_key = st.secrets["YOUTUBE_API_KEY"]
    except KeyError:
        st.error("YOUTUBE_API_KEY is missing from Streamlit Secrets.")
        return None

    if not api_key:
        st.error("YOUTUBE_API_KEY is empty.")
        return None

    return build(
        "youtube",
        "v3",
        developerKey=api_key,
        cache_discovery=False
    )


def get_mood_video(mood, language):

    youtube = get_youtube()

    if youtube is None:
        return None

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

    language_queries = queries.get(
        language,
        queries["English"]
    )

    query = language_queries.get(
        mood.lower(),
        "music"
    )

    try:
        response = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1
        ).execute()

        items = response.get("items", [])

        if not items:
            return None

        video_id = items[0]["id"].get("videoId")

        if not video_id:
            return None

        return f"https://www.youtube.com/watch?v={video_id}"

    except HttpError as e:
        st.error(f"YouTube API error: {e}")
        return None

    except Exception as e:
        st.error(f"Unable to fetch YouTube video: {e}")
        return None
