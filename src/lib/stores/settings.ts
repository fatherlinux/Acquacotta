import { writable } from "svelte/store";
import type { Settings } from "../types";
import { getSettings, saveSettings as apiSaveSettings } from "../api/commands";

const defaultSettings: Settings = {
  work_duration_minutes: 25,
  short_break_minutes: 5,
  long_break_minutes: 15,
  pomodoros_until_long_break: 4,
  sound_enabled: true,
  notifications_enabled: true,
};

export const settings = writable<Settings>(defaultSettings);

export async function loadSettings(): Promise<void> {
  try {
    const loaded = await getSettings();
    settings.set(loaded);
  } catch {
    settings.set(defaultSettings);
  }
}

export async function updateSettings(newSettings: Settings): Promise<void> {
  await apiSaveSettings(newSettings);
  settings.set(newSettings);
}
