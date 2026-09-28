import streamlit as st
import tempfile
import os
import json
import hashlib
import time
from datetime import datetime, time as dt_time
from streamlit_cookies_controller import CookieController

from services.gemini_service import analyze_video
from services.thumbnail_service import generate_thumbnail
from services.youtube_service import (
    upload_video,
    set_thumbnail
)
from services.youtube_auth import (
    get_authorization_url,
    exchange_code_for_credentials,
    save_connected_channel
)
from services.mongodb_service import (
    get_youtube_connection
)
from utils.video_utils import (
    detect_aspect_ratio,
    convert_video_format
)


st.set_page_config(
    page_title="YouTube AI Automation",
    page_icon="🎬",
    layout="centered"
)


cookie_controller = CookieController()

OAUTH_STATE_COOKIE = "youtube_oauth_state"


if "video_hash" not in st.session_state:
    st.session_state.video_hash = None

if "ai_thumbnail_path" not in st.session_state:
    st.session_state.ai_thumbnail_path = None

if "ai_thumbnail_generated" not in st.session_state:
    st.session_state.ai_thumbnail_generated = False

if "thumbnail_choice" not in st.session_state:
    st.session_state.thumbnail_choice = None

if "custom_thumbnail_uploaded" not in st.session_state:
    st.session_state.custom_thumbnail_uploaded = False

if "metadata_generated" not in st.session_state:
    st.session_state.metadata_generated = False

if "metadata" not in st.session_state:
    st.session_state.metadata = None

if "oauth_state" not in st.session_state:
    st.session_state.oauth_state = None

if "oauth_processed" not in st.session_state:
    st.session_state.oauth_processed = False


connection_id = cookie_controller.get(
    "youtube_connection_id"
)


query_params = st.query_params

oauth_code = query_params.get("code")
oauth_state = query_params.get("state")
oauth_error = query_params.get("error")


if oauth_error:
    st.error(
        f"YouTube connection failed: {oauth_error}"
    )

    st.query_params.clear()

    st.stop()


if (
    oauth_code
    and not st.session_state.oauth_processed
):
    try:
        saved_state = cookie_controller.get(
            OAUTH_STATE_COOKIE
        )

        if (
            not saved_state
            or oauth_state != saved_state
        ):
            st.error(
                "OAuth security validation failed. "
                "Please start the connection again."
            )

            st.query_params.clear()

            st.stop()

        with st.spinner(
            "Connecting your YouTube channel..."
        ):
            credentials = (
                exchange_code_for_credentials(
                    oauth_code,
                    oauth_state
                )
            )

            connection = save_connected_channel(
                credentials
            )

            cookie_controller.set(
                "youtube_connection_id",
                connection["connection_id"],
                max_age=60 * 60 * 24 * 365
            )

            cookie_controller.remove(
                OAUTH_STATE_COOKIE
            )

            st.session_state.connection_id = (
                connection["connection_id"]
            )

            st.session_state.channel_id = (
                connection["channel_id"]
            )

            st.session_state.channel_name = (
                connection["channel_name"]
            )

            st.session_state.oauth_processed = True

            st.query_params.clear()

            st.success(
                "YouTube channel connected successfully!"
            )

            time.sleep(1)

            st.rerun()

    except Exception as error:
        st.error(
            "Could not connect your YouTube channel."
        )

        st.exception(error)

        st.query_params.clear()

        st.stop()


youtube_connection = None


if connection_id:
    try:
        youtube_connection = (
            get_youtube_connection(
                connection_id
            )
        )

    except Exception as error:
        st.error(
            "Could not check your YouTube connection."
        )

        st.exception(error)

        st.stop()


if not youtube_connection:
    st.title(
        "YouTube AI Automation"
    )

    st.write(
        "Connect your YouTube channel to start "
        "uploading videos."
    )

    st.info(
        "You need to connect a YouTube channel "
        "before using the upload tools."
    )

    if st.button(
        "Connect YouTube Channel",
        width="stretch"
    ):
        try:
            authorization_url, state = (
                get_authorization_url()
            )

            cookie_controller.set(
                OAUTH_STATE_COOKIE,
                state,
                max_age=600
            )

            st.session_state.oauth_state = state

            st.markdown(
                f"[Click here to connect your YouTube channel]({authorization_url})"
            )

            st.info(
                "After approving Google permissions, "
                "you will be returned to this application."
            )

        except Exception as error:
            st.error(
                "Could not start YouTube authorization."
            )

            st.exception(error)

    st.stop()


channel_name = youtube_connection.get(
    "channel_name",
    "Connected Channel"
)

channel_id = youtube_connection.get(
    "channel_id",
    ""
)


