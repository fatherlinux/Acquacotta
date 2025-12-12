# Acquacotta - Pomodoro Time Tracker

## Overview
A lightweight desktop application for tracking Pomodoro work sessions with categorization and reporting.

## Platform
- Desktop application built with Rust + Tauri
- Cross-platform (Linux, macOS, Windows)

## Core Features

### Timer
- Configurable work duration (default: 25 minutes)
- Configurable break duration (default: 5 minutes)
- Pause/resume functionality
- Sound + desktop notification on completion

### Pomodoro Sessions
Each completed pomodoro records:
- **Name**: Free-text description of the work performed
- **Type**: Single category from the following list:
  - Product
  - Customer/Partner/Community
  - Content
  - Team
  - Social Media
  - Unqueued
  - Queued
  - Learn/Train
  - Travel
  - PTO
- **Duration**: Actual time spent
- **Timestamp**: When the session occurred

### Data Storage
- Local CSV file format
- Human-readable and manually editable
- Ability to add/edit past pomodoros through the UI

### Reporting
- Time period views: Day, Week, Month
- Breakdown by type with totals
- Visual charts and trend analysis
- CSV export functionality
