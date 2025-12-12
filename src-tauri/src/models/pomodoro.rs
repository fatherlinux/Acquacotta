use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum PomodoroType {
    Product,
    #[serde(rename = "Customer/Partner/Community")]
    CustomerPartnerCommunity,
    Content,
    Team,
    #[serde(rename = "Social Media")]
    SocialMedia,
    Unqueued,
    Queued,
    #[serde(rename = "Learn/Train")]
    LearnTrain,
    Travel,
    PTO,
}

impl std::fmt::Display for PomodoroType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            PomodoroType::Product => write!(f, "Product"),
            PomodoroType::CustomerPartnerCommunity => write!(f, "Customer/Partner/Community"),
            PomodoroType::Content => write!(f, "Content"),
            PomodoroType::Team => write!(f, "Team"),
            PomodoroType::SocialMedia => write!(f, "Social Media"),
            PomodoroType::Unqueued => write!(f, "Unqueued"),
            PomodoroType::Queued => write!(f, "Queued"),
            PomodoroType::LearnTrain => write!(f, "Learn/Train"),
            PomodoroType::Travel => write!(f, "Travel"),
            PomodoroType::PTO => write!(f, "PTO"),
        }
    }
}

impl std::str::FromStr for PomodoroType {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "Product" => Ok(PomodoroType::Product),
            "Customer/Partner/Community" => Ok(PomodoroType::CustomerPartnerCommunity),
            "Content" => Ok(PomodoroType::Content),
            "Team" => Ok(PomodoroType::Team),
            "Social Media" => Ok(PomodoroType::SocialMedia),
            "Unqueued" => Ok(PomodoroType::Unqueued),
            "Queued" => Ok(PomodoroType::Queued),
            "Learn/Train" => Ok(PomodoroType::LearnTrain),
            "Travel" => Ok(PomodoroType::Travel),
            "PTO" => Ok(PomodoroType::PTO),
            _ => Err(format!("Unknown pomodoro type: {}", s)),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Pomodoro {
    pub id: String,
    pub name: String,
    pub pomodoro_type: PomodoroType,
    pub start_time: DateTime<Utc>,
    pub end_time: DateTime<Utc>,
    pub duration_minutes: u32,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

impl Pomodoro {
    pub fn new(name: String, pomodoro_type: PomodoroType, duration_minutes: u32) -> Self {
        let end_time = Utc::now();
        let start_time = end_time - chrono::Duration::minutes(duration_minutes as i64);
        Self {
            id: Uuid::new_v4().to_string(),
            name,
            pomodoro_type,
            start_time,
            end_time,
            duration_minutes,
            notes: None,
        }
    }

    pub fn with_notes(mut self, notes: Option<String>) -> Self {
        self.notes = notes;
        self
    }

    pub fn manual(
        name: String,
        pomodoro_type: PomodoroType,
        start_time: DateTime<Utc>,
        end_time: DateTime<Utc>,
        duration_minutes: u32,
        notes: Option<String>,
    ) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            name,
            pomodoro_type,
            start_time,
            end_time,
            duration_minutes,
            notes,
        }
    }
}
