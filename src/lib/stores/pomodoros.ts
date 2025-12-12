import { writable } from "svelte/store";
import type { Pomodoro } from "../types";
import {
  getPomodoros as apiGetPomodoros,
  deletePomodoro as apiDeletePomodoro,
  updatePomodoro as apiUpdatePomodoro,
} from "../api/commands";

export const pomodoros = writable<Pomodoro[]>([]);

export async function loadPomodoros(
  startDate?: string,
  endDate?: string
): Promise<void> {
  try {
    const loaded = await apiGetPomodoros(startDate, endDate);
    pomodoros.set(loaded);
  } catch {
    pomodoros.set([]);
  }
}

export async function removePomodoro(id: string): Promise<void> {
  await apiDeletePomodoro(id);
  pomodoros.update((list) => list.filter((p) => p.id !== id));
}

export async function editPomodoro(updated: Pomodoro): Promise<void> {
  const result = await apiUpdatePomodoro(updated);
  pomodoros.update((list) =>
    list.map((p) => (p.id === result.id ? result : p))
  );
}

export function addToStore(pomodoro: Pomodoro): void {
  pomodoros.update((list) => [pomodoro, ...list]);
}
