# Acquacotta

A Pomodoro time tracking web application that stores your data in Google Sheets.

## Features

- Timer with configurable work durations (5, 10, 15, 25 minutes)
- 60 Minutes-style tick-tock sound effect
- Categorize pomodoros by customizable types
- View daily, weekly, and monthly reports with charts
- Data stored in your personal Google Sheets
- Export data to CSV
- Desktop notifications

## Quick Start

### 1. Set Up Google Cloud Credentials (one-time, ~5 minutes)

Acquacotta uses Google Sheets to store your data. Each user needs to create their own Google Cloud credentials.

#### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top → "New Project"
3. Name it `Acquacotta` → Click "Create"
4. Make sure your new project is selected in the dropdown

#### Step 2: Enable Required APIs

1. Go to **APIs & Services** → **Library** (in the left sidebar)
2. Search for `Google Sheets API` → Click it → Click **Enable**
3. Search for `Google Drive API` → Click it → Click **Enable**

#### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** → Click "Create"
3. Fill in the required fields:
   - App name: `Acquacotta`
   - User support email: *your email*
   - Developer contact email: *your email*
4. Click **Save and Continue**
5. On the "Scopes" page, click **Save and Continue** (no changes needed)
6. On the "Test users" page, click **Save and Continue**
7. Click **Back to Dashboard**

#### Step 4: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `Acquacotta Web`
5. Under "Authorized redirect URIs", click **Add URI** and enter:
   ```
   http://localhost:5000/auth/callback
   ```
6. Click **Create**
7. A popup will show your **Client ID** and **Client Secret** - copy both!

### 2. Run with Podman/Docker

```bash
podman run -d --name acquacotta \
  --security-opt label=disable \
  --network host \
  -e GOOGLE_CLIENT_ID="your-client-id-here" \
  -e GOOGLE_CLIENT_SECRET="your-client-secret-here" \
  -e FLASK_SECRET_KEY="any-random-string-here" \
  ghcr.io/fatherlinux/acquacotta:latest
```

Or build locally:

```bash
git clone https://github.com/fatherlinux/acquacotta.git
cd acquacotta
podman build -t acquacotta .
podman run -d --name acquacotta \
  --security-opt label=disable \
  --network host \
  -e GOOGLE_CLIENT_ID="your-client-id-here" \
  -e GOOGLE_CLIENT_SECRET="your-client-secret-here" \
  -e FLASK_SECRET_KEY="any-random-string-here" \
  acquacotta
```

> **Note:** The `--security-opt label=disable` flag is needed on SELinux-enabled systems (Fedora, RHEL, CentOS).

Then open http://localhost:5000 in your browser.

### 3. Sign In

1. Open http://localhost:5000
2. Click "Sign in with Google"
3. Authorize the app to access Google Sheets
4. A new spreadsheet called "Acquacotta - Pomodoro Tracker" will be created in your Google Drive

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CLIENT_ID` | Yes | OAuth Client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Yes | OAuth Client Secret from Google Cloud Console |
| `FLASK_SECRET_KEY` | Yes | Random string for session encryption |
| `FLASK_HOST` | No | Host to bind to (default: `127.0.0.1`, use `0.0.0.0` for container) |

## Running Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export FLASK_SECRET_KEY="random-secret"

# Run
python app.py
```

## Data Storage

Your pomodoro data is stored in a Google Sheet in your own Google Drive:
- **Pomodoros tab**: All your tracked pomodoros
- **Settings tab**: Your app preferences

You own your data and can access/edit it directly in Google Sheets.

## Troubleshooting

### "Sign in with Google" button doesn't work

Make sure you've set the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables when starting the container.

### "Access blocked: This app's request is invalid"

Your redirect URI doesn't match. In Google Cloud Console → Credentials → Your OAuth Client, make sure the Authorized redirect URI is exactly:
```
http://localhost:5000/auth/callback
```

### "Google hasn't verified this app" warning

This is normal for personal OAuth apps. Click "Advanced" → "Go to Acquacotta (unsafe)" to continue. Your credentials are only used by you.

## License

MIT
