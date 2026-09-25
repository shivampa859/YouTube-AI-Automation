# Cloudflare AI Setup

This project uses Cloudflare Workers AI to generate AI thumbnails.

You need two values:

- Cloudflare Account ID
- Cloudflare API Token

## Step 1: Open Cloudflare

1. Search for Cloudflare in Google.
2. Open the official Cloudflare website.
3. Sign in to your Cloudflare account.

## Step 2: Open Account API Tokens

1. Open the Cloudflare dashboard.
2. In the left sidebar, find `Manage Account`.
3. Open `Manage Account`.
4. Select `Account API Tokens`.
5. Click `Create Token`.

Cloudflare currently provides Account API Tokens under:

`Manage Account → Account API Tokens`

## Step 3: Create the API Token

1. Create a new account API token.
2. In the permissions section, search for:

   `Workers AI`

3. Select the Workers AI permission.
4. Give the token the following permissions:

   - Workers AI - Read
   - Workers AI - Edit

These permissions allow the application to use Workers AI through the Cloudflare API.

## Step 4: Review the Token

1. Click `Continue to summary` or `Review token`.
2. Check that the token has the required Workers AI permissions.
3. Click `Create Token`.

Cloudflare will display the API token.

## Step 5: Save the API Token

Copy the API token and save it somewhere secure.

Use it as:

```text
CLOUDFLARE_API_TOKEN