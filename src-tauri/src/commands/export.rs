use crate::models::PomodoroType;
use crate::state::AppState;
use chrono::{Datelike, Duration, NaiveDate, TimeZone, Utc};
use serde::Serialize;
use std::collections::HashMap;
use tauri::State;

#[derive(Debug, Serialize)]
pub struct ReportData {
    pub period: String,
    pub total_minutes: u32,
    pub total_pomodoros: u32,
    pub by_type: HashMap<String, u32>,
    pub daily_totals: Vec<DailyTotal>,
}

#[derive(Debug, Serialize)]
pub struct DailyTotal {
    pub date: String,
    pub minutes: u32,
    pub count: u32,
}

#[tauri::command]
pub fn export_pomodoros(
    start_date: Option<String>,
    end_date: Option<String>,
    export_path: Option<String>,
    state: State<AppState>,
) -> Result<String, String> {
    let path = if let Some(p) = export_path {
        std::path::PathBuf::from(p)
    } else {
        let timestamp = Utc::now().format("%Y%m%d_%H%M%S");
        state.data_dir.join(format!("export_{}.csv", timestamp))
    };

    state.storage.export_to(&path)?;

    Ok(path.to_string_lossy().to_string())
}

#[tauri::command]
pub fn get_report_data(
    period: String,
    date: String,
    state: State<AppState>,
) -> Result<ReportData, String> {
    let reference_date = NaiveDate::parse_from_str(&date, "%Y-%m-%d")
        .map_err(|e| format!("Invalid date format: {}", e))?;

    let (start_date, end_date, dates) = match period.as_str() {
        "day" => {
            let start = Utc.from_utc_datetime(
                &reference_date
                    .and_hms_opt(0, 0, 0)
                    .ok_or("Invalid time")?,
            );
            let end = start + Duration::days(1);
            let dates = vec![reference_date];
            (start, end, dates)
        }
        "week" => {
            let days_from_sunday = reference_date.weekday().num_days_from_sunday();
            let week_start = reference_date - Duration::days(days_from_sunday as i64);
            let start = Utc.from_utc_datetime(
                &week_start.and_hms_opt(0, 0, 0).ok_or("Invalid time")?,
            );
            let end = start + Duration::days(7);
            let dates: Vec<NaiveDate> = (0..7).map(|i| week_start + Duration::days(i)).collect();
            (start, end, dates)
        }
        "month" => {
            let month_start = NaiveDate::from_ymd_opt(reference_date.year(), reference_date.month(), 1)
                .ok_or("Invalid date")?;
            let next_month = if reference_date.month() == 12 {
                NaiveDate::from_ymd_opt(reference_date.year() + 1, 1, 1)
            } else {
                NaiveDate::from_ymd_opt(reference_date.year(), reference_date.month() + 1, 1)
            }
            .ok_or("Invalid date")?;

            let start = Utc.from_utc_datetime(
                &month_start.and_hms_opt(0, 0, 0).ok_or("Invalid time")?,
            );
            let end = Utc.from_utc_datetime(
                &next_month.and_hms_opt(0, 0, 0).ok_or("Invalid time")?,
            );

            let days_in_month = (next_month - month_start).num_days();
            let dates: Vec<NaiveDate> = (0..days_in_month)
                .map(|i| month_start + Duration::days(i))
                .collect();
            (start, end, dates)
        }
        _ => return Err("Invalid period. Use 'day', 'week', or 'month'".to_string()),
    };

    let pomodoros = state.storage.read_all()?;
    let filtered: Vec<_> = pomodoros
        .iter()
        .filter(|p| p.start_time >= start_date && p.start_time < end_date)
        .collect();

    let total_minutes: u32 = filtered.iter().map(|p| p.duration_minutes).sum();
    let total_pomodoros = filtered.len() as u32;

    // Group by type
    let mut by_type: HashMap<String, u32> = HashMap::new();
    for ptype in [
        PomodoroType::Product,
        PomodoroType::CustomerPartnerCommunity,
        PomodoroType::Content,
        PomodoroType::Team,
        PomodoroType::SocialMedia,
        PomodoroType::Unqueued,
        PomodoroType::Queued,
        PomodoroType::LearnTrain,
        PomodoroType::Travel,
        PomodoroType::PTO,
    ] {
        by_type.insert(ptype.to_string(), 0);
    }
    for p in &filtered {
        *by_type.entry(p.pomodoro_type.to_string()).or_insert(0) += p.duration_minutes;
    }

    // Daily totals
    let daily_totals: Vec<DailyTotal> = dates
        .iter()
        .map(|d| {
            let day_pomodoros: Vec<_> = filtered
                .iter()
                .filter(|p| p.start_time.date_naive() == *d)
                .collect();
            DailyTotal {
                date: d.to_string(),
                minutes: day_pomodoros.iter().map(|p| p.duration_minutes).sum(),
                count: day_pomodoros.len() as u32,
            }
        })
        .collect();

    Ok(ReportData {
        period,
        total_minutes,
        total_pomodoros,
        by_type,
        daily_totals,
    })
}
