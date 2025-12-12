use crate::models::Settings;
use crate::storage::CsvStorage;
use std::path::PathBuf;
use std::sync::Mutex;
use tauri::AppHandle;

#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TimerState {
    Idle,
    Running,
    Paused,
    Break,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct TimerStatus {
    pub state: TimerState,
    pub remaining_seconds: u32,
    pub is_break: bool,
    pub completed_count: u32,
}

pub struct TimerData {
    pub state: TimerState,
    pub remaining_seconds: u32,
    pub is_break: bool,
    pub completed_count: u32,
    pub work_duration: u32,
    pub break_duration: u32,
}

impl Default for TimerData {
    fn default() -> Self {
        Self {
            state: TimerState::Idle,
            remaining_seconds: 25 * 60,
            is_break: false,
            completed_count: 0,
            work_duration: 25 * 60,
            break_duration: 5 * 60,
        }
    }
}

impl TimerData {
    pub fn to_status(&self) -> TimerStatus {
        TimerStatus {
            state: self.state,
            remaining_seconds: self.remaining_seconds,
            is_break: self.is_break,
            completed_count: self.completed_count,
        }
    }
}

pub struct AppState {
    pub timer: Mutex<TimerData>,
    pub settings: Mutex<Settings>,
    pub storage: CsvStorage,
    pub data_dir: PathBuf,
}

impl AppState {
    pub fn new(app: AppHandle) -> Self {
        let data_dir = dirs::data_dir()
            .unwrap_or_else(|| PathBuf::from("."))
            .join("acquacotta");

        std::fs::create_dir_all(&data_dir).ok();

        let csv_path = data_dir.join("pomodoros.csv");
        let storage = CsvStorage::new(csv_path);

        Self {
            timer: Mutex::new(TimerData::default()),
            settings: Mutex::new(Settings::default()),
            storage,
            data_dir,
        }
    }
}
