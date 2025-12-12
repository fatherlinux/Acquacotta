import { invoke } from "@tauri-apps/api/core";
import type {
  Pomodoro,
  PomodoroType,
  Settings,
  TimerStatus,
  ReportData,
} from "../types";

// Timer commands
export async function startTimer(): Promise<TimerStatus> {
  return invoke("start_timer");
}

export async function pauseTimer(): Promise<TimerStatus> {
  return invoke("pause_timer");
}

export async function resumeTimer(): Promise<TimerStatus> {
  return invoke("resume_timer");
}

export async function stopTimer(): Promise<TimerStatus> {
  return invoke("stop_timer");
}

export async function getTimerStatus(): Promise<TimerStatus> {
  return invoke("get_timer_status");
}

export async function skipBreak(): Promise<TimerStatus> {
  return invoke("skip_break");
}

// Pomodoro CRUD commands
export async function savePomodoro(
  name: string,
  pomodoroType: PomodoroType,
  durationMinutes: number,
  notes?: string
): Promise<Pomodoro> {
  return invoke("save_pomodoro", {
    name,
    pomodoroType,
    durationMinutes,
    notes,
  });
}

export async function getPomodoros(
  startDate?: string,
  endDate?: string
): Promise<Pomodoro[]> {
  return invoke("get_pomodoros", { startDate, endDate });
}

export async function updatePomodoro(pomodoro: Pomodoro): Promise<Pomodoro> {
  return invoke("update_pomodoro", { pomodoro });
}

export async function deletePomodoro(id: string): Promise<void> {
  return invoke("delete_pomodoro", { id });
}

export async function addManualPomodoro(
  name: string,
  pomodoroType: PomodoroType,
  startTime: string,
  endTime: string,
  durationMinutes: number,
  notes?: string
): Promise<Pomodoro> {
  return invoke("add_manual_pomodoro", {
    name,
    pomodoroType,
    startTime,
    endTime,
    durationMinutes,
    notes,
  });
}

// Settings commands
export async function getSettings(): Promise<Settings> {
  return invoke("get_settings");
}

export async function saveSettings(settings: Settings): Promise<void> {
  return invoke("save_settings", { settings });
}

// Export commands
export async function exportPomodoros(
  startDate?: string,
  endDate?: string,
  exportPath?: string
): Promise<string> {
  return invoke("export_pomodoros", { startDate, endDate, exportPath });
}

export async function getReportData(
  period: "day" | "week" | "month",
  date: string
): Promise<ReportData> {
  return invoke("get_report_data", { period, date });
}
