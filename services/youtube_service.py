import os
import time
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from services.mongodb_service import get_youtube_connection


SCOPES = [
    "https://www.googleapis.com/auth/youtube"
]


# ============================================================
# YouTube credentials
# ============================================================

def get_credentials(connection_id=None):
    """
    Get YouTube OAuth credentials.

    Multi-user mode:
        If connection_id is provided, load the user's
        encrypted refresh token from MongoDB.

    Legacy mode:
        If connection_id is not provided, fall back to
        YOUTUBE_TOKEN_JSON or local token.json.

    This allows us to test the new multi-user system
    without immediately breaking the existing system.
    """

    credentials = None

    # ========================================================
    # 1. Multi-user MongoDB mode
    # ========================================================

    if connection_id:

        print(
            "Loading YouTube connection from MongoDB..."
        )

        connection = get_youtube_connection(
            connection_id
        )

        if not connection:

            raise RuntimeError(
                "YouTube connection was not found in MongoDB."
            )

        refresh_token = connection.get(
            "refresh_token"
        )

        if not refresh_token:

            raise RuntimeError(
                "YouTube refresh token was not found "
                "for this connection."
            )

        # ----------------------------------------------------
        # Get OAuth client configuration
        # ----------------------------------------------------

        client_config_json = None

        # Try Streamlit Secrets first
        try:

            import streamlit as st

            if "YOUTUBE_CLIENT_CONFIG_JSON" in st.secrets:

                client_config_json = (
                    st.secrets[
                        "YOUTUBE_CLIENT_CONFIG_JSON"
                    ]
                )

        except Exception:

            pass

        # Fall back to environment variable

        if not client_config_json:

            client_config_json = os.getenv(
                "YOUTUBE_CLIENT_CONFIG_JSON"
            )

        if not client_config_json:

            raise RuntimeError(
                "YOUTUBE_CLIENT_CONFIG_JSON is not configured."
            )

        try:

            client_config = json.loads(
                client_config_json
            )

        except Exception as error:

            raise RuntimeError(
                "YOUTUBE_CLIENT_CONFIG_JSON contains "
                "invalid JSON."
            ) from error

        # ----------------------------------------------------
        # Extract OAuth client information
        # ----------------------------------------------------

        if "web" in client_config:

            client_data = client_config["web"]

        elif "installed" in client_config:

            client_data = client_config["installed"]

        else:

            raise RuntimeError(
                "Invalid Google OAuth client configuration."
            )

        client_id = client_data.get(
            "client_id"
        )

        client_secret = client_data.get(
            "client_secret"
        )

        token_uri = client_data.get(
            "token_uri",
            "https://oauth2.googleapis.com/token"
        )

        if not client_id:

            raise RuntimeError(
                "OAuth client_id is missing."
            )

        if not client_secret:

            raise RuntimeError(
                "OAuth client_secret is missing."
            )

        # ----------------------------------------------------
        # Create credentials from refresh token
        # ----------------------------------------------------

        credentials = Credentials(

            token=None,

            refresh_token=refresh_token,

            token_uri=token_uri,

            client_id=client_id,

            client_secret=client_secret,

            scopes=SCOPES
        )

        # ----------------------------------------------------
        # Refresh access token
        # ----------------------------------------------------

        try:

            credentials.refresh(
                Request()
            )

            print(
                "YouTube access token refreshed "
                "from MongoDB connection."
            )

        except Exception as error:

            raise RuntimeError(
                "Could not refresh the YouTube access token. "
                "The stored refresh token may have been "
                "revoked or expired."
            ) from error

        return credentials

    # ========================================================
    # 2. Legacy YOUTUBE_TOKEN_JSON mode
    # ========================================================

    token_json = os.getenv(
        "YOUTUBE_TOKEN_JSON"
    )

    if token_json:

        try:

            token_data = json.loads(
                token_json
            )

            credentials = (
                Credentials.from_authorized_user_info(
                    token_data,
                    SCOPES
                )
            )

            print(
                "YouTube credentials loaded from "
                "YOUTUBE_TOKEN_JSON."
            )

        except Exception as error:

            raise RuntimeError(
                "YOUTUBE_TOKEN_JSON is present but invalid."
            ) from error

    # ========================================================
    # 3. Local token.json
    # ========================================================

    if (
        credentials is None
        and os.path.exists("token.json")
    ):

        print(
            "Loading YouTube credentials from token.json..."
        )

        credentials = (
            Credentials.from_authorized_user_file(
                "token.json",
                SCOPES
            )
        )

    # ========================================================
    # 4. Refresh legacy credentials
    # ========================================================

    if credentials and credentials.expired:

        if credentials.refresh_token:

            print(
                "YouTube access token expired."
            )

            print(
                "Refreshing YouTube access token..."
            )

            try:

                credentials.refresh(
                    Request()
                )

                print(
                    "YouTube access token refreshed."
                )

            except Exception as error:

                raise RuntimeError(
                    "Could not refresh the YouTube OAuth token."
                ) from error

        else:

            credentials = None

    # ========================================================
    # 5. Return valid legacy credentials
    # ========================================================

    if credentials and credentials.valid:

        return credentials

    # ========================================================
    # 6. Local OAuth login
    # ========================================================

    client_config_json = os.getenv(
        "YOUTUBE_CLIENT_CONFIG_JSON"
    )

    local_client_secret = (
        "credentials/client_secret.json"
    )

    if client_config_json:

        print(
            "Using YouTube OAuth client configuration "
            "from YOUTUBE_CLIENT_CONFIG_JSON."
        )

        try:

            client_config = json.loads(
                client_config_json
            )

        except Exception as error:

            raise RuntimeError(
                "YOUTUBE_CLIENT_CONFIG_JSON is invalid JSON."
            ) from error

        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES
        )

    elif os.path.exists(
        local_client_secret
    ):

        print(
            "Using local credentials/client_secret.json..."
        )

        flow = InstalledAppFlow.from_client_secrets_file(
            local_client_secret,
            SCOPES
        )

    else:

        raise RuntimeError(
            "\n\n"
            "YouTube OAuth credentials were not found.\n\n"
            "For local development:\n"
            "  Put your OAuth file at:\n"
            "  credentials/client_secret.json\n\n"
            "For deployment:\n"
            "  Configure YOUTUBE_TOKEN_JSON or "
            "use the multi-user connection flow.\n"
        )

    print(
        "\nOpening Google OAuth authorization..."
    )

    credentials = flow.run_local_server(
        port=0
    )

    # --------------------------------------------------------
    # Save local token
    # --------------------------------------------------------

    try:

        with open(
            "token.json",
            "w"
        ) as token:

            token.write(
                credentials.to_json()
            )

        print(
            "YouTube OAuth token saved to token.json."
        )

    except Exception as error:

        print(
            "Warning: Could not save token.json:",
            error
        )

    return credentials