st.title(
    "YouTube AI Automation"
)

st.success(
    f"Connected YouTube Channel: **{channel_name}**"
)

st.caption(
    f"Channel ID: {channel_id}"
)

st.write(
    "Automatically analyze your video, generate "
    "YouTube metadata, create an AI or custom "
    "thumbnail, convert video format, and upload "
    "or schedule the video."
)


st.subheader("Video")


uploaded_file = st.file_uploader(
    "Choose your video",
    type=[
        "mp4",
        "mov",
        "avi",
        "mkv"
    ]
)


if uploaded_file is None:
    st.info(
        "Upload a video to continue."
    )

else:
    current_video_hash = hashlib.md5(
        uploaded_file.getvalue()
    ).hexdigest()

    if (
        st.session_state.video_hash
        != current_video_hash
    ):
        st.session_state.video_hash = (
            current_video_hash
        )

        st.session_state.ai_thumbnail_path = None

        st.session_state.ai_thumbnail_generated = (
            False
        )

        st.session_state.thumbnail_choice = None

        st.session_state.custom_thumbnail_uploaded = (
            False
        )

        st.session_state.metadata_generated = False

        st.session_state.metadata = None

        old_thumbnail = (
            "generated_thumbnail.png"
        )

        if os.path.exists(
            old_thumbnail
        ):
            try:
                os.remove(
                    old_thumbnail
                )
            except PermissionError:
                pass


    st.subheader(
        "Video Format"
    )


    video_extension = os.path.splitext(
        uploaded_file.name
    )[1]


    preview_temp = (
        tempfile.NamedTemporaryFile(
            delete=False,
            suffix=video_extension
        )
    )


    preview_temp.write(
        uploaded_file.getbuffer()
    )

    preview_temp.close()


    preview_video_path = (
        preview_temp.name
    )


    try:
        video_info = detect_aspect_ratio(
            preview_video_path
        )

    finally:
        if os.path.exists(
            preview_video_path
        ):
            os.remove(
                preview_video_path
            )


    st.info(
        f"Detected format: "
        f"**{video_info['format']}**"
    )


    st.write(
        f"Resolution: "
        f"{video_info['width']} × "
        f"{video_info['height']}"
    )


    st.write(
        f"Aspect ratio: "
        f"{video_info['ratio']:.3f}"
    )


    format_choice = st.selectbox(
        "Choose video format",
        [
            "Auto Detect",
            "16:9 Landscape",
            "9:16 Vertical"
        ]
    )


    if format_choice == "Auto Detect":
        st.success(
            "Original video format will be used."
        )

    elif format_choice == video_info["format"]:
        st.success(
            f"Video already matches "
            f"{format_choice}."
        )

    else:
        st.info(
            f"Video will be converted to "
            f"{format_choice}."
        )


    st.subheader(
        "AI Thumbnail"
    )


    st.write(
        "Generate an AI thumbnail and review it "
        "before choosing your final thumbnail."
    )


    if not st.session_state.ai_thumbnail_generated:

        if st.button(
            "Generate AI Thumbnail",
            width="stretch"
        ):
            thumbnail_video_temp = (
                tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=video_extension
                )
            )

            thumbnail_video_temp.write(
                uploaded_file.getbuffer()
            )

            thumbnail_video_temp.close()

            thumbnail_video_path = (
                thumbnail_video_temp.name
            )

            try:
                with st.spinner(
                    "Gemini is analyzing the video and "
                    "Cloudflare is generating the thumbnail..."
                ):
                    thumbnail_result = (
                        generate_thumbnail(
                            thumbnail_video_path
                        )
                    )

                st.session_state.ai_thumbnail_path = (
                    thumbnail_result[
                        "thumbnail_path"
                    ]
                )

                st.session_state.ai_thumbnail_generated = (
                    True
                )

                st.session_state.thumbnail_choice = (
                    "Use AI Thumbnail"
                )

                st.success(
                    "AI thumbnail generated successfully!"
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "AI thumbnail generation failed."
                )

                st.exception(error)

                st.info(
                    "You can upload your own thumbnail instead."
                )

                st.session_state.thumbnail_choice = (
                    "Upload Custom Thumbnail"
                )

            finally:
                if os.path.exists(
                    thumbnail_video_path
                ):
                    os.remove(
                        thumbnail_video_path
                    )


    if (
        st.session_state.ai_thumbnail_generated
        and st.session_state.ai_thumbnail_path
        and os.path.exists(
            st.session_state.ai_thumbnail_path
        )
    ):
        st.markdown("---")

        st.subheader(
            "AI Thumbnail Preview"
        )

        st.image(
            st.session_state.ai_thumbnail_path,
            caption="Generated AI Thumbnail",
            width="stretch"
        )

        st.success(
            "Review the AI thumbnail above."
        )

        st.subheader(
            "Choose Thumbnail"
        )

        thumbnail_choice = st.radio(
            "Do you want to use the AI thumbnail "
            "or upload your own?",
            [
                "Use AI Thumbnail",
                "Upload Custom Thumbnail"
            ],
            index=(
                0
                if st.session_state.thumbnail_choice
                != "Upload Custom Thumbnail"
                else 1
            ),
            key="thumbnail_selection"
        )

        st.session_state.thumbnail_choice = (
            thumbnail_choice
        )

        thumbnail_file = None

        if (
            thumbnail_choice
            == "Upload Custom Thumbnail"
        ):
            st.write(
                "Upload your own thumbnail."
            )

            thumbnail_file = st.file_uploader(
                "Choose your custom thumbnail",
                type=[
                    "jpg",
                    "jpeg",
                    "png"
                ],
                key="custom_thumbnail"
            )

            if thumbnail_file:
                st.session_state.custom_thumbnail_uploaded = (
                    True
                )

                st.image(
                    thumbnail_file,
                    caption="Custom Thumbnail Preview",
                    width="stretch"
                )

        else:
            thumbnail_file = None

    else:
        thumbnail_file = None


    if (
        not st.session_state.ai_thumbnail_generated
        and st.session_state.thumbnail_choice
        == "Upload Custom Thumbnail"
    ):
        st.markdown("---")

        st.subheader(
            "Custom Thumbnail"
        )

        thumbnail_file = st.file_uploader(
            "Choose your custom thumbnail",
            type=[
                "jpg",
                "jpeg",
                "png"
            ],
            key="custom_thumbnail_fallback"
        )

        if thumbnail_file:
            st.session_state.custom_thumbnail_uploaded = (
                True
            )

            st.image(
                thumbnail_file,
                caption="Custom Thumbnail Preview",
                width="stretch"
            )


    st.markdown("---")


    st.subheader(
        "YouTube Visibility"
    )


    privacy_status = st.selectbox(
        "Choose visibility",
        [
            "private",
            "unlisted",
            "public"
        ]
    )


    st.subheader(
        "Upload Timing"
    )


    upload_mode = st.radio(
        "When should the video be published?",
        [
            "Upload Now",
            "Schedule"
        ],
        horizontal=True
    )


    schedule_date = None
    schedule_time = None


    if upload_mode == "Schedule":
        schedule_date = st.date_input(
            "Schedule Date"
        )

        schedule_time = st.time_input(
            "Schedule Time",
            value=dt_time(20, 0)
        )

        st.info(
            f"Video will be scheduled for "
            f"{schedule_date} at "
            f"{schedule_time.strftime('%I:%M %p')}"
        )

        st.warning(
            "Scheduled videos are uploaded as private "
            "and published at the scheduled time."
        )


    st.subheader(
        "YouTube Metadata"
    )


    if st.button(
        "Generate Metadata",
        width="stretch"
    ):
        metadata_video_temp = (
            tempfile.NamedTemporaryFile(
                delete=False,
                suffix=video_extension
            )
        )

        metadata_video_temp.write(
            uploaded_file.getbuffer()
        )

        metadata_video_temp.close()

        metadata_video_path = (
            metadata_video_temp.name
        )

        try:
            st.info(
                "Generating YouTube metadata..."
            )

            metadata_text = analyze_video(
                metadata_video_path
            )

            try:
                metadata = json.loads(
                    metadata_text
                )

            except json.JSONDecodeError:
                st.error(
                    "Gemini returned invalid JSON."
                )

                st.code(
                    metadata_text
                )

                st.stop()

            st.session_state.metadata = metadata

            st.session_state.metadata_generated = (
                True
            )

            st.success(
                "Metadata generated!"
            )

        except Exception as error:
            st.error(
                "Metadata generation failed."
            )

            st.exception(error)

        finally:
            if os.path.exists(
                metadata_video_path
            ):
                os.remove(
                    metadata_video_path
                )


    if st.session_state.metadata_generated:

        metadata = (
            st.session_state.metadata
        )

        st.markdown("---")

        st.write(
            "Edit the metadata before uploading."
        )

        edited_title = st.text_input(
            "Title",
            value=metadata["title"]
        )

        edited_description = st.text_area(
            "Description",
            value=metadata["description"],
            height=200
        )

        edited_tags = st.text_input(
            "Tags",
            value=", ".join(
                metadata["tags"]
            )
        )

        st.subheader(
            "Upload"
        )

        if st.button(
            "Process & Upload to YouTube",
            width="stretch"
        ):

            if (
                st.session_state.thumbnail_choice
                is None
            ):
                st.error(
                    "Please choose a thumbnail."
                )

                st.stop()


            if (
                st.session_state.thumbnail_choice
                == "Upload Custom Thumbnail"
                and thumbnail_file is None
            ):
                st.error(
                    "Please upload your custom thumbnail."
                )

                st.stop()


            metadata["title"] = (
                edited_title
            )

            metadata["description"] = (
                edited_description
            )

            metadata["tags"] = [
                tag.strip()
                for tag in edited_tags.split(",")
                if tag.strip()
            ]


            video_temp = (
                tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=video_extension
                )
            )

            video_temp.write(
                uploaded_file.getbuffer()
            )

            video_temp.close()

            video_path = (
                video_temp.name
            )

            converted_video_path = None
            thumbnail_path = None


            try:

                if (
                    format_choice != "Auto Detect"
                    and format_choice
                    != video_info["format"]
                ):

                    st.info(
                        f"Converting video to "
                        f"{format_choice}..."
                    )

                    converted_temp = (
                        tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".mp4"
                        )
                    )

                    converted_temp.close()

                    converted_video_path = (
                        converted_temp.name
                    )

                    convert_video_format(
                        video_path,
                        converted_video_path,
                        format_choice
                    )

                    if os.path.exists(
                        video_path
                    ):
                        os.remove(
                            video_path
                        )

                    video_path = (
                        converted_video_path
                    )

                    converted_video_path = None

                    st.success(
                        "Video conversion completed!"
                    )


                if (
                    st.session_state.thumbnail_choice
                    == "Use AI Thumbnail"
                ):

                    thumbnail_path = (
                        st.session_state.ai_thumbnail_path
                    )

                else:

                    thumbnail_extension = (
                        os.path.splitext(
                            thumbnail_file.name
                        )[1]
                    )

                    thumbnail_temp = (
                        tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=thumbnail_extension
                        )
                    )

                    thumbnail_temp.write(
                        thumbnail_file.getbuffer()
                    )

                    thumbnail_temp.close()

                    thumbnail_path = (
                        thumbnail_temp.name
                    )


                publish_at = None


                if upload_mode == "Schedule":

                    selected_datetime = (
                        datetime.combine(
                            schedule_date,
                            schedule_time
                        )
                    )

                    publish_at = (
                        selected_datetime.isoformat()
                        + "+05:30"
                    )


                st.info(
                    "The YouTube connection is ready. "
                    "The upload service still needs to be "
                    "switched to the connected account."
                )

                st.warning(
                    "Upload is temporarily disabled while "
                    "the multi-user YouTube authentication "
                    "is being connected."
                )

                st.stop()


            except Exception as error:

                st.error(
                    "Something went wrong."
                )

                st.exception(error)


            finally:

                if os.path.exists(
                    video_path
                ):
                    os.remove(
                        video_path
                    )

                if (
                    converted_video_path
                    and os.path.exists(
                        converted_video_path
                    )
                ):
                    os.remove(
                        converted_video_path
                    )

                if (
                    thumbnail_path
                    and st.session_state.thumbnail_choice
                    == "Upload Custom Thumbnail"
                    and os.path.exists(
                        thumbnail_path
                    )
                ):
                    os.remove(
                        thumbnail_path
                    )


