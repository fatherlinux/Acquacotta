# Acquacotta

**The Power-User's Pomodoro System.** A data-driven time tracker designed for those who want to turn their productivity history into actionable intelligence.

> *"Acquacotta automates your tracking by logging every session directly to your own Google Sheet. You own the infrastructure, you control the schema, and you can leverage the full power of spreadsheets and LLMs to analyze your performance."*

**Try it super easily with the free, hosted version here: https://acquacotta.crunchtools.com:8443** You can still save your data to your own Google Sheet.

## Why Acquacotta?

Most free, online tools are just simple 25-minute Pomodoro timers, and nothing more. Acquacotta is built for users who want to focus, but also track their performance over time, and make improvements over time.

- **Google Sheets as a Platform**: Don't just "export" data; live in it. Use Sheets' native formulas, pivot tables, and AI features to build custom dashboards that no other app provides.

- **Frictionless Automation**: Logs the category and duration automatically. Stop wasting time managing with a manual spreadsheet.

- **Extreme Configurability**: Fine-tune Acquacotta to match your exact workflow. From custom focus categories to adjustable timer increments and sound profiles, the app adapts to you, not the other way around.

- **Deep Performance Metrics**: Go beyond the clock. Track Focus Types to identify where your mental energy is actually going and where you are leaking time.

- **Fluidly Use Physical Timer or Built-in Timer**: Whether you use the built-in digital timer or a high-end physical desk timer, Acquacotta provides a unified interface to capture every minute of work.

## The Story Behind the Soup

Acquacotta was created by a veteran of the Pomodoro Technique with over 20 years of experience—ranging from engineering at NASA to leadership as a Senior Principal Product Manager at Red Hat.

For two decades, that tracking was a manual, tedious process in spreadsheets because no app offered the right balance of automation and data flexibility. Acquacotta was born to solve that: a professional-grade tool for people who want to treat their productivity like a data science project, not just a series of alarms.

**Why the name?**

Acquacotta means "cooked water" in Italian—a traditional, hearty tomato soup. Since the Pomodoro Technique is named after the tomato-shaped kitchen timer (tomato is *Pomodoro* in Italian), we felt a "complete meal" of a system—timer, automated logging, and powerful reporting—deserved a name that felt just as substantial.

## Data-Driven Performance

The classic Pomodoro method (Focus → Short Break → Repeat) is great for focus, but it's the review process that drives growth. Acquacotta puts you in the driver's seat:

- **Audit Your Focus**: Are you spending enough time on deep learning vs. shallow administrative tasks?
- **Balance Your Load**: Are meetings drowning out your "High-Value" work?
- **Align with Goals**: See a weekly or monthly breakdown of your actual output compared to your intent.

By categorizing each interval (e.g., Product, Learning, Administrative, Meetings), you turn a simple timer into a high-fidelity performance log.

## Sustainable Productivity: Finding the "Goldilocks" Zone

True productivity isn't just about doing more; it's about doing the right amount consistently. Acquacotta features visual Daily Minutes Goals to help you maintain a sustainable pace:

- **Not Too Little**: Set a target for your "deep work" minutes to ensure you feel a sense of accomplishment and momentum every single day.
- **Not Too Much**: Prevent the "heroics-to-burnout" cycle. Glancing at the reports give you visual sense of when you're working above your optimal daily capacity.
- **Real-Time Visual Feedback**: Progress bars provide an instant, at-a-glance status of your day, helping you decide whether to take on one more task or call it a day.

## The Sound of Deep Work

One of Acquacotta's most praised features is its optional Acoustic Focus Mode.

Inspired by the iconic, rhythmic ticking of a classic mechanical stopwatch or the "60 Minutes" stopwatch, our "tick-tock" audio is made to provide a subtle, grounding presence. For many users, this auditory feedback creates a stimulus that:

- **Signals Flow State**: Over time, the sound becomes a Pavlovian trigger (think Pavlov's Dogs)—when the ticking starts, your brain knows it is time for deep work.
- **Eliminates Time Blindness**: The gentle rhythm provides a subconscious sense of passing time without the anxiety of a countdown clock.
- **Anchors Concentration**: The steady beat acts as a metronome for the mind, helping to block out erratic ambient noise and mental wandering.

## Features

- **Flexible Timer**: Configurable durations (5, 10, 15, 25 minutes) to match your workflow.
- **Daily Goal Tracking**: Set and monitor visual minute targets to balance output and recovery.
- **Physical Timer Support**: A dedicated mode to log completed pomodoros from tactile hardware instantly.
- **Focus Audio**: Optional "60 Minutes" style ticking sound to maintain a high-tempo focus environment.
- **Integrated Visuals**: Instant daily, weekly, and monthly performance charts built into the app.
- **Offline-First Architecture**: A local SQLite cache ensures the UI is lightning-fast, even when your connection isn't.
- **Native Sheets Backend**: Direct, real-time logging to your personal Google Cloud.
- **Power-User Export**: Full CSV portability for external analysis.

## Who Is This For?

Acquacotta is built for **Engineers**, **Managers**, **Freelancers**, and **Data Nerds** who want to:

- Quantify their work habits with professional-grade accuracy.
- Automate the "admin of productivity."
- Maintain a permanent, accessible record of their career output.

## Self-Hosting

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
  quay.io/fatherlinux/acquacotta:latest
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
| `CLEAR_CACHE_ON_START` | No | Clear SQLite cache on startup (default: `true`) |

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

You own your data and can access/edit it directly in Google Sheets. Power users can:
- Make backups anytime
- Analyze patterns with LLMs
- Build custom reports
- Export to other tools

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

This project is licensed under the GPL-3.0 License.
