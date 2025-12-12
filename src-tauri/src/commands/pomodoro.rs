use crate::models::{Pomodoro, PomodoroType};
use crate::state::AppState;
use chrono::{DateTime, Utc};
use tauri::State;

#[tauri::command]
pub fn save_pomodoro(
    name: String,
    pomodoro_type: PomodoroType,
    duration_minutes: u32,
    notes: Option<String>,
    state: State<AppState>,
) -> Result<Pomodoro, String> {
    let pomodoro = Pomodoro::new(name, pomodoro_type, duration_minutes).with_notes(notes);
    state.storage.append(&pomodoro)?;

    // Increment completed count
    if let Ok(mut timer) = state.timer.lock() {
        timer.completed_count += 1;
    }

    Ok(pomodoro)
}

#[tauri::command]
pub fn get_pomodoros(
    start_date: Option<String>,
    end_date: Option<String>,
    state: State<AppState>,
) -> Result<Vec<Pomodoro>, String> {
    let mut pomodoros = state.storage.read_all()?;

    // Filter by date range if provided
    if let Some(start) = start_date {
        if let Ok(start_dt) = start.parse::<DateTime<Utc>>() {
            pomodoros.retain(|p| p.start_time >= start_dt);
        }
    }

    if let Some(end) = end_date {
        if let Ok(end_dt) = end.parse::<DateTime<Utc>>() {
            pomodoros.retain(|p| p.start_time <= end_dt);
        }
    }

    Ok(pomodoros)
}

#[tauri::command]
pub fn update_pomodoro(pomodoro: Pomodoro, state: State<AppState>) -> Result<Pomodoro, String> {
    state.storage.update(&pomodoro)?;
    Ok(pomodoro)
}

#[tauri::command]
pub fn delete_pomodoro(id: String, state: State<AppState>) -> Result<(), String> {
    state.storage.delete(&id)
}

#[tauri::command]
pub fn add_manual_pomodoro(
    name: String,
    pomodoro_type: PomodoroType,
    start_time: String,
    end_time: String,
    duration_minutes: u32,
    notes: Option<String>,
    state: State<AppState>,
) -> Result<Pomodoro, String> {
    let start_dt: DateTime<Utc> = start_time
        .parse()
        .map_err(|e| format!("Invalid start_time: {}", e))?;
    let end_dt: DateTime<Utc> = end_time
        .parse()
        .map_err(|e| format!("Invalid end_time: {}", e))?;

    let pomodoro = Pomodoro::manual(name, pomodoro_type, start_dt, end_dt, duration_minutes, notes);
    state.storage.append(&pomodoro)?;

    Ok(pomodoro)
}
