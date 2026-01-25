# Tasks: Slidable Timer Circle

**Input**: Design documents from `/specs/001-slidable-timer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Manual browser testing only (no automated tests requested)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single file change**: All modifications in `templates/index.html`

---

## Phase 1: Setup (Foundational Code)

**Purpose**: Add drag state variables and utility functions needed by all user stories

- [x] T001 Add drag state variables (isDragging, dragStartAngle, dragStartSeconds) to JavaScript section in templates/index.html
- [x] T002 Add getTimerCenter() function to calculate SVG center point relative to viewport in templates/index.html
- [x] T003 Add getAngleFromPoint(x, y) function using Math.atan2 for angle calculation in templates/index.html
- [x] T004 Add angleToSeconds(angleDelta) function to convert angle change to time change in templates/index.html

**Checkpoint**: ✅ Foundation ready - utility functions in place for drag implementation

---

## Phase 2: User Story 1 - Adjust Timer Duration by Dragging (Priority: P1) 🎯 MVP

**Goal**: User can drag the timer circle to increase or decrease remaining time

**Independent Test**: Start a 10-minute timer, drag clockwise to add 5 minutes, verify display shows ~15 minutes. Drag counter-clockwise to reduce to 3 minutes, verify display updates.

### Implementation for User Story 1

- [x] T005 [US1] Add pointerdown event listener to timer-ring SVG element in templates/index.html
- [x] T006 [US1] Implement handleDragStart() function to capture initial angle and remaining seconds in templates/index.html
- [x] T007 [US1] Add pointermove event listener on document for drag tracking in templates/index.html
- [x] T008 [US1] Implement handleDragMove() function to calculate new remainingSeconds from angle delta in templates/index.html
- [x] T009 [US1] Add pointerup event listener on document to end drag in templates/index.html
- [x] T010 [US1] Implement handleDragEnd() function to finalize drag interaction in templates/index.html
- [x] T011 [US1] Add time clamping logic: minimum 0 seconds, maximum 60 minutes (3600 seconds) in templates/index.html
- [x] T012 [US1] Update totalSeconds when adjusting idle timer (before start) in templates/index.html

**Checkpoint**: ✅ User Story 1 complete - basic drag to adjust works with mouse

---

## Phase 3: User Story 2 - Drag Timer to Near-Zero Completion (Priority: P1)

**Goal**: User can drag timer to near-zero and let it complete naturally, triggering the bell

**Independent Test**: Start a 25-minute timer, drag counter-clockwise until only 5 seconds remain, release and wait for timer to complete, verify bell sounds and completion dialog appears.

### Implementation for User Story 2

- [x] T013 [US2] Add zero-crossing detection in handleDragMove() to trigger immediate completion in templates/index.html
- [x] T014 [US2] Call timerComplete() or breakComplete() when drag reaches zero in templates/index.html
- [x] T015 [US2] Ensure completion sequence works correctly after drag-to-zero (bell, notification, save dialog) in templates/index.html

**Checkpoint**: ✅ User Story 2 complete - drag to zero triggers completion

---

## Phase 4: User Story 3 - Touch and Mouse Input Support (Priority: P2)

**Goal**: Timer drag works on both desktop (mouse) and mobile (touch) devices

**Independent Test**: On a touch device, touch and drag the timer indicator. On desktop, click and drag with mouse. Both should adjust the timer identically.

### Implementation for User Story 3

- [x] T016 [US3] Add touch-action: none CSS to timer-ring to prevent browser gestures in templates/index.html
- [x] T017 [US3] Ensure pointer events work with touch by adding touch-action CSS property in templates/index.html
- [x] T018 [US3] Add setPointerCapture() in handleDragStart() for reliable drag tracking in templates/index.html
- [x] T019 [US3] Add releasePointerCapture() in handleDragEnd() to clean up in templates/index.html
- [x] T020 [US3] Test and fix any touch-specific edge cases (e.g., multi-touch ignored) in templates/index.html

**Checkpoint**: ✅ User Story 3 complete - touch and mouse both work

---

## Phase 5: User Story 4 - Visual Feedback During Adjustment (Priority: P2)

**Goal**: Time display updates smoothly in real-time while user drags

**Independent Test**: Begin dragging the timer, observe that the digital time display updates continuously as you drag.

### Implementation for User Story 4

- [x] T021 [US4] Call updateTimerDisplay() in handleDragMove() for real-time visual feedback in templates/index.html
- [x] T022 [US4] Ensure smooth visual updates by avoiding unnecessary DOM queries in drag loop in templates/index.html
- [x] T023 [US4] Add cursor style change (grab/grabbing) during drag for visual affordance in templates/index.html

**Checkpoint**: ✅ User Story 4 complete - smooth visual feedback during drag

---

## Phase 6: Polish & Edge Cases

**Purpose**: Handle edge cases and improve robustness

- [x] T024 Handle drag while timer is paused - maintain paused state but update duration in templates/index.html
- [x] T025 Handle drag outside timer circle - continue tracking based on angle from center in templates/index.html
- [x] T026 Prevent text selection during drag by adding user-select: none CSS in templates/index.html
- [ ] T027 Validate against quickstart.md test scenarios in templates/index.html
- [ ] T028 Test on mobile browser (Chrome/Safari iOS/Android) to verify touch works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ Complete
- **User Story 1 (Phase 2)**: ✅ Complete
- **User Story 2 (Phase 3)**: ✅ Complete
- **User Story 3 (Phase 4)**: ✅ Complete
- **User Story 4 (Phase 5)**: ✅ Complete
- **Polish (Phase 6)**: 🔄 In Progress (manual testing remaining)

### Task Dependencies Within Phases

**Phase 1 (Setup)**:
- T001 → T002 → T003 → T004 (sequential, each builds on previous)

**Phase 2 (US1)**:
- T005, T007, T009 (event listeners) can be done together
- T006, T008, T010 (handlers) depend on corresponding listeners
- T011, T012 (clamping, idle mode) can be done after T008

**Phase 3-5**:
- All depend on Phase 2 completion
- Within each phase, tasks are sequential (same file modifications)

### Parallel Opportunities

Since all tasks modify the same file (`templates/index.html`), true parallelism is limited. However:

- User Stories 3 and 4 can be developed in separate branches and merged after US1/US2 are complete
- Polish tasks (T024-T028) are independent of each other once US1-4 complete

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. ✅ Complete Phase 1: Setup (4 tasks)
2. ✅ Complete Phase 2: User Story 1 (8 tasks)
3. ✅ Complete Phase 3: User Story 2 (3 tasks)
4. **STOP and VALIDATE**: Test basic drag functionality with mouse
5. Deploy/demo if ready - core value delivered

### Full Feature

1. ✅ Complete MVP (Phases 1-3)
2. ✅ Add Phase 4: Touch support (5 tasks)
3. ✅ Add Phase 5: Visual polish (3 tasks)
4. 🔄 Complete Phase 6: Edge cases (3/5 tasks done)
5. Final testing per quickstart.md

---

## Summary

| Metric | Count | Completed |
|--------|-------|-----------|
| Total Tasks | 28 | 26 |
| Setup Tasks | 4 | 4 |
| User Story 1 (P1) | 8 | 8 |
| User Story 2 (P1) | 3 | 3 |
| User Story 3 (P2) | 5 | 5 |
| User Story 4 (P2) | 3 | 3 |
| Polish Tasks | 5 | 3 |
| Files Modified | 1 (templates/index.html) | ✅ |

**MVP Scope**: ✅ Phases 1-3 complete - core drag-to-adjust functionality delivered

---

## Notes

- All modifications in single file: `templates/index.html`
- No backend changes required
- Manual testing only (per plan.md)
- Commit after each phase checkpoint
- Test on both desktop and mobile before merging
- **Remaining**: T027, T028 require manual browser testing
