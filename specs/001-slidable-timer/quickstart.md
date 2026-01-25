# Quickstart: Slidable Timer Circle

**Feature**: 001-slidable-timer
**Date**: 2025-12-27

## Prerequisites

- Python 3.x installed
- Google OAuth credentials configured (or test offline)

## Running the Application

```bash
# From repository root
python app.py

# Open in browser
open http://localhost:5000
```

## Testing the Slidable Timer

### Test 1: Basic Drag to Increase Time

1. Open the Timer view (default view)
2. Click and hold on the timer circle (the colored ring)
3. Drag clockwise (to the right, then down)
4. Observe: Time display increases as you drag
5. Release: Timer shows new duration

**Expected**: Smooth visual feedback, time increases proportionally

### Test 2: Drag to Decrease Time

1. Start a timer (click any preset, then Start)
2. Click and hold on the timer circle
3. Drag counter-clockwise (to the left, then up)
4. Observe: Remaining time decreases
5. Release: Timer continues from new time

**Expected**: Timer keeps running at reduced time

### Test 3: Drag to Zero (Quick Complete)

1. Start a 5-minute timer
2. Drag counter-clockwise all the way to zero
3. Observe: Timer reaches 0:00

**Expected**: Bell sounds, completion dialog appears

### Test 4: Touch Interaction (Mobile/Tablet)

1. Open on touch device or use browser DevTools device emulation
2. Touch and drag on timer circle
3. Verify same behavior as mouse

**Expected**: Touch drag works identically to mouse drag

### Test 5: Drag While Paused

1. Start timer, then click Pause
2. Drag to adjust time
3. Click Resume

**Expected**: Timer resumes from adjusted time, stays paused during drag

### Test 6: Drag Before Starting

1. With timer idle (showing preset duration)
2. Drag to adjust the preset
3. Click Start

**Expected**: Timer starts from dragged duration

## Troubleshooting

**Drag not working?**
- Ensure you're dragging on the colored ring, not the center text
- Try refreshing the page
- Check browser console for JavaScript errors

**Time jumping erratically?**
- Move mouse/finger more slowly
- Ensure you're not double-clicking

**Touch not working?**
- Verify touch events are not blocked by other UI elements
- Try disabling browser gestures (pinch-to-zoom) temporarily
