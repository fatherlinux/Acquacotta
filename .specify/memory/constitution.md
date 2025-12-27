# Acquacotta Constitution

## Core Principles

### I. User Data Ownership
Users own and control their data. All pomodoro records and settings are stored in the user's personal Google Sheets, accessible and editable outside the application. The application creates no proprietary data formats or vendor lock-in. Users can export their data to CSV at any time. Deleting the application leaves user data intact in their Google Drive.

### II. Offline-First Architecture
The application MUST function without network connectivity. Local SQLite serves as the primary data store for all read operations. Background sync propagates changes to Google Sheets without blocking user interactions. Sync failures MUST NOT disrupt the user experience - operations queue for retry. Local cache provides instant responsiveness regardless of network conditions.

### III. Simplicity & Focus
Acquacotta is a Pomodoro timer and time tracker - nothing more. Features MUST directly support: starting/stopping timers, categorizing completed work, and viewing time reports. Feature requests that deviate from core Pomodoro methodology require explicit justification. The UI MUST remain minimal and distraction-free. Avoid feature creep - say no to features that add complexity without proportional value.

### IV. Privacy by Design
The application collects no analytics, telemetry, or usage data. Google OAuth is used solely for authentication and Sheets API access. No user data is stored on application servers - all data flows directly between user browser and Google APIs. Session data expires and is not persisted beyond the browser session. The application requests minimal OAuth scopes (`drive.file` for app-created files only).

### V. Container-Ready Deployment
The application MUST be deployable as a single container with no external dependencies beyond Google APIs. All configuration via environment variables. No required persistent volumes for application state (user data lives in Google Sheets). Stateless design enables horizontal scaling. Support both rootless Podman and Docker deployments.

### VI. Timer Agnosticism
Users MUST be able to use the built-in timer OR an external physical timer (e.g., a desk timer) with equal effectiveness. The application MUST NOT assume the internal timer is always used. Manual entry of pomodoros MUST be a first-class feature, not an afterthought. The UI MUST make it equally easy to: (a) start the internal timer and log on completion, or (b) log a completed pomodoro after using an external timer. Time tracking is the core value - the timer is optional tooling.

## Technology Constraints

### Stack Requirements
- **Backend**: Python 3.x with Flask
- **Frontend**: Vanilla HTML/CSS/JavaScript (no build step required)
- **Local Storage**: SQLite for offline cache
- **Cloud Storage**: Google Sheets API v4
- **Authentication**: Google OAuth 2.0
- **Containerization**: OCI-compliant container images

### Security Requirements
- HTTPS required for production deployments
- OAuth tokens stored only in server-side sessions
- No client-side storage of credentials
- CSRF protection on all state-changing endpoints
- Input validation on all API endpoints

### Performance Targets
- Timer accuracy within 1 second
- UI response time under 100ms for local operations
- Sync operations complete within 5 seconds under normal network conditions
- Support for 10,000+ pomodoro records per user

## Development Workflow

### Code Quality Gates
- All Python code MUST pass linting (flake8/ruff)
- Frontend code MUST work without JavaScript frameworks
- API endpoints MUST return JSON with consistent error formats
- Changes MUST be tested manually before merge

### Branching Strategy
- `main` branch is always deployable
- Feature branches follow `feature/description` naming
- Bug fixes follow `fix/description` naming
- All changes via pull request with review

## Governance

This constitution supersedes informal practices and ad-hoc decisions. Amendments require:
1. Written proposal with rationale
2. Review period for feedback
3. Documentation of the change
4. Version increment

All development decisions MUST align with these principles. When principles conflict, prioritize in order: Privacy, User Data Ownership, Simplicity, Timer Agnosticism, Offline-First, Container-Ready.

**Version**: 1.1.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
