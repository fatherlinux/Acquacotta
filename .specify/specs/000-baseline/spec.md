# Feature Specification: Acquacotta Baseline

**Feature Branch**: `000-baseline`
**Created**: 2025-12-27
**Status**: Active
**Input**: Define all existing workflows and intents for the Acquacotta Pomodoro time tracker

## User Scenarios & Testing

### User Story 1 - Start and Complete a Pomodoro Timer (Priority: P1)

A user wants to track their focused work time using the Pomodoro technique. They select a duration, start the timer, and upon completion receive an audible notification and can categorize their work.

**Why this priority**: Core functionality - without a working timer, the app has no purpose.

**Independent Test**: Start a 5-minute timer, wait for completion, verify bell sounds and completion dialog appears.

**Acceptance Scenarios**:

1. **Given** the timer is not running, **When** user clicks a duration preset (5/10/15/25 min), **Then** timer starts counting down from selected duration
2. **Given** timer is running, **When** countdown reaches zero, **Then** bell sound plays and desktop notification appears
3. **Given** timer completed, **When** completion dialog appears, **Then** user can enter name, select type, and save the pomodoro

---

### User Story 2 - View Time Reports (Priority: P1)

A user wants to see how they've spent their time across different categories over various time periods.

**Why this priority**: Without reporting, users cannot gain insights from their tracked time.

**Independent Test**: Complete 3 pomodoros with different types, navigate to Reports, verify daily/weekly/monthly views show accurate totals.

**Acceptance Scenarios**:

1. **Given** user has recorded pomodoros, **When** user navigates to Reports, **Then** daily view shows breakdown by type with totals
2. **Given** user is viewing daily report, **When** user switches to week view, **Then** 7-day summary displays with daily totals chart
3. **Given** user is viewing reports, **When** user navigates between periods, **Then** data updates without page reload

---

### User Story 3 - Google Account Login and Sync (Priority: P2)

A user wants to persist their data in their Google Drive so they can access it from any device or after reinstalling.

**Why this priority**: Essential for data persistence but app works offline without it.

**Independent Test**: Log in with Google, complete a pomodoro, verify data appears in Google Sheet.

**Acceptance Scenarios**:

1. **Given** user is not logged in, **When** user clicks "Sign in with Google", **Then** OAuth flow completes and user is authenticated
2. **Given** user is logged in for first time, **When** authentication completes, **Then** new spreadsheet "Acquacotta - Pomodoro Tracker" is created in user's Drive
3. **Given** user is logged in, **When** user completes a pomodoro, **Then** data syncs to Google Sheets in background

---

### User Story 4 - Pause and Resume Timer (Priority: P2)

A user needs to temporarily pause their focus session due to an interruption.

**Why this priority**: Important for real-world usage but not essential for basic tracking.

**Independent Test**: Start timer, pause after 2 minutes, resume, verify total time is accurate.

**Acceptance Scenarios**:

1. **Given** timer is running, **When** user clicks pause, **Then** timer stops and shows paused state
2. **Given** timer is paused, **When** user clicks resume, **Then** timer continues from where it stopped
3. **Given** timer was paused and completed, **When** user saves pomodoro, **Then** recorded duration reflects only active time

---

### User Story 5 - Manual Pomodoro Entry (Priority: P1)

A user wants to log work they did using an external physical timer (e.g., desk timer) or retroactively after forgetting to start the in-app timer.

**Why this priority**: Per Timer Agnosticism principle - manual entry is a first-class feature, not an afterthought. Users with external timers should have an equally good experience.

**Independent Test**: Open manual entry form, enter custom start/end times and category, verify record appears in history.

**Acceptance Scenarios**:

1. **Given** user is on main page, **When** user clicks "Add Manual Entry", **Then** form appears with date/time pickers
2. **Given** manual entry form is open, **When** user fills in details and submits, **Then** pomodoro is saved with custom times
3. **Given** manual pomodoro is saved, **When** user views reports, **Then** manual entry appears in totals

---

### User Story 6 - Configure Timer Settings (Priority: P3)

A user wants to customize timer presets, break durations, and notification preferences.

**Why this priority**: Personalization enhances experience but defaults work for most users.

**Independent Test**: Change timer presets in settings, verify new values appear on main page.

**Acceptance Scenarios**:

1. **Given** user opens Settings, **When** user modifies timer preset values, **Then** new presets appear on timer page
2. **Given** user has configured breaks, **When** pomodoro completes, **Then** break timer offers configured duration
3. **Given** user disables sounds, **When** timer completes, **Then** no audio plays (only visual notification)

