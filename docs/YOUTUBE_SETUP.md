# YouTube Data API v3 Setup

This project uses the YouTube Data API v3 to upload videos, set video visibility, schedule videos, and upload thumbnails.

You need a Google Cloud project and OAuth 2.0 credentials.

## Step 1: Open Google Cloud

1. Search for Google Cloud in Google.
2. Open the official Google Cloud website.
3. Sign in with your Google account.
4. Open the Google Cloud Console.

## Step 2: Create a Google Cloud Project

1. Open the project selector at the top of the Google Cloud Console.
2. Click `New Project`.
3. Enter a project name.

For example:

```text
YouTube Automation System
Click Create.
Select the project after it is created.
Step 3: Enable YouTube Data API v3
Open APIs & Services.
Click Library.
Search for:
YouTube Data API v3
Open YouTube Data API v3.
Click Enable.

The application needs this API to communicate with YouTube.

Step 4: Configure OAuth Consent Screen
Open APIs & Services.
Open the OAuth consent screen or Google Auth Platform configuration.
Configure the application information.
Select External if the application is being used outside a Google Workspace organization.
Enter the application name.
Add the required contact information.
Save the configuration.

For testing, add the Google account that will use the application as a test user if Google asks for test users.

Step 5: Create OAuth Client
Open APIs & Services → Credentials.
Click Create Credentials.
Select OAuth client ID.
For the application type, select:
Desktop app
Enter a name for the OAuth client.
Click Create.

This project uses the desktop/installed-application OAuth flow. Google documents this flow for applications running on Windows, macOS, and Linux desktops.

Step 6: Download the OAuth Credentials

After creating the OAuth client:

Download the JSON credentials file.
Create this folder inside the project:
credentials/
Put the downloaded JSON file inside the folder.
Rename it to:
client_secret.json

Your local project should look like:

YouTube-AI-Automation/
│
├── credentials/
│   └── client_secret.json
│
├── app.py
└── ...
Step 7: Run the Application

Start the application:

streamlit run app.py

When the application needs YouTube access, Google will open the authorization page in your browser.

Step 8: Sign in with Google
Select the Google account connected to your YouTube channel.
Review the permissions requested by the application.
Allow the requested permissions.
Complete the authorization process.

The YouTube Data API uses OAuth 2.0 when an application needs access to private YouTube account data or needs to perform actions on behalf of the user.

Step 9: Authentication Token

After successful authorization, the application creates:

token.json

This file is used to keep the authentication information so the application can access YouTube without asking you to authorize it every time.

Your local project may then look like:

YouTube-AI-Automation/
│
├── credentials/
│   └── client_secret.json
│
├── token.json
├── app.py
└── ...
Step 10: YouTube Permissions

This project uses the following YouTube OAuth scope:

https://www.googleapis.com/auth/youtube

This scope allows the application to manage the authenticated user's YouTube account, including operations required by this project.
```text