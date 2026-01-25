# Implementation Plan: Slidable Timer Circle

**Branch**: `001-slidable-timer` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-slidable-timer/spec.md`

## Summary

Add drag-to-adjust functionality to the existing SVG timer circle, allowing users to increase or decrease remaining time by dragging clockwise or counter-clockwise, mimicking a physical tomato kitchen timer. The implementation is frontend-only, modifying the existing vanilla JavaScript timer logic in `templates/index.html`.

## Technical Context

**Language/Version**: JavaScript (ES6+), embedded in HTML
**Primary Dependencies**: None (vanilla JS, no frameworks per constitution)
**Storage**: N/A (timer state is in-memory only)
**Testing**: Manual browser testing
**Target Platform**: Modern browsers (desktop + mobile)
**Project Type**: Web application (monolithic Flask + vanilla JS)
**Performance Goals**: <100ms response to drag, 10+ FPS visual updates during drag
**Constraints**: Must work offline, no external libraries, touch + mouse support
**Scale/Scope**: Single-file change to `templates/index.html`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy by Design | PASS | No data collection, purely local UI interaction |
| II. User Data Ownership | PASS | No data storage changes |
| III. Simplicity & Focus | PASS | Directly enhances timer control, core Pomodoro functionality |
| IV. Timer Agnosticism | PASS | Makes digital timer behave like physical timer |
| V. Offline-First | PASS | Pure frontend, works without network |
| VI. Container-Ready | PASS | No deployment changes |

## Project Structure

### Documentation (this feature)

```text
specs/001-slidable-timer/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal - no new entities)
├── quickstart.md        # Phase 1 output
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
templates/
└── index.html           # Single file to modify - timer UI and JavaScript
```

**Structure Decision**: Single-file modification. The existing `index.html` contains all timer logic inline. New drag interaction code will be added to the existing JavaScript section, following the established pattern.

## Complexity Tracking

No constitution violations. Single-file change with no new dependencies.

## Architecture Overview

### Current Timer State Model

```
Timer State Variables (existing):
├── timerState: 'idle' | 'running' | 'paused'
├── remainingSeconds: number
├── totalSeconds: number
├── isBreak: boolean
└── timerInterval: setInterval handle

SVG Elements (existing):
├── svg.timer-ring (viewBox="0 0 280 280")
├── circle.timer-ring-bg (cx=140, cy=140, r=120)
├── circle#timer-progress (stroke-dasharray=754, stroke-dashoffset=0-754)
└── div.timer-text > div#timer-time
```

### New Drag Interaction Model

```
Drag State (new):
├── isDragging: boolean
├── dragStartAngle: number (radians)
└── dragStartSeconds: number

Event Flow:
mousedown/touchstart on timer-ring
  → Calculate angle from center
  → Set isDragging = true
  → Store dragStartAngle, dragStartSeconds

mousemove/touchmove (global)
  → If isDragging: calculate new angle
  → Compute delta angle → delta seconds
  → Update remainingSeconds (clamped 0 to maxDuration)
  → Call updateTimerDisplay()

mouseup/touchend (global)
  → Set isDragging = false
  → If remainingSeconds <= 0: trigger completion
```

### Angle-to-Time Mapping

- Full circle (360°) = 60 minutes (max duration)
- 1 degree = 10 seconds
- Clockwise rotation = increase time
- Counter-clockwise rotation = decrease time
- Center point: (140, 140) in SVG coordinates

## Key Implementation Decisions

1. **Event attachment**: Attach mousedown/touchstart to the SVG element, but mousemove/mouseup to document to handle drag outside the circle.

2. **Angle calculation**: Use `Math.atan2(y - centerY, x - centerX)` to get angle in radians, convert to degrees for time mapping.

3. **Time clamping**: Minimum 0 seconds (triggers completion), maximum from settings (default 60 minutes).

4. **Visual feedback**: Reuse existing `updateTimerDisplay()` function during drag for consistent appearance.

5. **State preservation**: Dragging while paused keeps timer paused; dragging while running keeps it running.

6. **Touch handling**: Use `touch.clientX/clientY` from `touches[0]` for touch events.

## API Contracts

No backend API changes. This is a frontend-only feature.

## Data Model Changes

No database or storage changes. Timer state remains in-memory JavaScript variables.
