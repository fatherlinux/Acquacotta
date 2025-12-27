# Acquacotta - Claude Code Instructions

## Project Overview

Acquacotta is a Pomodoro time tracking web application. Before making changes, understand the project's governing principles and specifications.

## Required Reading

Before implementing any feature or making significant changes, read:

1. **Constitution** (`.specify/memory/constitution.md`) - Core principles that govern all decisions
2. **Baseline Spec** (`.specify/specs/000-baseline/spec.md`) - All user stories and requirements
3. **Technical Plan** (`.specify/specs/000-baseline/plan.md`) - Architecture and API documentation

## Core Principles (Summary)

All work must align with these principles (in priority order):

1. **Privacy by Design** - No analytics, no telemetry, minimal OAuth scopes
2. **User Data Ownership** - Data lives in user's Google Sheets, not our servers
3. **Simplicity & Focus** - Pomodoro timer and time tracking only, no feature creep
4. **Timer Agnosticism** - Internal timer and external physical timers are equally supported
5. **Offline-First** - SQLite cache for all reads, background sync to Google Sheets
6. **Container-Ready** - Single container, env var config, no persistent volumes

## Technology Stack

- **Backend**: Python 3.x / Flask
- **Frontend**: Vanilla HTML/CSS/JavaScript (no build step)
- **Local Storage**: SQLite
- **Cloud Storage**: Google Sheets API v4
- **Auth**: Google OAuth 2.0

## Before Making Changes

1. Check if the change aligns with the constitution principles
2. Verify the change fits within existing user stories or propose a new spec
3. Manual entry must remain a first-class feature (Timer Agnosticism principle)
4. Never add analytics, tracking, or telemetry
5. Keep the UI minimal and distraction-free

## Spec-Kit Commands

Use these slash commands for structured development:

- `/speckit.constitution` - Update project principles
- `/speckit.specify` - Create a new feature specification
- `/speckit.plan` - Create implementation plan from spec
- `/speckit.tasks` - Generate task breakdown
- `/speckit.implement` - Execute implementation
- `/speckit.clarify` - Clarify ambiguous requirements
- `/speckit.analyze` - Cross-artifact consistency check

## File Structure

```
.specify/
├── memory/constitution.md    # Governing principles
├── specs/                    # Feature specifications
│   └── 000-baseline/         # Current app baseline
└── templates/                # Spec-kit templates

app.py                        # Flask application
sheets_storage.py             # Google Sheets operations
templates/                    # HTML templates
```
