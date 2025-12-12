use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settings {
    pub work_duration_minutes: u32,
    pub short_break_minutes: u32,
    pub long_break_minutes: u32,
    pub pomodoros_until_long_break: u32,
    pub sound_enabled: bool,
    pub notifications_enabled: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            work_duration_minutes: 25,
            short_break_minutes: 5,
            long_break_minutes: 15,
            pomodoros_until_long_break: 4,
            sound_enabled: true,
            notifications_enabled: true,
        }
    }
}
