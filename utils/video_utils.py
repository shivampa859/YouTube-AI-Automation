import cv2
import subprocess
import os


def get_video_dimensions(video_path):
    """
    Returns the width and height of a video.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError("Could not open the video.")

    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    video.release()

    if width == 0 or height == 0:
        raise ValueError(
            "Could not determine video dimensions."
        )

    return width, height


def detect_aspect_ratio(video_path):
    """
    Detects whether the video is approximately
    16:9, 9:16, or another aspect ratio.
    """

    width, height = get_video_dimensions(
        video_path
    )

    ratio = width / height

    # 16:9
    if abs(ratio - (16 / 9)) < 0.05:

        format_name = "16:9 Landscape"

    # 9:16
    elif abs(ratio - (9 / 16)) < 0.05:

        format_name = "9:16 Vertical"

    else:

        format_name = "Other"

    return {
        "width": width,
        "height": height,
        "ratio": ratio,
        "format": format_name
    }


def convert_video_format(
    input_path,
    output_path,
    target_format
):
    """
    Converts a video to either:

    16:9 Landscape
    9:16 Vertical

    The video is cropped to fill the target
    aspect ratio without stretching/distortion.
    """

    if target_format == "9:16 Vertical":

        # 1080 x 1920
        filter_value = (
            "scale=1080:1920:"
            "force_original_aspect_ratio=increase,"
            "crop=1080:1920"
        )

    elif target_format == "16:9 Landscape":

        # 1920 x 1080
        filter_value = (
            "scale=1920:1080:"
            "force_original_aspect_ratio=increase,"
            "crop=1920:1080"
        )

    else:

        raise ValueError(
            "Target format must be "
            "'16:9 Landscape' or "
            "'9:16 Vertical'."
        )

    command = [
        "ffmpeg",

        "-y",

        "-i",
        input_path,

        "-vf",
        filter_value,

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "23",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        output_path
    ]

    print(
        f"Converting video to {target_format}..."
    )

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg conversion failed:\n\n"
            + result.stderr
        )

    if not os.path.exists(output_path):

        raise RuntimeError(
            "FFmpeg completed but the "
            "output video was not created."
        )

    print(
        "Video conversion completed successfully."
    )

    return output_path