# ============================================================
# Upload video
# ============================================================

def upload_video(
    video_path,
    metadata,
    privacy_status="private",
    publish_at=None,
    progress_callback=None,
    connection_id=None
):
    """
    Upload a video to YouTube.

    connection_id:
        MongoDB connection ID for the user whose
        YouTube channel should receive the upload.

    privacy_status:
        private
        unlisted
        public

    publish_at:
        ISO 8601 datetime.
        Used for scheduled publishing.

    progress_callback:
        Optional function that receives upload progress
        as a value between 0.0 and 1.0.
    """

    print(
        "Connecting to YouTube..."
    )

    credentials = get_credentials(
        connection_id=connection_id
    )

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    # --------------------------------------------------------
    # Video status
    # --------------------------------------------------------

    status = {
        "privacyStatus": privacy_status
    }

    # --------------------------------------------------------
    # Scheduled video
    # --------------------------------------------------------

    if publish_at:

        status["privacyStatus"] = "private"

        status["publishAt"] = publish_at

    # --------------------------------------------------------
    # Request body
    # --------------------------------------------------------

    request_body = {

        "snippet": {

            "title":
                metadata["title"],

            "description":
                metadata["description"],

            "tags":
                metadata["tags"],

            "categoryId":
                "22"
        },

        "status":
            status
    }

    # --------------------------------------------------------
    # Video media
    # --------------------------------------------------------

    media = MediaFileUpload(

        video_path,

        chunksize=1024 * 1024 * 5,

        resumable=True
    )

    # --------------------------------------------------------
    # Create upload request
    # --------------------------------------------------------

    print(
        "Uploading video to YouTube..."
    )

    request = youtube.videos().insert(

        part="snippet,status",

        body=request_body,

        media_body=media
    )

    # --------------------------------------------------------
    # Upload video
    # --------------------------------------------------------

    response = None

    while response is None:

        try:

            status_progress, response = (
                request.next_chunk()
            )

        except Exception as error:

            print(
                "Upload error:",
                error
            )

            raise

        # ----------------------------------------------------
        # Update progress
        # ----------------------------------------------------

        if status_progress:

            progress = (
                status_progress.progress()
            )

            print(
                f"Upload progress: "
                f"{progress * 100:.1f}%"
            )

            if progress_callback:

                progress_callback(
                    progress
                )

    # --------------------------------------------------------
    # Get video ID
    # --------------------------------------------------------

    video_id = response["id"]

    # --------------------------------------------------------
    # Complete upload
    # --------------------------------------------------------

    if progress_callback:

        progress_callback(
            1.0
        )

    print(
        "\n================================"
    )

    print(
        "UPLOAD SUCCESSFUL!"
    )

    print(
        "YouTube Video ID:",
        video_id
    )

    print(
        "YouTube URL:",
        f"https://www.youtube.com/watch?v={video_id}"
    )

    print(
        "================================"
    )

    return video_id