st.markdown("---")


st.subheader(
    "Upload History"
)


HISTORY_FILE = "upload_history.json"


def load_upload_history():

    if not os.path.exists(
        HISTORY_FILE
    ):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            history = json.load(
                file
            )

        if isinstance(
            history,
            list
        ):
            return history

        return []

    except Exception:
        return []


def save_upload_history(
    history
):

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
            ensure_ascii=False
        )


upload_history = (
    load_upload_history()
)


if not upload_history:

    st.info(
        "No videos uploaded yet."
    )

else:

    for item in reversed(
        upload_history
    ):

        with st.container(
            border=True
        ):

            st.write(
                f"### "
                f"{item.get('title', 'Untitled')}"
            )

            st.write(
                f"Uploaded: "
                f"{item.get('date', 'Unknown date')}"
            )

            st.write(
                f"Status: "
                f"**{item.get('status', 'Unknown')}**"
            )

            st.write(
                f"Visibility: "
                f"**{item.get('visibility', 'Unknown')}**"
            )

            if item.get(
                "scheduled_for"
            ):

                st.write(
                    f"Scheduled for: "
                    f"**{item.get('scheduled_for')}**"
                )

            st.write(
                f"Video ID: "
                f"`{item.get('video_id', 'Unknown')}`"
            )

            if item.get(
                "url"
            ):

                st.markdown(
                    f"[Open video on YouTube]"
                    f"({item['url']})"
                )