import os
import time
import base64
import requests
import cv2

from google import genai

from utils.video_utils import detect_aspect_ratio


# Cloudflare configuration

CLOUDFLARE_ACCOUNT_ID = os.getenv(
    "CLOUDFLARE_ACCOUNT_ID"
)

CLOUDFLARE_API_TOKEN = os.getenv(
    "CLOUDFLARE_API_TOKEN"
)

CLOUDFLARE_MODEL = (
    "@cf/black-forest-labs/flux-1-schnell"
)


# Generate thumbnail prompt

def generate_thumbnail_prompt(
    video_path,
    aspect_ratio
):
    """
    Uploads the video to Gemini and asks Gemini
    to create a prompt specifically for an AI
    YouTube thumbnail.

    Gemini does NOT generate the image here.

    Returns:
        Thumbnail generation prompt as string.
    """

    print(
        "Uploading video to Gemini for "
        "thumbnail prompt generation..."
    )

    client = genai.Client()

    video_file = client.files.upload(
        file=video_path
    )


    # Wait for Gemini video processing

    while (
        not video_file.state
        or video_file.state.name != "ACTIVE"
    ):

        print(
            "Gemini video state:",
            video_file.state
        )

        if (
            video_file.state
            and video_file.state.name == "FAILED"
        ):

            raise RuntimeError(
                "Gemini failed to process the video."
            )

        time.sleep(5)

        video_file = client.files.get(
            name=video_file.name
        )


    print(
        "Video is ready for Gemini analysis."
    )


    # Create thumbnail prompt

    prompt = f"""
Analyze this video carefully.

Create ONE detailed image-generation prompt
for a YouTube thumbnail based ONLY on the
actual content of this video.

The video aspect ratio is {aspect_ratio}.

The thumbnail must:

- Represent the actual video content.
- Focus on the most interesting or visually
  important subject/moment.
- Be cinematic and visually striking.
- Have strong subject focus.
- Use dramatic but appropriate lighting.
- Use strong contrast.
- Be suitable for a professional YouTube thumbnail.
- Avoid misleading objects, people, or events.
- Do not invent details that are not present
  in the video.
- Do not include watermarks.
- Do not include unnecessary text.
- Composition must be suitable for {aspect_ratio}.

Return ONLY the image-generation prompt.

Do not return:
- Title
- Description
- Tags
- JSON
- Markdown
- Explanation
"""


    # Generate prompt with Gemini

    print(
        "Generating thumbnail prompt with Gemini..."
    )

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=[
            {
                "type": "video",
                "uri": video_file.uri,
                "mime_type": video_file.mime_type
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
    )


    thumbnail_prompt = (
        interaction.output_text.strip()
    )


    if not thumbnail_prompt:

        raise RuntimeError(
            "Gemini did not generate a thumbnail prompt."
        )


    print(
        "\nGemini Thumbnail Prompt:"
    )

    print(
        thumbnail_prompt
    )

    return thumbnail_prompt


# Generate image with Cloudflare

def generate_image_with_cloudflare(
    prompt,
    aspect_ratio
):
    """
    Sends the Gemini-generated thumbnail prompt
    to Cloudflare Workers AI and generates an image.

    The image is then cropped/resized to the
    required aspect ratio.

    Returns:
        Path to generated thumbnail.
    """


    # Validate Cloudflare credentials

    if not CLOUDFLARE_ACCOUNT_ID:

        raise ValueError(
            "CLOUDFLARE_ACCOUNT_ID is not set."
        )

    if not CLOUDFLARE_API_TOKEN:

        raise ValueError(
            "CLOUDFLARE_API_TOKEN is not set."
        )


    # Validate aspect ratio

    if aspect_ratio not in [
        "16:9",
        "9:16"
    ]:

        raise ValueError(
            "Aspect ratio must be 16:9 or 9:16."
        )


    # Add format instructions

    if aspect_ratio == "16:9":

        final_prompt = f"""
{prompt}

Create this as a professional YouTube thumbnail.

Format:
- Landscape
- Wide cinematic composition
- 16:9 aspect ratio
- Keep the main subject clearly visible
- Strong visual hierarchy
- No watermark
"""

    else:

        final_prompt = f"""
{prompt}

Create this as a professional YouTube Shorts thumbnail.

Format:
- Portrait
- Vertical cinematic composition
- 9:16 aspect ratio
- Keep the main subject clearly visible
- Strong visual hierarchy
- No watermark
"""


    # Cloudflare API URL

    url = (
        "https://api.cloudflare.com/client/v4/"
        f"accounts/{CLOUDFLARE_ACCOUNT_ID}"
        f"/ai/run/{CLOUDFLARE_MODEL}"
    )


    # Send request

    print(
        f"\nGenerating {aspect_ratio} "
        "thumbnail with Cloudflare..."
    )

    response = requests.post(
        url,
        headers={
            "Authorization":
                f"Bearer {CLOUDFLARE_API_TOKEN}",

            "Content-Type":
                "application/json"
        },
        json={
            "prompt": final_prompt
        }
    )


    # Check response

    if not response.ok:

        raise RuntimeError(
            "Cloudflare image generation failed:\n\n"
            + response.text
        )


    data = response.json()


    if not data.get("success"):

        raise RuntimeError(
            f"Cloudflare API error:\n{data}"
        )


    # Decode image

    image_base64 = data["result"]["image"]

    image_bytes = base64.b64decode(
        image_base64
    )


    temporary_path = (
        "cloudflare_thumbnail_temp.png"
    )


    with open(
        temporary_path,
        "wb"
    ) as file:

        file.write(image_bytes)


    # Read image

    image = cv2.imread(
        temporary_path
    )


    if image is None:

        raise RuntimeError(
            "Could not read the image generated "
            "by Cloudflare."
        )


    height, width = image.shape[:2]


    # Crop image

    if aspect_ratio == "16:9":

        target_ratio = 16 / 9

    else:

        target_ratio = 9 / 16


    current_ratio = width / height


    if current_ratio > target_ratio:

        # Image is too wide

        new_width = int(
            height * target_ratio
        )

        start_x = (
            width - new_width
        ) // 2

        image = image[
            :,
            start_x:start_x + new_width
        ]

    else:

        # Image is too tall

        new_height = int(
            width / target_ratio
        )

        start_y = (
            height - new_height
        ) // 2

        image = image[
            start_y:start_y + new_height,
            :
        ]


    # Resize image

    if aspect_ratio == "16:9":

        image = cv2.resize(
            image,
            (1920, 1080)
        )

    else:

        image = cv2.resize(
            image,
            (1080, 1920)
        )


    # Save thumbnail

    output_path = (
        "generated_thumbnail.png"
    )


    success = cv2.imwrite(
        output_path,
        image
    )


    if not success:

        raise RuntimeError(
            "Could not save generated thumbnail."
        )


    # Remove temporary image

    if os.path.exists(
        temporary_path
    ):

        os.remove(
            temporary_path
        )


    print(
        "\nAI thumbnail generated successfully!"
    )

    print(
        "Thumbnail:",
        output_path
    )

    print(
        "Final size:",
        image.shape[1],
        "x",
        image.shape[0]
    )


    return output_path


# Thumbnail pipeline

def generate_thumbnail(
    video_path
):
    """
    Complete thumbnail pipeline:

    1. Detect video aspect ratio.
    2. Gemini watches the video.
    3. Gemini generates thumbnail prompt.
    4. Cloudflare generates the image.
    5. Image is converted to the correct ratio.

    Returns:
        {
            "video_format": ...,
            "thumbnail_prompt": ...,
            "thumbnail_path": ...
        }
    """


    # Detect video ratio

    print(
        "\nDetecting video aspect ratio..."
    )

    video_info = detect_aspect_ratio(
        video_path
    )


    detected_format = video_info["format"]


    print(
        "Video dimensions:",
        video_info["width"],
        "x",
        video_info["height"]
    )

    print(
        "Detected format:",
        detected_format
    )


    # Convert format name

    if detected_format == "16:9 Landscape":

        aspect_ratio = "16:9"

    elif detected_format == "9:16 Vertical":

        aspect_ratio = "9:16"

    else:

        raise ValueError(
            "The video must be approximately "
            "16:9 or 9:16 for AI thumbnail generation."
        )


    # Generate prompt with Gemini

    thumbnail_prompt = generate_thumbnail_prompt(
        video_path,
        aspect_ratio
    )


    # Generate image with Cloudflare

    thumbnail_path = generate_image_with_cloudflare(
        thumbnail_prompt,
        aspect_ratio
    )


    # Return result

    return {
        "video_format": detected_format,
        "aspect_ratio": aspect_ratio,
        "thumbnail_prompt": thumbnail_prompt,
        "thumbnail_path": thumbnail_path
    }