---

### User Story 7 - Edit or Delete Past Pomodoros (Priority: P3)

A user needs to correct a mistake in a previously recorded pomodoro.

**Why this priority**: Data correction is important but not frequently needed.

**Independent Test**: Find a pomodoro in history, edit its type, verify change persists and syncs.

**Acceptance Scenarios**:

1. **Given** user views pomodoro history, **When** user clicks edit on a record, **Then** edit form appears with current values
2. **Given** edit form is open, **When** user changes type and saves, **Then** record updates locally and syncs to Sheets
3. **Given** user views a pomodoro, **When** user clicks delete, **Then** record is removed from local cache and Sheets

---

### User Story 8 - Export Data to CSV (Priority: P3)

A user wants to export their data for backup or analysis in external tools.

**Why this priority**: Nice-to-have feature for power users.

**Independent Test**: Click export, verify CSV file downloads with all pomodoro records.

**Acceptance Scenarios**:

1. **Given** user has recorded pomodoros, **When** user clicks Export CSV, **Then** browser downloads CSV file
2. **Given** CSV is downloaded, **When** user opens in spreadsheet app, **Then** all columns (id, name, type, times, duration, notes) are present

---

### User Story 9 - Data Migration on Login (Priority: P3)

A user who has been using the app offline logs in for the first time and needs to migrate existing local data.

**Why this priority**: One-time scenario but critical for user experience.

**Independent Test**: Create pomodoros offline, log in, verify migration dialog offers to upload local data.

**Acceptance Scenarios**:

1. **Given** user has local pomodoros and logs in, **When** login completes, **Then** migration dialog appears showing local and cloud counts
2. **Given** migration dialog is shown, **When** user chooses to upload local data, **Then** local records sync to Google Sheets
3. **Given** migration dialog is shown, **When** user chooses to keep cloud data, **Then** cloud data replaces local cache

---

### Edge Cases

- What happens when network disconnects during sync? → Operations queue for retry when connection restored
- What happens when timer tab is backgrounded? → Timer continues accurately using system time
- What happens when user has >10,000 pomodoros? → Pagination and date filtering limit API calls
- What happens when Google token expires? → Refresh token used automatically; if fails, user prompted to re-auth
- What happens when two devices sync simultaneously? → Last-write-wins for individual records; no conflict resolution

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a countdown timer with configurable duration presets
- **FR-002**: System MUST play an audible notification when timer completes
- **FR-003**: System MUST display desktop notification when timer completes (if permitted)
- **FR-004**: System MUST allow categorization of completed pomodoros by type
- **FR-005**: System MUST persist pomodoro records to local SQLite cache
- **FR-006**: System MUST sync pomodoro records to Google Sheets when authenticated
- **FR-007**: System MUST provide daily, weekly, and monthly report views
- **FR-008**: System MUST calculate time totals by category for each report period
- **FR-009**: System MUST allow manual entry of pomodoros with custom times
- **FR-010**: System MUST allow editing of existing pomodoro records
- **FR-011**: System MUST allow deletion of pomodoro records
- **FR-012**: System MUST export all pomodoro data as CSV
- **FR-013**: System MUST authenticate users via Google OAuth 2.0
- **FR-014**: System MUST create a Google Sheet for each user on first login
- **FR-015**: System MUST provide configurable timer presets (default: 5, 10, 15, 25 minutes)
- **FR-016**: System MUST provide configurable break durations (short and long)
- **FR-017**: System MUST support pause and resume of running timer
- **FR-018**: System MUST work offline with full functionality except sync
- **FR-019**: System MUST handle data migration between local cache and Google Sheets

### Key Entities

- **Pomodoro**: A recorded work session with id, name, type, start_time, end_time, duration_minutes, notes
- **Settings**: User preferences including timer presets, break durations, notification settings, pomodoro types
- **User**: Google account identity with email, name, picture, and associated spreadsheet_id

## Success Criteria

### Measurable Outcomes

- **SC-001**: Timer countdown accuracy within 1 second of actual elapsed time
- **SC-002**: Pomodoro save operation completes in under 100ms locally
- **SC-003**: Report data loads in under 500ms for up to 1000 records
- **SC-004**: Background sync completes within 5 seconds under normal network conditions
- **SC-005**: Application functions fully offline after initial load
- **SC-006**: Application starts and displays timer within 2 seconds
- **SC-007**: All API endpoints return valid JSON with appropriate HTTP status codes
