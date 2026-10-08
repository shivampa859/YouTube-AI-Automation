import os
import time
import json

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/youtube"]


def get_credentials():
    """
    Get YouTube OAuth credentials.

    Priority:

    1. YOUTUBE_TOKEN_JSON environment variable
       - Used for Docker / Hugging Face deployment.

    2. Local token.json
       - Used during local development.

    3. Local credentials/client_secret.json
       - Used to perform the initial OAuth login locally.

    The actual OAuth credentials should never be committed
    to GitHub or included directly inside the Docker image.
    """

    credentials = None
    token_json = os.getenv("YOUTUBE_TOKEN_JSON")

    if token_json:

        try:

            token_data = json.loads(token_json)

            credentials = Credentials.from_authorized_user_info(
                token_data,
                SCOPES
            )

            print(
                "YouTube credentials loaded from "
                "YOUTUBE_TOKEN_JSON."
            )

        except Exception as error:

            raise RuntimeError(
                "YOUTUBE_TOKEN_JSON is present but invalid. "
                "Make sure it contains the complete contents "
                "of your token.json file."
            ) from error


    if credentials is None and os.path.exists("token.json"):

        print(
            "Loading YouTube credentials from token.json..."
        )

        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )


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
                    "Could not refresh the YouTube OAuth token. "
                    "The refresh token may have expired or been revoked."
                ) from error

        else:

            credentials = None



    if credentials and credentials.valid:

        return credentials


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

    elif os.path.exists(local_client_secret):

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
            "For Docker / Hugging Face:\n"
            "  Add YOUTUBE_TOKEN_JSON as a secret/environment variable.\n"
            "  It should contain the complete contents of token.json.\n"
        )

    print(
        "\nOpening Google OAuth authorization..."
    )

    credentials = flow.run_local_server(
        port=0
    )
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


def upload_video(
    video_path,
    metadata,
    privacy_status="private",
    publish_at=None,
    progress_callback=None
):
    """
    Upload a video to YouTube.

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

    credentials = get_credentials()

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )



    status = {
        "privacyStatus": privacy_status
    }


    if publish_at:

        status["privacyStatus"] = "private"

        status["publishAt"] = publish_at
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

    media = MediaFileUpload(

        video_path,

        chunksize=1024 * 1024 * 5,

        resumable=True
    )


    print(
        "Uploading video to YouTube..."
    )

    request = youtube.videos().insert(

        part="snippet,status",

        body=request_body,

        media_body=media
    )


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


    video_id = response["id"]


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



def set_thumbnail(
    video_id,
    thumbnail_path
):
    """
    Uploads a custom thumbnail to YouTube
    and verifies that YouTube registered it.
    """

    print(
        "\nUploading custom thumbnail..."
    )

    if not os.path.exists(
        thumbnail_path
    ):

        raise FileNotFoundError(
            f"Thumbnail file not found: "
            f"{thumbnail_path}"
        )


    extension = os.path.splitext(
        thumbnail_path
    )[1].lower()


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


    credentials = get_credentials()

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )


    media = MediaFileUpload(

        thumbnail_path,

        mimetype=mimetype,

        resumable=True
    )


    print(
        "Sending thumbnail to YouTube..."
    )

    request = youtube.thumbnails().set(

        videoId=video_id,

        media_body=media
    )

    response = request.execute()


    if not response:

        raise RuntimeError(
            "YouTube did not return a thumbnail response."
        )

    print(
        "YouTube accepted the thumbnail upload."
    )

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


    print(
        "\n================================"
    )

    print(
        "WARNING:"
    )

    print(
        "YouTube accepted the thumbnail request,"
        " but hasCustomThumbnail is not yet true."
    )

    print(
        "YouTube may still be processing the thumbnail."
    )

    print(
        "================================"
    )

    return False