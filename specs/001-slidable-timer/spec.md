# Feature Specification: Slidable Timer Circle

**Feature Branch**: `001-slidable-timer`
**Created**: 2025-12-27
**Status**: Draft
**Input**: Make the timer circle slidable - A user should be able to slide the timer to add more time or remove time. They should be able to slide it all the way to a couple of seconds before the end and let the time run out. The timer should have all of the same capabilities as a physical tomato timer sitting on one's desk.

## User Scenarios & Testing

### User Story 1 - Adjust Timer Duration by Dragging (Priority: P1)

A user wants to change the remaining time on a running or stopped timer by dragging the timer dial, just like twisting a physical tomato kitchen timer. They grab the timer indicator and drag clockwise to add time or counter-clockwise to reduce time.

**Why this priority**: Core feature - without the ability to drag/adjust the timer, this feature has no value. This is the primary interaction that makes the digital timer behave like a physical one.

**Independent Test**: Start a 10-minute timer, drag the indicator clockwise to add 5 minutes, verify display shows ~15 minutes remaining. Drag counter-clockwise to reduce to 3 minutes, verify display updates.

**Acceptance Scenarios**:

1. **Given** a timer is running, **When** user drags the timer indicator clockwise, **Then** remaining time increases proportionally to the drag distance
2. **Given** a timer is running, **When** user drags the timer indicator counter-clockwise, **Then** remaining time decreases proportionally to the drag distance
3. **Given** a timer is stopped at a preset duration, **When** user drags the indicator, **Then** the preset duration changes before starting
4. **Given** user is dragging the timer, **When** they release the drag, **Then** the timer continues from the new time (or remains stopped if it was stopped)

---

### User Story 2 - Drag Timer to Near-Zero Completion (Priority: P1)

A user wants to quickly end their current session by dragging the timer down to just a few seconds remaining and letting it naturally complete, triggering the completion bell and logging workflow.

**Why this priority**: Essential for the "physical timer" metaphor - users often twist physical timers to quickly end a session rather than stopping/canceling.

**Independent Test**: Start a 25-minute timer, drag counter-clockwise until only 5 seconds remain, release and wait for timer to complete, verify bell sounds and completion dialog appears.

**Acceptance Scenarios**:

1. **Given** a timer is running with significant time remaining, **When** user drags to reduce time to under 10 seconds, **Then** timer shows the reduced time and continues counting down
2. **Given** timer has been dragged to near-zero, **When** countdown reaches zero, **Then** normal completion behavior occurs (bell, notification, save dialog)
3. **Given** user drags timer, **When** they drag past zero (fully counter-clockwise), **Then** timer stops at zero and triggers completion

---

### User Story 3 - Touch and Mouse Input Support (Priority: P2)

Users on different devices (desktop with mouse, tablet/phone with touch) can interact with the timer dial using their native input method.

**Why this priority**: Important for accessibility across devices, but core functionality can be validated with mouse-only initially.

**Independent Test**: On a touch device, touch and drag the timer indicator. On desktop, click and drag with mouse. Both should adjust the timer identically.

**Acceptance Scenarios**:

1. **Given** user is on a device with mouse, **When** they click and drag the timer indicator, **Then** timer adjusts smoothly following the cursor
2. **Given** user is on a touch device, **When** they touch and drag the timer indicator, **Then** timer adjusts smoothly following the touch point
3. **Given** user is dragging, **When** they move outside the timer circle area, **Then** drag continues to work based on angle from center

---

### User Story 4 - Visual Feedback During Adjustment (Priority: P2)

While dragging, the user sees clear visual feedback showing the current time value updating in real-time, so they know exactly where they're setting the timer.

**Why this priority**: Enhances usability but timer is functional without it.

**Independent Test**: Begin dragging the timer, observe that the digital time display updates continuously as you drag.

**Acceptance Scenarios**:

1. **Given** user is actively dragging the timer, **When** they move the indicator, **Then** the time display updates in real-time to show current value
2. **Given** user is dragging, **When** the indicator passes minute boundaries, **Then** the display reflects the change immediately

---

### Edge Cases

- What happens when user drags timer while paused? Timer remains paused but duration updates; resume continues from new time.
- What happens when user drags past the maximum time (60 minutes)? Timer caps at maximum configurable duration.
- What happens when user drags to exactly zero? Timer stops and triggers completion sequence.
- What happens when user starts dragging then moves cursor/finger far away? Drag continues based on angle from timer center, not absolute position.
- What happens on very fast drags? Timer updates smoothly, no skipping or lag perceptible to user.

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow users to adjust timer duration by dragging the timer circle indicator
- **FR-002**: System MUST interpret clockwise drag as increasing time and counter-clockwise as decreasing time
- **FR-003**: System MUST update the time display in real-time while user is dragging
- **FR-004**: System MUST support both mouse drag and touch drag interactions
- **FR-005**: System MUST allow dragging the timer to near-zero (minimum 1 second) and letting it complete naturally
- **FR-006**: System MUST trigger normal completion behavior when a dragged-to-zero timer expires
- **FR-007**: System MUST cap timer adjustments at the maximum configurable duration
- **FR-008**: System MUST preserve timer state (running/paused) when duration is adjusted via drag
- **FR-009**: System MUST allow timer adjustment before starting (adjusting preset duration)

### Key Entities

- **Timer State**: Current mode (stopped, running, paused), remaining duration, total duration
- **Drag Interaction**: Start angle, current angle, drag delta translated to time change

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can adjust timer duration via drag within 100ms of interaction start (responsive feel)
- **SC-002**: Time display updates at least 10 times per second during active drag (smooth visual feedback)
- **SC-003**: 95% of users can successfully adjust timer duration on first attempt without instruction
- **SC-004**: Drag-to-complete workflow takes under 2 seconds from grab to release near zero
- **SC-005**: Timer accuracy remains within 1 second after drag adjustment (no drift introduced)

## Assumptions

- Maximum timer duration is 60 minutes (standard Pomodoro maximum)
- The timer circle already exists as a visual element that can be enhanced with drag interaction
- Clockwise = more time follows physical timer convention (winding up)
- Counter-clockwise = less time follows physical timer convention (unwinding)
