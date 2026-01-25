# Data Model: Slidable Timer Circle

**Feature**: 001-slidable-timer
**Date**: 2025-12-27

## Overview

This feature introduces no new persistent data entities. All state is transient and exists only in JavaScript memory during the browser session.

## New State Variables

Added to existing timer JavaScript scope:

| Variable | Type | Description |
|----------|------|-------------|
| `isDragging` | boolean | True while user is actively dragging the timer circle |
| `dragStartAngle` | number | Angle (radians) at drag start, used to calculate delta |
| `dragStartSeconds` | number | `remainingSeconds` value at drag start |

## Modified Behavior

### Existing Variables (no schema change)

| Variable | Modification |
|----------|-------------|
| `remainingSeconds` | Now also updated by drag interaction (was only updated by interval) |
| `totalSeconds` | May be updated when adjusting idle timer preset via drag |

## Relationships

```
User Drag Input
    │
    ├─► isDragging (new)
    │       │
    │       ▼
    ├─► dragStartAngle (new) ──► delta calculation
    │       │
    │       ▼
    └─► dragStartSeconds (new) ──► remainingSeconds (existing)
                                        │
                                        ▼
                                   updateTimerDisplay() (existing)
```

## Validation Rules

- `remainingSeconds` clamped to [0, maxDuration * 60]
- `maxDuration` from settings (default 60 minutes)
- Drag to 0 triggers completion sequence
