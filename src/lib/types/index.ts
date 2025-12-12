export type PomodoroType =
  | "Product"
  | "Customer/Partner/Community"
  | "Content"
  | "Team"
  | "Social Media"
  | "Unqueued"
  | "Queued"
  | "Learn/Train"
  | "Travel"
  | "PTO";

export const POMODORO_TYPES: PomodoroType[] = [
  "Product",
  "Customer/Partner/Community",
  "Content",
  "Team",
  "Social Media",
  "Unqueued",
  "Queued",
  "Learn/Train",
  "Travel",
  "PTO",
];

export interface Pomodoro {
  id: string;
  name: string;
  pomodoro_type: PomodoroType;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  notes?: string;
}

export interface Settings {
  work_duration_minutes: number;
  short_break_minutes: number;
  long_break_minutes: number;
  pomodoros_until_long_break: number;
  sound_enabled: boolean;
  notifications_enabled: boolean;
}

export type TimerState = "idle" | "running" | "paused" | "break";

export interface TimerStatus {
  state: TimerState;
  remaining_seconds: number;
  is_break: boolean;
  completed_count: number;
}

export interface ReportData {
  period: string;
  total_minutes: number;
  total_pomodoros: number;
  by_type: Record<PomodoroType, number>;
  daily_totals: Array<{ date: string; minutes: number; count: number }>;
}

export const TYPE_COLORS: Record<PomodoroType, string> = {
  Product: "#e94560",
  "Customer/Partner/Community": "#4ecca3",
  Content: "#ffc93c",
  Team: "#a855f7",
  "Social Media": "#3b82f6",
  Unqueued: "#6b7280",
  Queued: "#8b5cf6",
  "Learn/Train": "#10b981",
  Travel: "#f97316",
  PTO: "#06b6d4",
};
