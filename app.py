import streamlit as st
import tempfile
import os
import json
import hashlib
from datetime import datetime, time

from services.gemini_service import analyze_video
from services.thumbnail_service import generate_thumbnail
from services.youtube_service import (
    upload_video,
    set_thumbnail
)

from utils.video_utils import (
    detect_aspect_ratio,
    convert_video_format
)


# Page configuration

st.set_page_config(
    page_title="YouTube AI Automation",
    page_icon="🎬",
    layout="centered"
)


# History functions

HISTORY_FILE = "upload_history.json"


def load_upload_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            history = json.load(file)

        if isinstance(history, list):
            return history

        return []

    except Exception:

        return []


def save_upload_history(history):

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


# Session state

if "video_hash" not in st.session_state:
    st.session_state.video_hash = None

if "ai_thumbnail_path" not in st.session_state:
    st.session_state.ai_thumbnail_path = None

if "ai_thumbnail_generated" not in st.session_state:
    st.session_state.ai_thumbnail_generated = False

if "metadata_generated" not in st.session_state:
    st.session_state.metadata_generated = False

if "metadata" not in st.session_state:
    st.session_state.metadata = None


# Title

st.title("YouTube AI Automation")

st.write(
    "Automatically analyze your video, generate YouTube "
    "metadata, create an AI or custom thumbnail, convert "
    "video format, and upload or schedule the video."
)


# Video upload

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


# Video status

if uploaded_file is None:

    st.info(
        "Upload a video to continue."
    )

