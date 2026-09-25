# YouTube AI Automation – AI-Powered YouTube Video Publishing System

YouTube AI Automation is an AI-powered video publishing application built using Python and Streamlit.

The project automates major parts of the YouTube publishing workflow, including video analysis, metadata generation, thumbnail generation, video format detection, video conversion, thumbnail selection, YouTube uploading, scheduling, and upload history management.

The application uses Google Gemini to analyze video content and generate YouTube metadata, Cloudflare AI to generate thumbnails, FFmpeg for video processing, OpenCV for video analysis, and the YouTube Data API v3 for video uploading.

---

## Project Overview

This project demonstrates:

- AI-powered video content analysis
- Automatic YouTube title generation
- Automatic YouTube description generation
- Automatic YouTube tag generation
- AI thumbnail generation
- Video aspect ratio detection
- Video format conversion using FFmpeg
- Custom thumbnail upload
- YouTube video upload using YouTube Data API v3
- YouTube video scheduling
- YouTube visibility control
- Upload progress tracking
- Upload history management
- Streamlit-based user interface
- Google OAuth 2.0 authentication
- Environment variable and API credential management

The main goal of this project is to reduce the manual work involved in preparing and publishing YouTube videos.

---

## Project Architecture

```text
                              YouTube AI Automation
                                       │
                                       ▼
                              Streamlit Web Interface
                                       │
                                       ▼
                                  Upload Video
                                       │
                                       ▼
                            Detect Aspect Ratio
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                      16:9                         9:16
                    Landscape                     Vertical
                         │                           │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                             Video Format Conversion
                                       │
                                       ▼
                             Google Gemini Analysis
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                          ▼                         ▼
                       Title                 Description
                          │                         │
                          └────────────┬────────────┘
                                       │
                                       ▼
                                      Tags
                                       │
                                       ▼
                              AI Thumbnail Generation
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                          ▼                         ▼
                       Gemini                  Cloudflare AI
                  Prompt Generation          Image Generation
                          │                         │
                          └────────────┬────────────┘
                                       │
                                       ▼
                              Thumbnail Preview
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
                  AI Thumbnail               Custom Thumbnail
                         │                           │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                              Upload Configuration
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
                     Upload Now                  Schedule
                         │                           │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                              YouTube Data API v3
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
                    Video Upload              Thumbnail Upload
                         │                           │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                                Upload Result
                                       │
                                       ▼
                                Upload History
                                       │
                                       ▼
                              Stored Locally
````

---

## Core Workflow

```text
Upload Video
     ↓
Detect Aspect Ratio
     ↓
Convert Video if Required
     ↓
Analyze Video with Gemini
     ↓
Generate Title
     ↓
Generate Description
     ↓
Generate Tags
     ↓
Generate AI Thumbnail
     ↓
Preview Thumbnail
     ↓
Choose AI or Custom Thumbnail
     ↓
Select Visibility
     ↓
Choose Upload Now or Schedule
     ↓
Upload Video to YouTube
     ↓
Set Selected Thumbnail
     ↓
Display Upload Result
     ↓
Save Upload History
```

---

## Features

### Video Upload

Users can upload a video directly through the Streamlit interface.

The application processes the uploaded video before sending it to the AI and YouTube services.

---

### Video Aspect Ratio Detection

The application automatically detects the uploaded video's aspect ratio.

Supported formats include:

* 16:9 Landscape
* 9:16 Vertical
* Other

This allows the application to determine the appropriate processing and thumbnail dimensions.

---

### Video Format Conversion

The application uses FFmpeg to convert videos into the required format.

Supported target formats:

* 1920 × 1080 for 16:9 Landscape
* 1080 × 1920 for 9:16 Vertical

The conversion process uses scaling and cropping to maintain the required aspect ratio.

---

### AI Video Analysis

Google Gemini analyzes the actual video content.

The AI generates YouTube metadata based on the uploaded video.

Generated metadata includes:

* YouTube title
* YouTube description
* YouTube tags

The generated metadata can be reviewed and edited before uploading.

---

### AI Thumbnail Generation

The application generates an AI thumbnail using a two-stage process.

First, Google Gemini analyzes the video and creates a thumbnail-generation prompt.

Then, Cloudflare AI uses that prompt to generate the thumbnail image.

```text
Video
  ↓
Gemini
  ↓
Thumbnail Prompt
  ↓
