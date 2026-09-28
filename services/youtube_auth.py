import os
import json
import uuid

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from services.mongodb_service import save_youtube_connection


SCOPES = [
    "https://www.googleapis.com/auth/youtube"
]

REDIRECT_URI = (
    "https://shivampa859-youtube-ai-automation-"
    "app-xddrga.streamlit.app/"
)


def get_client_config():
    """
    Load Google OAuth configuration.

    Streamlit Cloud:
        Read from Streamlit Secrets.

    Local development:
        Read from environment variable.
    """

    config_json = None

    # Try Streamlit Secrets first
    try:
        import streamlit as st

        if "YOUTUBE_CLIENT_CONFIG_JSON" in st.secrets:
            config_json = st.secrets[
                "YOUTUBE_CLIENT_CONFIG_JSON"
            ]

    except Exception:
        pass

    # Fall back to environment variable
    if not config_json:
        config_json = os.getenv(
            "YOUTUBE_CLIENT_CONFIG_JSON"
        )

    if not config_json:
        raise RuntimeError(
            "YOUTUBE_CLIENT_CONFIG_JSON is not configured."
        )

    return json.loads(config_json)


def create_oauth_flow():
    """
    Create the Google OAuth flow for connecting
    a user's YouTube channel.
    """

    client_config = get_client_config()

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    return flow


def get_authorization_url():
    """
    Generate the Google authorization URL.
    """

    flow = create_oauth_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    return authorization_url, state


def exchange_code_for_credentials(code, state=None):
    """
    Exchange Google's authorization code for
    the user's YouTube credentials.
    """

    flow = create_oauth_flow()

    flow.fetch_token(code=code)

    return flow.credentials


def get_connected_channel(credentials):
    """
    Get the YouTube channel connected through OAuth.
    """

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    response = youtube.channels().list(
        part="id,snippet",
        mine=True
    ).execute()

    channels = response.get("items", [])

    if not channels:
        raise RuntimeError(
            "No YouTube channel was found for this Google account."
        )

    channel = channels[0]

    return {
        "channel_id": channel["id"],
        "channel_name": channel["snippet"]["title"]
    }


def save_connected_channel(credentials):
    """
    Save the connected YouTube channel in MongoDB.

    The refresh token is encrypted by
    mongodb_service.py before storage.
    """

    if not credentials.refresh_token:
        raise RuntimeError(
            "Google did not provide a refresh token."
        )

    channel = get_connected_channel(credentials)

    connection_id = str(uuid.uuid4())

    save_youtube_connection(
        connection_id=connection_id,
        channel_id=channel["channel_id"],
        channel_name=channel["channel_name"],
        refresh_token=credentials.refresh_token
    )

    return {
        "connection_id": connection_id,
        "channel_id": channel["channel_id"],
        "channel_name": channel["channel_name"]
    }