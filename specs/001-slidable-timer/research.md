# Research: Slidable Timer Circle

**Feature**: 001-slidable-timer
**Date**: 2025-12-27

## Research Questions

### 1. Best practices for circular drag interactions in vanilla JavaScript

**Decision**: Use pointer events with angle calculation from center point.

**Rationale**:
- Pointer events (`pointerdown`, `pointermove`, `pointerup`) unify mouse and touch handling
- `Math.atan2()` provides reliable angle calculation
- Tracking angle delta (not absolute position) allows intuitive drag-to-adjust

**Alternatives Considered**:
- Separate mouse/touch event handlers: More code, same result
- Third-party drag libraries: Violates constitution (no frameworks)
- CSS-based interactions: Insufficient control for time calculation

### 2. SVG coordinate transformation for drag events

**Decision**: Use `getBoundingClientRect()` to convert page coordinates to SVG-relative coordinates.

**Rationale**:
- Works reliably across viewport sizes and scroll positions
- No need for complex SVG matrix transformations
- Center point is fixed at (width/2, height/2) of bounding rect

**Alternatives Considered**:
- SVG `getScreenCTM()`: More complex, not needed for our use case
- Fixed pixel coordinates: Breaks on window resize

### 3. Time-to-angle mapping strategy

**Decision**: Map full circle (360°) to 60 minutes, with 12 o'clock as 0 minutes.

**Rationale**:
- Matches physical timer mental model (twist clockwise to add time)
- 1 degree = 10 seconds provides fine-grained control
- 12 o'clock start position is intuitive (like a clock)

**Alternatives Considered**:
- Map to current timer preset: Confusing when preset changes
- Non-linear mapping: Over-complicated for minimal benefit

### 4. Handling drag completion at zero

**Decision**: Trigger timer completion immediately when drag reaches zero.

**Rationale**:
- Matches physical timer behavior (twist to zero = ding)
- Provides immediate feedback
- Simpler than requiring release at zero

**Alternatives Considered**:
- Require explicit release at zero: Extra step, less intuitive
- Prevent reaching zero via drag: Defeats user story requirement

## Browser Compatibility

**Target browsers**: Modern evergreen browsers (Chrome, Firefox, Safari, Edge)

**Pointer events support**: All target browsers support pointer events natively.

**Fallback**: Not needed for target audience.

## Performance Considerations

- Use `requestAnimationFrame` if needed for smoother visual updates during drag
- Avoid DOM queries in hot path (cache element references)
- Update stroke-dashoffset directly, no layout recalculation needed
