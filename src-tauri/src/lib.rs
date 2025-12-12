mod commands;
mod models;
mod state;
mod storage;

use state::AppState;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let state = AppState::new(app.handle().clone());
            app.manage(state);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Timer commands
            commands::timer::start_timer,
            commands::timer::pause_timer,
            commands::timer::resume_timer,
            commands::timer::stop_timer,
            commands::timer::get_timer_status,
            commands::timer::skip_break,
            // Pomodoro commands
            commands::pomodoro::save_pomodoro,
            commands::pomodoro::get_pomodoros,
            commands::pomodoro::update_pomodoro,
            commands::pomodoro::delete_pomodoro,
            commands::pomodoro::add_manual_pomodoro,
            // Settings commands
            commands::settings::get_settings,
            commands::settings::save_settings,
            // Export commands
            commands::export::export_pomodoros,
            commands::export::get_report_data,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
