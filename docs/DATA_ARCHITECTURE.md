# Acquacotta Data Architecture

This document explains how Acquacotta stores and synchronizes your pomodoro data. It's written for multiple audiences: everyday users, software architects, developers, and system administrators.

## Table of Contents

1. [For Users: Where Does My Data Live?](#for-users-where-does-my-data-live)
2. [For Architects: System Design](#for-architects-system-design)
3. [For Developers: Implementation Details](#for-developers-implementation-details)
4. [For Sysadmins: Deployment & Operations](#for-sysadmins-deployment--operations)

---

## For Users: Where Does My Data Live?

### Demo Mode (Not Logged In)

When you use Acquacotta without logging in:

- **Your data stays on your device** - stored in your browser's local database (IndexedDB)
- **Nothing is sent to any server** - complete privacy
- **Data persists** until you clear your browser data
- **No account needed** - just start tracking

### Logged In Mode (Google Account)

When you log in with Google:

- **Your data is stored in YOUR Google Sheets** - a spreadsheet in your own Google Drive
- **The server never stores your data** - it only helps you talk to Google
- **You own your data** - export, delete, or modify it anytime in Google Sheets
- **Syncs across devices** - access from any browser where you log in

### What Gets Stored?

| Data Type | Demo Mode | Logged In Mode |
|-----------|-----------|----------------|
| Pomodoros (tasks, times, notes) | Browser only | Browser + Your Google Sheet |
| Settings (timer presets, preferences) | Browser only | Browser + Your Google Sheet |
| Google credentials | N/A | Browser only (NOT on server) |

### Privacy Guarantees

1. **No analytics or tracking** - we don't know how you use the app
2. **No data on our servers** - the server is stateless
3. **Your Google Sheet = Your data** - we can't see it without you being logged in
4. **Minimal permissions** - we only ask for access to files we create

---

## For Architects: System Design

### Design Principles

1. **Stateless Server** - The server stores no user data
2. **Browser-First Storage** - IndexedDB is the primary data store
3. **User-Owned Cloud Backup** - Google Sheets belongs to the user
4. **Offline-First** - Full functionality without internet

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                          │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │   Acquacotta    │    │    IndexedDB    │                     │
│  │   Frontend      │◄──►│  (Primary Store)│                     │
│  │   (JavaScript)  │    │                 │                     │
│  └────────┬────────┘    │ • pomodoros     │                     │
│           │             │ • settings      │                     │
│           │             │ • sync_queue    │                     │
│           │             │ • auth (creds)  │                     │
│           │             └─────────────────┘                     │
└───────────┼─────────────────────────────────────────────────────┘
            │ HTTPS (credentials in request)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ACQUACOTTA SERVER                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Flask Application                      │    │
│  │  • OAuth flow handler (login/callback)                   │    │
│  │  • Google Sheets API proxy                               │    │
│  │  • NO user data storage                                  │    │
│  │  • NO database                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────┬─────────────────────────────────────────────────────┘
            │ Google APIs (OAuth tokens from browser)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER'S GOOGLE ACCOUNT                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Google Sheets (User's Drive)                │    │
│  │                                                          │    │
│  │  Spreadsheet: "Acquacotta Pomodoro Tracker"              │    │
│  │  ├── Sheet: "Pomodoros"                                  │    │
│  │  │   └── Columns: id, name, type, start_time,            │    │
│  │  │                end_time, duration_minutes, notes      │    │
│  │  └── Sheet: "Settings"                                   │    │
│  │      └── Columns: key, value                             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: Creating a Pomodoro

```
1. User completes timer
   │
2. Save to IndexedDB (immediate, works offline)
   │
3. Add to sync_queue in IndexedDB
   │
4. If online + logged in:
   │
5. POST /api/sheets/pomodoros
   │  (credentials included in request body)
   │
6. Server proxies to Google Sheets API
   │  (using user's OAuth token)
   │
7. On success: mark synced=true, remove from queue
   On failure: retry with exponential backoff
```

### Sync Strategies

| Scenario | Strategy |
|----------|----------|
| New Google Sheet | Push local data TO Sheet |
| Existing Google Sheet | Bidirectional sync by unique ID |
| Settings conflict | Sheet is authoritative (pull from Sheet) |
| Pomodoro conflict | Merge by ID (no overwrites) |
| Offline changes | Queue locally, sync when online |

### Duplicate Prevention

Duplicates are prevented at multiple layers:

1. **Sync Queue** - Removes existing queue items for same record before adding
2. **Backend Check** - `save_pomodoro()` checks if ID exists before appending
3. **Initial Sync** - Runs deduplication on first connect to existing sheet

---

## For Developers: Implementation Details

### IndexedDB Schema

```javascript
// Database: 'acquacotta', Version: 2

// Object Store: 'pomodoros'
// KeyPath: 'id'
// Indexes: 'start_time', 'type', 'synced'
{
    id: "uuid-v4",
    name: "Task name",
    type: "Product",
    start_time: "2025-01-25T09:00:00.000Z",  // ISO 8601
    end_time: "2025-01-25T09:25:00.000Z",
    duration_minutes: 25,
    notes: "Optional notes",
    synced: false  // true after synced to Sheets
}

// Object Store: 'settings'
// KeyPath: 'key'
{
    key: "timer_preset_1",
    value: 25,
    synced: false
}

// Object Store: 'sync_queue'
// KeyPath: 'id' (autoIncrement)
{
    id: 1,
    operation: "create",  // create, update, delete
    store: "pomodoros",
    record_id: "uuid",
    data: { ... },
    created_at: "2025-01-25T09:00:00.000Z",
    retries: 0
}

// Object Store: 'auth'
// KeyPath: 'key'
{
    key: "credentials",
    token: "ya29...",
    refresh_token: "1//...",
    spreadsheet_id: "1xQm...",
    user_email: "user@gmail.com",
    // ... other OAuth data
}

// Object Store: 'sync_status'
// KeyPath: 'key'
{
    key: "initial_sync_done",
    value: true
}
```

### Key Files

| File | Purpose |
|------|---------|
| `static/js/storage.js` | IndexedDB operations, sync logic, Storage API |
| `app.py` | Flask server, OAuth flow, Sheets API proxy |
| `sheets_storage.py` | Google Sheets CRUD operations |
| `templates/index.html` | Single-page app with all UI logic |

### API Endpoints

#### Authentication
- `GET /auth/google` - Initiate OAuth flow
- `GET /auth/callback` - OAuth callback, stores credentials in browser
- `GET /auth/logout` - Clear session
- `GET /api/auth/status` - Check if Google is configured

#### Sheets Proxy (all require credentials in request)
- `GET /api/sheets/pomodoros` - List pomodoros
- `GET /api/sheets/pomodoros/count` - Efficient count (IDs only)
- `POST /api/sheets/pomodoros` - Create pomodoro
- `PUT /api/sheets/pomodoros/<id>` - Update pomodoro
- `DELETE /api/sheets/pomodoros/<id>` - Delete pomodoro
- `GET /api/sheets/settings` - Get settings
- `POST /api/sheets/settings` - Save settings
- `POST /api/sheets/deduplicate` - Remove duplicate rows
- `GET /api/sheets/export` - Export as CSV

### Credential Handling

Credentials flow from browser to server with each request:

```javascript
// For GET/DELETE: Base64-encoded header
headers['X-Credentials'] = btoa(JSON.stringify({
    token: "...",
    refresh_token: "...",
    spreadsheet_id: "...",
    // ...
}));

// For POST/PUT: Merged into request body
body._credentials = {
    token: "...",
    refresh_token: "...",
    spreadsheet_id: "...",
    // ...
};
```

### Sync Queue Processing

```javascript
async function processSyncQueue() {
    // Promise-based lock prevents concurrent syncs
    if (syncLockPromise) {
        await syncLockPromise;
        return;
    }

    let resolveLock;
    syncLockPromise = new Promise(r => resolveLock = r);

    try {
        const queue = await getAllFromStore(STORES.SYNC_QUEUE);
        queue.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

        for (const item of queue) {
            await syncOperationToSheets(item);
            await deleteFromStore(STORES.SYNC_QUEUE, item.id);
        }
    } finally {
        syncLockPromise = null;
        resolveLock();
    }
}
```

### Initial Sync Logic

```javascript
if (storedCredentials.spreadsheet_existed) {
    // Existing sheet: bidirectional merge
    // 1. Deduplicate Sheet
    // 2. Pull pomodoros from Sheet (add missing to local)
    // 3. Push local pomodoros to Sheet (add missing to Sheet)
    // 4. Pull settings from Sheet (Sheet is authoritative)
    // 5. Save spreadsheet_id to Sheet settings
} else {
    // New sheet: push local to Sheet
    // 1. Queue all local pomodoros
    // 2. Queue all local settings
    // 3. Process sync queue
}
```

---

## For Sysadmins: Deployment & Operations

### Container Architecture

```
┌─────────────────────────────────────────┐
│           Container (Port 80)           │
│  ┌─────────────────────────────────┐    │
│  │     Apache (Reverse Proxy)      │    │
│  │         Port 80 (external)      │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────▼──────────────────┐    │
│  │     Gunicorn (WSGI Server)      │    │
│  │       Port 5000 (internal)      │    │
│  └──────────────┬──────────────────┘    │
│                 │                        │
│  ┌──────────────▼──────────────────┐    │
│  │     Flask Application           │    │
│  │       (Stateless)               │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Environment Variables

```bash
# Required for Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Flask configuration
FLASK_SECRET_KEY=random-secret-for-sessions
```

### Container Commands

```bash
# Build
podman build -t acquacotta:dev -f Containerfile .

# Run (map host:5000 to container:80)
podman run -d --name acquacotta-dev \
    -p 5000:80 \
    --env-file .env \
    acquacotta:dev

# View logs
podman logs -f acquacotta-dev

# Stop and remove
podman stop acquacotta-dev && podman rm acquacotta-dev
```

### What the Server DOES Store

| Item | Storage | Purpose |
|------|---------|---------|
| Flask session cookie | Memory (not persisted) | CSRF protection during OAuth |
| Static files | Container filesystem | HTML, JS, CSS |

### What the Server Does NOT Store

- User pomodoro data
- User settings
- OAuth tokens (passed per-request from browser)
- Any persistent database

### Scaling Considerations

Since the server is stateless:

- **Horizontal scaling** - Run multiple containers behind a load balancer
- **No shared state** - No database clustering needed
- **No sticky sessions** - Any container can handle any request
- **Container restarts** - No data loss (data lives in browser + Google Sheets)

### Monitoring

Key metrics to watch:

- Google Sheets API quota usage (per user)
- OAuth token refresh failures
- 5xx error rates on `/api/sheets/*` endpoints

### Backup & Recovery

- **User data backup** - Users own their Google Sheet (Google handles backup)
- **Server backup** - Not needed (stateless, no persistent data)
- **Browser data loss** - User logs in again, data syncs from their Sheet

---

## Appendix: Google Sheets Structure

### Pomodoros Sheet

| Column | Type | Description |
|--------|------|-------------|
| A: id | UUID | Unique identifier |
| B: name | String | Task/activity name |
| C: type | String | Category (Product, Learn, etc.) |
| D: start_time | ISO 8601 | When pomodoro started |
| E: end_time | ISO 8601 | When pomodoro ended |
| F: duration_minutes | Integer | Duration in minutes |
| G: notes | String | Optional notes |

### Settings Sheet

| Column | Type | Description |
|--------|------|-------------|
| A: key | String | Setting name |
| B: value | JSON | Setting value (JSON-encoded) |

Example settings:
- `timer_preset_1`: `25`
- `pomodoro_types`: `["Product", "Learn", "Team"]`
- `spreadsheet_id`: `"1xQm..."` (for reconnection)
