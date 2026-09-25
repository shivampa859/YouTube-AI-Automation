import os
import time

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/youtube"]


# YouTube credentials

def get_credentials():

    credentials = None

    if os.path.exists("token.json"):

        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not credentials or not credentials.valid:

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):

            credentials.refresh(
                Request()
            )

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials/client_secret.json",
                SCOPES
            )

            credentials = flow.run_local_server(
                port=0
            )

        with open(
            "token.json",
            "w"
        ) as token:

            token.write(
                credentials.to_json()
            )

    return credentials


# Upload video

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


    # Video status

    status = {
        "privacyStatus": privacy_status
    }


    # Scheduled video

    if publish_at:

        status["privacyStatus"] = "private"

        status["publishAt"] = publish_at


    # Request body

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


    # Video media

    media = MediaFileUpload(

        video_path,

        chunksize=1024 * 1024 * 5,

        resumable=True
    )


    # Create upload request

    print(
        "Uploading video to YouTube..."
    )

    request = youtube.videos().insert(

        part="snippet,status",

        body=request_body,

        media_body=media
    )


    # Upload video

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


        # Update progress

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


    # Get video ID

    video_id = response["id"]


    # Complete upload

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


# Set custom thumbnail

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


    # Validate thumbnail file

    if not os.path.exists(
        thumbnail_path
    ):

        raise FileNotFoundError(
            f"Thumbnail file not found: "
            f"{thumbnail_path}"
        )


    # Get file extension

    extension = os.path.splitext(
        thumbnail_path
    )[1].lower()


    # Determine MIME type

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


    # Check file size

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


    # Get credentials

    credentials = get_credentials()

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials
    )


    # Create media

    media = MediaFileUpload(

        thumbnail_path,

        mimetype=mimetype,

        resumable=True
    )


    # Upload thumbnail

    print(
        "Sending thumbnail to YouTube..."
    )

    request = youtube.thumbnails().set(

        videoId=video_id,

        media_body=media
    )

    response = request.execute()


    # Check response

    if not response:

        raise RuntimeError(
            "YouTube did not return a thumbnail response."
        )


    print(
        "YouTube accepted the thumbnail upload."
    )


    # Verify thumbnail

    print(
        "Verifying custom thumbnail..."
    )

    time.sleep(3)


    video_response = youtube.videos().list(

        part="snippet,status",

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

    status = video.get(
        "status",
        {}
    )

    has_custom_thumbnail = status.get(
        "hasCustomThumbnail",
        False
    )


    # Check verification result

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


    # Thumbnail not verified

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