else:

    # Create video hash

    current_video_hash = hashlib.md5(
        uploaded_file.getvalue()
    ).hexdigest()


    # Reset state when video changes

    if (
        st.session_state.video_hash
        != current_video_hash
    ):

        st.session_state.video_hash = (
            current_video_hash
        )

        st.session_state.ai_thumbnail_path = None

        st.session_state.ai_thumbnail_generated = False

        st.session_state.metadata_generated = False

        st.session_state.metadata = None

        old_thumbnail = "generated_thumbnail.png"

        if os.path.exists(old_thumbnail):

            try:

                os.remove(old_thumbnail)

            except PermissionError:

                pass


    # Video format

    st.subheader("Video Format")

    video_extension = os.path.splitext(
        uploaded_file.name
    )[1]


    preview_temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=video_extension
    )

    preview_temp.write(
        uploaded_file.getbuffer()
    )

    preview_temp.close()

    preview_video_path = preview_temp.name


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


    # Format selector

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


    # AI thumbnail

    st.subheader("AI Thumbnail")

    st.write(
        "Generate an AI thumbnail first. "
        "Review the result before choosing your final thumbnail."
    )


    # Generate AI thumbnail

    if st.button(
        "Generate AI Thumbnail",
        width="stretch"
    ):

        thumbnail_video_temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=video_extension
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

                thumbnail_result = generate_thumbnail(
                    thumbnail_video_path
                )

            st.session_state.ai_thumbnail_path = (
                thumbnail_result["thumbnail_path"]
            )

            st.session_state.ai_thumbnail_generated = True

            st.success(
                "AI thumbnail generated successfully!"
            )

        except Exception as error:

            st.error(
                "AI thumbnail generation failed."
            )

            st.exception(
                error
            )

        finally:

            if os.path.exists(
                thumbnail_video_path
            ):

                os.remove(
                    thumbnail_video_path
                )


    # AI thumbnail preview

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
            "Review the thumbnail above."
        )


        # Thumbnail selection

        st.subheader(
            "Choose Thumbnail"
        )

        thumbnail_choice = st.radio(
            "Which thumbnail do you want to use?",
            [
                "Use AI Thumbnail",
                "Upload Custom Thumbnail"
            ]
        )


        # Custom thumbnail

        thumbnail_file = None

        if (
            thumbnail_choice
            == "Upload Custom Thumbnail"
        ):

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

                st.image(
                    thumbnail_file,
                    caption="Custom Thumbnail Preview",
                    width="stretch"
                )


        # YouTube visibility

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


        # Upload timing

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


        # Schedule

        schedule_date = None
        schedule_time = None

        if upload_mode == "Schedule":

            schedule_date = st.date_input(
                "Schedule Date"
            )

            schedule_time = st.time_input(
                "Schedule Time",
                value=time(20, 0)
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


        # YouTube metadata

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

                st.session_state.metadata_generated = True

                st.success(
                    "Metadata generated!"
                )

            except Exception as error:

                st.error(
                    "Metadata generation failed."
                )

                st.exception(
                    error
                )

            finally:

                if os.path.exists(
                    metadata_video_path
                ):

                    os.remove(
                        metadata_video_path
                    )


        # Edit metadata

        if st.session_state.metadata_generated:

            metadata = st.session_state.metadata

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
                value=", ".join(metadata["tags"])
            )


            # Process and upload

            st.subheader(
                "Upload"
            )

            if st.button(
                "Process & Upload to YouTube",
                width="stretch"
            ):

                # Validate custom thumbnail

                if (
                    thumbnail_choice
                    == "Upload Custom Thumbnail"
                    and thumbnail_file is None
                ):

                    st.error(
                        "Please upload your custom thumbnail."
                    )

                    st.stop()


                # Save edited metadata

                metadata["title"] = edited_title

                metadata["description"] = edited_description

                metadata["tags"] = [
                    tag.strip()
                    for tag in edited_tags.split(",")
                    if tag.strip()
                ]


                # Save video temporarily

                video_temp = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=video_extension
                )

                video_temp.write(
                    uploaded_file.getbuffer()
                )

                video_temp.close()

                video_path = video_temp.name

                converted_video_path = None
                thumbnail_path = None


                try:

                    # Video conversion

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


                    # Prepare thumbnail

                    if (
                        thumbnail_choice
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


                    # Schedule

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


                    # Upload video

                    st.info(
                        "Uploading video to YouTube..."
                    )

                    upload_progress_bar = st.progress(0)

                    upload_progress_text = st.empty()


                    # Upload progress

                    def update_upload_progress(progress):

                        percentage = int(
                            progress * 100
                        )

                        upload_progress_bar.progress(
                            percentage
                        )

                        upload_progress_text.write(
                            f"Upload progress: {percentage}%"
                        )


                    # Upload to YouTube

                    video_id = upload_video(
                        video_path,
                        metadata,
                        privacy_status=privacy_status,
                        publish_at=publish_at,
                        progress_callback=update_upload_progress
                    )


                    # Upload completed

                    upload_progress_bar.progress(100)

                    upload_progress_text.success(
                        "Video upload completed!"
                    )


                    # Upload thumbnail

                    st.info(
                        "Setting selected thumbnail..."
                    )

                    thumbnail_uploaded = set_thumbnail(
                        video_id,
                        thumbnail_path
                    )

                    if thumbnail_uploaded:

                        st.success(
                            "Thumbnail uploaded and "
                            "verified by YouTube!"
                        )

                    else:

                        st.warning(
                            "YouTube accepted the thumbnail, "
                            "but it may still be processing. "
                            "Check YouTube Studio after a few moments."
                        )


                    # Save upload history

                    video_url = (
                        f"https://www.youtube.com/watch?v={video_id}"
                    )

                    upload_record = {

                        "title": metadata["title"],

                        "date": datetime.now().strftime(
                            "%d %B %Y, %I:%M %p"
                        ),

                        "status": (
                            "Scheduled"
                            if upload_mode == "Schedule"
                            else "Uploaded"
                        ),

                        "visibility": privacy_status,

                        "video_id": video_id,

                        "url": video_url
                    }


                    upload_history = load_upload_history()

                    upload_history.append(
                        upload_record
                    )

                    save_upload_history(
                        upload_history
                    )


                    # Final success

                    st.success(
                        "Process completed successfully!"
                    )

                    st.markdown(
                        f"[Open video on YouTube]({video_url})"
                    )

                    st.write(
                        "YouTube Video ID:",
                        video_id
                    )

                    st.info(
                        f"Visibility: **{privacy_status}**"
                    )


                    if upload_mode == "Schedule":

                        st.info(
                            f"Scheduled for "
                            f"{schedule_date} at "
                            f"{schedule_time.strftime('%I:%M %p')}"
                        )


                # Error handling

                except Exception as error:

                    st.error(
                        "Something went wrong."
                    )

                    st.exception(
                        error
                    )


                # Cleanup

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
                        and thumbnail_choice
                        == "Upload Custom Thumbnail"
                        and os.path.exists(
                            thumbnail_path
                        )
                    ):

                        os.remove(
                            thumbnail_path
                        )


# Upload history

st.markdown("---")

st.subheader("Upload History")

upload_history = load_upload_history()

if not upload_history:

    st.info(
        "No videos uploaded yet."
    )

else:

    for item in reversed(upload_history):

        with st.container(border=True):

            st.write(
                f"### {item.get('title', 'Untitled')}"
            )

            st.write(
                f"Date: {item.get('date', 'Unknown date')}"
            )

            st.write(
                f"Status: "
                f"**{item.get('status', 'Unknown')}**"
            )

            st.write(
                f"Visibility: "
                f"**{item.get('visibility', 'Unknown')}**"
            )

            st.write(
                f"Video ID: "
                f"`{item.get('video_id', 'Unknown')}`"
            )

            if item.get("url"):

                st.markdown(
                    f"[Open video on YouTube]({item['url']})"
                )