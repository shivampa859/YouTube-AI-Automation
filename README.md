# YouTube AI Automation – AI-Powered YouTube Video Publishing System

YouTube AI Automation is an AI-powered video publishing application built using Python and Streamlit.

The project automates major parts of the YouTube publishing workflow, including video analysis, metadata generation, thumbnail generation, video format detection, video conversion, thumbnail selection, and YouTube uploading.

The application uses Google Gemini to analyze video content and generate YouTube metadata, Cloudflare AI to generate thumbnails, FFmpeg for video processing, and the YouTube Data API v3 for video uploading.

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
- Upload visibility control
- Upload progress tracking
- Streamlit-based user interface
- OAuth 2.0 authentication for YouTube
- Secure API credential management

The main goal of the project is to reduce the manual work involved in preparing and publishing YouTube videos.

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
                       Detect Video Aspect Ratio
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                 16:9                        9:16
                Landscape                    Vertical
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                         Video Format Conversion
                                  │
                                  ▼
                         Google Gemini Analysis
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
                  Title                    Description
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                                 Tags
                                  │
                                  ▼
                         AI Thumbnail Generation
                                  │
                         ┌────────┴────────┐
                         │                 │
                         ▼                 ▼
                       Gemini          Cloudflare AI
                    Prompt Creation    Image Generation
                         │                 │
                         └────────┬────────┘
                                  │
                                  ▼
                         Thumbnail Preview
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
              AI Thumbnail              Custom Thumbnail
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                         YouTube Upload
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
                Upload Now                   Schedule
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                         YouTube Data API v3
                                  │
                                  ▼
                          Published / Scheduled
                              Video