Cloudflare AI
  ↓
Generated Thumbnail
```

The generated thumbnail is then processed according to the detected video format.

---

### Custom Thumbnail

Users can choose between:

* AI-generated thumbnail
* Custom uploaded thumbnail

This provides flexibility when the user already has a manually designed thumbnail.

---

### Thumbnail Preview

The generated AI thumbnail is displayed before uploading the video.

Users can review the thumbnail and decide whether to use it or upload their own thumbnail.

---

### YouTube Visibility

Users can select the visibility of the uploaded video:

* Private
* Unlisted
* Public

---

### YouTube Scheduling

The application supports scheduled publishing.

Users can select a future date and time for the video to be published.

---

### Upload Progress

The application displays upload progress while the video is being uploaded to YouTube.

This provides feedback during large video uploads.

---

### Upload History

The application maintains a local upload history after successful uploads.

The upload history can contain:

* Video title
* Upload date
* Upload status
* Visibility
* YouTube video ID
* YouTube video URL

The history is stored locally in:

```text
upload_history.json
```

Upload history is displayed at the bottom of the Streamlit application.

---

## Technologies Used

### Programming Language

* Python

### Frontend / User Interface

* Streamlit

### Artificial Intelligence

* Google Gemini API
* Cloudflare AI

### Video Processing

* FFmpeg
* OpenCV

### YouTube Integration

* YouTube Data API v3
* Google OAuth 2.0

### Supporting Libraries

* Google GenAI SDK
* Google API Client
* Google Authentication Libraries
* Requests

### Version Control

* Git
* GitHub

---

## Project Structure

```text
YouTube-AI-Automation/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── services/
│   ├── gemini_service.py
│   ├── thumbnail_service.py
│   └── youtube_service.py
│
└── utils/
    └── video_utils.py
```

---

## Project File Description

### `app.py`

Main Streamlit application.

It handles:

* User interface
* Video upload
* Video format selection
* Video conversion
* Metadata generation
* Thumbnail generation
* Thumbnail selection
* Visibility selection
* Scheduling
* YouTube upload
* Upload progress
* Upload history

---

### `services/gemini_service.py`

Handles communication with Google Gemini.

Its main responsibility is analyzing the uploaded video and generating:

* Title
* Description
* Tags

---

### `services/thumbnail_service.py`

Handles AI thumbnail generation.

The service:

1. Detects the video format.
2. Sends the video to Gemini.
3. Generates a thumbnail prompt.
4. Sends the prompt to Cloudflare AI.
5. Processes the generated image.
6. Crops the image according to the required aspect ratio.
7. Resizes the thumbnail.
8. Saves the final thumbnail.

---

### `services/youtube_service.py`

Handles YouTube API operations.

Its responsibilities include:

* Google OAuth authentication
* YouTube API connection
* Video upload
* Upload progress
* Thumbnail upload

---

### `utils/video_utils.py`

Contains video-processing utilities.

Its responsibilities include:

* Reading video dimensions
* Detecting video aspect ratio
* Converting video format using FFmpeg

---

### `requirements.txt`

Contains the Python dependencies required to run the project.

---

### `.env.example`

Provides an example of the environment variables required by the application.

Actual credentials should never be stored in this file.

---

### `.gitignore`

Prevents sensitive credentials, generated files, local videos, virtual environments, and other local files from being uploaded to GitHub.

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/shivampa859/YouTube-AI-Automation.git
```

Navigate to the project:

```bash
cd YouTube-AI-Automation
```

---

