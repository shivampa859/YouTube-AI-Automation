# Gemini API Setup

This project uses Google Gemini to analyze videos and generate YouTube metadata.

Gemini is used for:

- Video analysis
- YouTube title generation
- YouTube description generation
- YouTube tags generation
- Thumbnail prompt generation

You need one value:

- Gemini API Key

## Step 1: Open Google AI Studio

1. Search for Google AI Studio in Google.
2. Open the official Google AI Studio website.
3. Sign in with your Google account.

## Step 2: Create an API Key

1. Open the Google AI Studio dashboard.
2. Find the option for `Get API key`.
3. Click `Create API key`.
4. Select an existing Google Cloud project or create a new project if required.
5. Create the API key.

Google AI Studio provides API keys for using the Gemini API.

## Step 3: Copy the API Key

After creating the API key, copy it and save it somewhere secure.

Use it as:

```text
GEMINI_API_KEY

Do not share the API key or upload it to GitHub.

Step 4: Configure the Environment Variable

The application reads the Gemini API key from the environment variable:

GEMINI_API_KEY=your_gemini_api_key

For local development, add the key to your system environment variables.

For cloud deployment, add it through the platform's Secrets or Environment Variables settings.

Step 5: Verify the Configuration

After configuring the API key, start the application:

streamlit run app.py

Upload a video and run the metadata generation process.

The application will use Gemini to analyze the video and generate:

Title
Description
Tags
Gemini in This Project

Gemini is used in two parts of the application.

Video Metadata Generation
Video
  ↓
Gemini
  ↓
Title
Description
Tags
Thumbnail Prompt Generation
Video
  ↓
Gemini
  ↓
Thumbnail Prompt
  ↓
Cloudflare AI
  ↓
AI Thumbnail
Important

Never put your real Gemini API key inside:

Python source code
README.md
.env.example
GitHub
Screenshots

Use a placeholder in documentation:

GEMINI_API_KEY=your_gemini_api_key_here

Keep the actual API key private.