# ============================================================
# Set custom thumbnail
# ============================================================

def set_thumbnail(
    video_id,
    thumbnail_path,
    connection_id=None
):
    """
    Upload a custom thumbnail to YouTube
    and verify that YouTube registered it.

    connection_id:
        MongoDB connection ID for the user's
        YouTube channel.
    """

    print(
        "\nUploading custom thumbnail..."
    )

    # --------------------------------------------------------
    # Validate thumbnail file
    # --------------------------------------------------------

    if not os.path.exists(
        thumbnail_path
    ):

        raise FileNotFoundError(
            f"Thumbnail file not found: "
            f"{thumbnail_path}"
        )

    # --------------------------------------------------------
    # Get file extension
    # --------------------------------------------------------

    extension = os.path.splitext(
        thumbnail_path
    )[1].lower()

    # --------------------------------------------------------
    # Determine MIME type
    # --------------------------------------------------------

    if extension in [
        ".jpg",
        ".jpeg"
    ]:

        mimetype = "image/jpeg"

    elif extension == ".png":

        mimetype = "image/png"

    else:

        raise ValueError(
            "Thumbnail must be JPG, JPEG, or PNG."
        )

    # --------------------------------------------------------
    # Check file size
    # --------------------------------------------------------

    file_size = os.path.getsize(
        thumbnail_path
    )

    print(
        "Thumbnail file:",
        thumbnail_path
    )

    print(
        "Thumbnail size:",
        file_size,
        "bytes"
    )

    # --------------------------------------------------------
    # Get credentials
    # --------------------------------------------------------

    credentials = get_credentials(
        connection_id=connection_id
    )

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )

    # --------------------------------------------------------
    # Create media
    # --------------------------------------------------------

    media = MediaFileUpload(

        thumbnail_path,

        mimetype=mimetype,

        resumable=True
    )

    # --------------------------------------------------------
    # Upload thumbnail
    # --------------------------------------------------------

    print(
        "Sending thumbnail to YouTube..."
    )

    request = youtube.thumbnails().set(

        videoId=video_id,

        media_body=media
    )

    response = request.execute()

    # --------------------------------------------------------
    # Check response
    # --------------------------------------------------------

    if not response:

        raise RuntimeError(
            "YouTube did not return a thumbnail response."
        )

    print(
        "YouTube accepted the thumbnail upload."
    )

    # --------------------------------------------------------
    # Verify thumbnail
    # --------------------------------------------------------

    print(
        "Verifying custom thumbnail..."
    )

    time.sleep(3)

    video_response = youtube.videos().list(

        part="snippet,contentDetails",

        id=video_id

    ).execute()

    if not video_response.get(
        "items"
    ):

        raise RuntimeError(
            "Could not find the uploaded video "
            "while verifying thumbnail."
        )

    video = video_response["items"][0]

    content_details = video.get(
        "contentDetails",
        {}
    )

    has_custom_thumbnail = content_details.get(
        "hasCustomThumbnail",
        False
    )

    # --------------------------------------------------------
    # Check verification result
    # --------------------------------------------------------

    if has_custom_thumbnail:

        print(
            "\n================================"
        )

        print(
            "CUSTOM THUMBNAIL VERIFIED!"
        )

        print(
            "Video ID:",
            video_id
        )

        print(
            "================================"
        )

        return True

    # --------------------------------------------------------
    # Thumbnail not verified yet
    # --------------------------------------------------------

    print(
        "\n================================"
    )

    print(
        "WARNING:"
    )

    print(
        "YouTube accepted the thumbnail request, "
        "but hasCustomThumbnail is not yet true."
    )

    print(
        "YouTube may still be processing the thumbnail."
    )

    print(
        "================================"
    )

    return False