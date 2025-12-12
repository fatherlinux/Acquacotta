import { writable, derived, get } from "svelte/store";
import type { TimerState, TimerStatus } from "../types";
import {
  startTimer as apiStart,
  pauseTimer as apiPause,
  resumeTimer as apiResume,
  stopTimer as apiStop,
  getTimerStatus,
  skipBreak as apiSkipBreak,
} from "../api/commands";
import { settings } from "./settings";

interface TimerStore {
  state: TimerState;
  remainingSeconds: number;
  isBreak: boolean;
  completedCount: number;
  totalSeconds: number;
}

const initialState: TimerStore = {
  state: "idle",
  remainingSeconds: 25 * 60,
  isBreak: false,
  completedCount: 0,
  totalSeconds: 25 * 60,
};

export const timer = writable<TimerStore>(initialState);

let intervalId: number | null = null;

function startLocalTick() {
  if (intervalId) return;
  intervalId = window.setInterval(() => {
    timer.update((t) => {
      if (t.state !== "running" || t.remainingSeconds <= 0) {
        return t;
      }
      return { ...t, remainingSeconds: t.remainingSeconds - 1 };
    });
  }, 1000);
}

function stopLocalTick() {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}

export const formattedTime = derived(timer, ($timer) => {
  const minutes = Math.floor($timer.remainingSeconds / 60);
  const seconds = $timer.remainingSeconds % 60;
  return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
});

export const progress = derived(timer, ($timer) => {
  if ($timer.totalSeconds === 0) return 0;
  return (($timer.totalSeconds - $timer.remainingSeconds) / $timer.totalSeconds) * 100;
});

function updateFromStatus(status: TimerStatus) {
  const currentSettings = get(settings);
  const totalSeconds = status.is_break
    ? currentSettings.short_break_minutes * 60
    : currentSettings.work_duration_minutes * 60;

  timer.set({
    state: status.state,
    remainingSeconds: status.remaining_seconds,
    isBreak: status.is_break,
    completedCount: status.completed_count,
    totalSeconds,
  });

  if (status.state === "running") {
    startLocalTick();
  } else {
    stopLocalTick();
  }
}

export async function startTimer(): Promise<void> {
  const status = await apiStart();
  updateFromStatus(status);
}

export async function pauseTimer(): Promise<void> {
  const status = await apiPause();
  updateFromStatus(status);
}

export async function resumeTimer(): Promise<void> {
  const status = await apiResume();
  updateFromStatus(status);
}

export async function stopTimer(): Promise<void> {
  const status = await apiStop();
  updateFromStatus(status);
}

export async function skipBreak(): Promise<void> {
  const status = await apiSkipBreak();
  updateFromStatus(status);
}

export async function syncTimerStatus(): Promise<void> {
  try {
    const status = await getTimerStatus();
    updateFromStatus(status);
  } catch {
    // Backend not ready, use defaults
  }
}

export function resetToIdle(): void {
  stopLocalTick();
  const currentSettings = get(settings);
  timer.set({
    state: "idle",
    remainingSeconds: currentSettings.work_duration_minutes * 60,
    isBreak: false,
    completedCount: get(timer).completedCount,
    totalSeconds: currentSettings.work_duration_minutes * 60,
  });
}
