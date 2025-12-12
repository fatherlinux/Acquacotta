use crate::models::Settings;
use crate::state::AppState;
use tauri::State;

#[tauri::command]
pub fn get_settings(state: State<AppState>) -> Result<Settings, String> {
    let settings = state.settings.lock().map_err(|e| e.to_string())?;
    Ok(settings.clone())
}

#[tauri::command]
pub fn save_settings(settings: Settings, state: State<AppState>) -> Result<(), String> {
    let mut current = state.settings.lock().map_err(|e| e.to_string())?;
    *current = settings;

    // Update timer durations
    if let Ok(mut timer) = state.timer.lock() {
        timer.work_duration = current.work_duration_minutes * 60;
        timer.break_duration = current.short_break_minutes * 60;
    }

    Ok(())
}
