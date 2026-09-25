import time
from google import genai


def analyze_video(video_path):
    """
    Uploads a video to Gemini and generates
    YouTube title, description, and tags.
    """

    client = genai.Client()

    print("Uploading video to Gemini...")

    video_file = client.files.upload(file=video_path)

    # Wait until Gemini finishes processing
    while not video_file.state or video_file.state.name != "ACTIVE":

        print("Gemini video state:", video_file.state)

        if video_file.state and video_file.state.name == "FAILED":
            raise RuntimeError(
                "Gemini failed to process the video."
            )

        time.sleep(5)

        video_file = client.files.get(
            name=video_file.name
        )

    print("Video is ready for Gemini analysis.")

    prompt = """
Analyze this video carefully and generate YouTube metadata
based ONLY on the actual video content.

Return ONLY valid JSON.
Do not use markdown.
Do not use ```.

Use exactly this structure:

{
    "title": "YouTube title here",
    "description": "YouTube description here",
    "tags": [
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5",
        "tag6",
        "tag7",
        "tag8",
        "tag9",
        "tag10"
    ]
}

Requirements:
- title: compelling and accurate
- description: detailed and accurate summary
- tags: exactly 10 relevant tags
"""

    print("Generating metadata with Gemini...")

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

    print("Gemini analysis completed.")

    return interaction.output_text