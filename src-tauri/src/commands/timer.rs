use crate::state::{AppState, TimerState, TimerStatus};
use tauri::State;

#[tauri::command]
pub fn start_timer(state: State<AppState>) -> Result<TimerStatus, String> {
    let mut timer = state.timer.lock().map_err(|e| e.to_string())?;
    let settings = state.settings.lock().map_err(|e| e.to_string())?;

    timer.work_duration = settings.work_duration_minutes * 60;
    timer.break_duration = settings.short_break_minutes * 60;
    timer.remaining_seconds = timer.work_duration;
    timer.state = TimerState::Running;
    timer.is_break = false;

    Ok(timer.to_status())
}

#[tauri::command]
pub fn pause_timer(state: State<AppState>) -> Result<TimerStatus, String> {
    let mut timer = state.timer.lock().map_err(|e| e.to_string())?;

    if timer.state == TimerState::Running {
        timer.state = TimerState::Paused;
    }

    Ok(timer.to_status())
}

#[tauri::command]
pub fn resume_timer(state: State<AppState>) -> Result<TimerStatus, String> {
    let mut timer = state.timer.lock().map_err(|e| e.to_string())?;

    if timer.state == TimerState::Paused {
        timer.state = TimerState::Running;
    }

    Ok(timer.to_status())
}

#[tauri::command]
pub fn stop_timer(state: State<AppState>) -> Result<TimerStatus, String> {
    let mut timer = state.timer.lock().map_err(|e| e.to_string())?;
    let settings = state.settings.lock().map_err(|e| e.to_string())?;

    timer.state = TimerState::Idle;
    timer.remaining_seconds = settings.work_duration_minutes * 60;
    timer.is_break = false;

    Ok(timer.to_status())
}

#[tauri::command]
pub fn get_timer_status(state: State<AppState>) -> Result<TimerStatus, String> {
    let timer = state.timer.lock().map_err(|e| e.to_string())?;
    Ok(timer.to_status())
}

#[tauri::command]
pub fn skip_break(state: State<AppState>) -> Result<TimerStatus, String> {
    let mut timer = state.timer.lock().map_err(|e| e.to_string())?;
    let settings = state.settings.lock().map_err(|e| e.to_string())?;

    if timer.is_break {
        timer.state = TimerState::Idle;
        timer.remaining_seconds = settings.work_duration_minutes * 60;
        timer.is_break = false;
    }

    Ok(timer.to_status())
}