## Create Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\activate
```

---

## Install Dependencies

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

---

## FFmpeg Setup

The application uses FFmpeg for video conversion.

FFmpeg must be installed and available in the system PATH.

Verify the installation using:

```powershell
ffmpeg -version
```

If FFmpeg is installed correctly, the command will display the installed FFmpeg version.

---

## API Configuration

The application requires credentials for the following services:

* Google Gemini
* Cloudflare AI
* YouTube Data API v3

---

## Google Gemini Setup

Google Gemini is used for:

* Video analysis
* YouTube metadata generation
* Thumbnail prompt generation

Required environment variable:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The actual API key must never be committed to GitHub.

---

## Cloudflare AI Setup

Cloudflare AI is used for:

* AI thumbnail image generation

Required environment variables:

```env
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
```

The actual Cloudflare credentials must never be committed to GitHub.

---

## YouTube Data API v3 Setup

The YouTube integration is used for:

* Uploading videos
* Setting video visibility
* Scheduling videos
* Uploading thumbnails

YouTube authentication uses Google OAuth 2.0.

The setup requires:

1. Create a Google Cloud project.
2. Enable YouTube Data API v3.
3. Configure the OAuth consent screen.
4. Create an OAuth client.
5. Download the OAuth client credentials.
6. Store the credentials locally.
7. Run the application.
8. Complete Google authentication.
9. Allow the required YouTube permissions.
10. Store the generated authentication token locally.

OAuth credentials should never be uploaded to GitHub.

---

## Environment Variables

The application uses the following environment variables:

```env
GEMINI_API_KEY=your_gemini_api_key_here
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id_here
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token_here
```

Use `.env.example` as a reference.

Never add actual API keys to the repository.

---

## Run the Application

Start the Streamlit application:

```powershell
streamlit run app.py
```

The application will open in the browser.

The default Streamlit address is:

```text
http://localhost:8501
```

---

## Application Workflow

### Step 1: Upload Video

Upload a video through the Streamlit interface.

### Step 2: Detect Video Format

The application detects whether the video is:

* 16:9 Landscape
* 9:16 Vertical
* Other

### Step 3: Convert Video

If required, the application converts the video using FFmpeg.

### Step 4: Generate Metadata

Gemini analyzes the video and generates:

* Title
* Description
* Tags

The generated metadata can be edited before uploading.

### Step 5: Generate Thumbnail

Gemini creates a thumbnail prompt and Cloudflare AI generates the thumbnail.

### Step 6: Preview Thumbnail

The generated thumbnail is displayed in the application.

### Step 7: Select Thumbnail

Choose:

* AI-generated thumbnail
* Custom thumbnail

### Step 8: Configure Upload

Select:

* Visibility
* Upload timing
* Schedule date and time if required

### Step 9: Upload

The application uploads the video to YouTube and sets the selected thumbnail.

### Step 10: Upload Result

After the upload completes, the application displays the YouTube video information.

### Step 11: Upload History

The successful upload is saved to the local upload history and displayed at the bottom of the application.

---

## Security

Sensitive credentials must never be committed to the repository.

The following files and credentials must remain private:

```text
.env
credentials/
token.json
client_secret.json
```

Local files such as the following should also remain outside the public repository:

```text
videos/
uploaded/
failed/
upload_history.json
```

The project `.gitignore` prevents these files from being added to Git.

API keys should be stored using environment variables or the secret-management system provided by the deployment platform.

Never share:

* API keys
* Cloudflare tokens
* OAuth client secrets
* OAuth access tokens
* OAuth refresh tokens

---

## Deployment

The application is designed to be deployed as a Streamlit application.

The project can be deployed using cloud platforms that support Streamlit applications and environment secrets.

Deployment requires configuring the required environment variables:

* Gemini API key
* Cloudflare Account ID
* Cloudflare API token

YouTube OAuth requires additional configuration for production deployment because authentication credentials and user authorization should not be exposed publicly.

---

## Current Project Status

The core application currently supports:

* Video upload
* Video aspect ratio detection
* Video format conversion
* Gemini video analysis
* AI metadata generation
* AI thumbnail generation
* Custom thumbnail selection
* YouTube visibility selection
* YouTube video upload
* Scheduled publishing
* Upload progress
* Upload history

---

## Future Improvements

Possible future improvements include:

* Improved AI thumbnail generation
* Better thumbnail prompt generation
* Additional video format options
* Multiple YouTube channel support
* Advanced scheduling
* Cloud-based upload history
* Improved error handling
* Production-ready multi-user OAuth
* Deployment optimization
* Additional AI-generated metadata options

---

## Key Learning Outcomes

This project demonstrates practical experience with:

* Python application development
* Streamlit application development
* Generative AI integration
* Google Gemini API
* AI-based video analysis
* AI image generation
* Cloudflare AI
* YouTube Data API v3
* Google OAuth 2.0
* FFmpeg video processing
* OpenCV
* REST API integration
* Environment variable management
* Git and GitHub
* AI-powered workflow automation

---

## Author
### Shivam Patel
Computer Science and Engineering Graduate

Interests:

* Artificial Intelligence
* Machine Learning
* Computer Vision
* Generative AI
* Agentic AI
* Automation


```
```
