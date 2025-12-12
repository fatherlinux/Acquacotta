use crate::models::{Pomodoro, PomodoroType};
use chrono::{DateTime, Utc};
use std::fs::{File, OpenOptions};
use std::io::{BufReader, BufWriter};
use std::path::PathBuf;

pub struct CsvStorage {
    path: PathBuf,
}

#[derive(Debug, serde::Deserialize, serde::Serialize)]
struct CsvRecord {
    id: String,
    name: String,
    #[serde(rename = "type")]
    pomodoro_type: String,
    start_time: String,
    end_time: String,
    duration_minutes: u32,
    #[serde(default)]
    notes: String,
}

impl From<&Pomodoro> for CsvRecord {
    fn from(p: &Pomodoro) -> Self {
        CsvRecord {
            id: p.id.clone(),
            name: p.name.clone(),
            pomodoro_type: p.pomodoro_type.to_string(),
            start_time: p.start_time.to_rfc3339(),
            end_time: p.end_time.to_rfc3339(),
            duration_minutes: p.duration_minutes,
            notes: p.notes.clone().unwrap_or_default(),
        }
    }
}

impl TryFrom<CsvRecord> for Pomodoro {
    type Error = String;

    fn try_from(r: CsvRecord) -> Result<Self, Self::Error> {
        let pomodoro_type: PomodoroType = r.pomodoro_type.parse()?;
        let start_time: DateTime<Utc> = r
            .start_time
            .parse()
            .map_err(|e| format!("Invalid start_time: {}", e))?;
        let end_time: DateTime<Utc> = r
            .end_time
            .parse()
            .map_err(|e| format!("Invalid end_time: {}", e))?;

        Ok(Pomodoro {
            id: r.id,
            name: r.name,
            pomodoro_type,
            start_time,
            end_time,
            duration_minutes: r.duration_minutes,
            notes: if r.notes.is_empty() {
                None
            } else {
                Some(r.notes)
            },
        })
    }
}

impl CsvStorage {
    pub fn new(path: PathBuf) -> Self {
        Self { path }
    }

    pub fn ensure_file_exists(&self) -> Result<(), String> {
        if !self.path.exists() {
            if let Some(parent) = self.path.parent() {
                std::fs::create_dir_all(parent)
                    .map_err(|e| format!("Failed to create directory: {}", e))?;
            }
            let file =
                File::create(&self.path).map_err(|e| format!("Failed to create file: {}", e))?;
            let mut writer = csv::Writer::from_writer(BufWriter::new(file));
            writer
                .write_record([
                    "id",
                    "name",
                    "type",
                    "start_time",
                    "end_time",
                    "duration_minutes",
                    "notes",
                ])
                .map_err(|e| format!("Failed to write header: {}", e))?;
            writer
                .flush()
                .map_err(|e| format!("Failed to flush: {}", e))?;
        }
        Ok(())
    }

    pub fn read_all(&self) -> Result<Vec<Pomodoro>, String> {
        self.ensure_file_exists()?;

        let file =
            File::open(&self.path).map_err(|e| format!("Failed to open file: {}", e))?;
        let reader = BufReader::new(file);
        let mut csv_reader = csv::Reader::from_reader(reader);

        let mut pomodoros = Vec::new();
        for result in csv_reader.deserialize() {
            let record: CsvRecord =
                result.map_err(|e| format!("Failed to read record: {}", e))?;
            let pomodoro = Pomodoro::try_from(record)?;
            pomodoros.push(pomodoro);
        }

        // Sort by start_time descending (most recent first)
        pomodoros.sort_by(|a, b| b.start_time.cmp(&a.start_time));

        Ok(pomodoros)
    }

    pub fn append(&self, pomodoro: &Pomodoro) -> Result<(), String> {
        self.ensure_file_exists()?;

        let file = OpenOptions::new()
            .append(true)
            .open(&self.path)
            .map_err(|e| format!("Failed to open file: {}", e))?;

        let mut writer = csv::WriterBuilder::new()
            .has_headers(false)
            .from_writer(BufWriter::new(file));

        let record = CsvRecord::from(pomodoro);
        writer
            .serialize(record)
            .map_err(|e| format!("Failed to write record: {}", e))?;
        writer
            .flush()
            .map_err(|e| format!("Failed to flush: {}", e))?;

        Ok(())
    }

    pub fn update(&self, pomodoro: &Pomodoro) -> Result<(), String> {
        let mut pomodoros = self.read_all()?;
        if let Some(pos) = pomodoros.iter().position(|p| p.id == pomodoro.id) {
            pomodoros[pos] = pomodoro.clone();
            self.write_all(&pomodoros)?;
        }
        Ok(())
    }

    pub fn delete(&self, id: &str) -> Result<(), String> {
        let pomodoros: Vec<Pomodoro> = self
            .read_all()?
            .into_iter()
            .filter(|p| p.id != id)
            .collect();
        self.write_all(&pomodoros)
    }

    fn write_all(&self, pomodoros: &[Pomodoro]) -> Result<(), String> {
        let file =
            File::create(&self.path).map_err(|e| format!("Failed to create file: {}", e))?;
        let mut writer = csv::Writer::from_writer(BufWriter::new(file));

        for pomodoro in pomodoros {
            let record = CsvRecord::from(pomodoro);
            writer
                .serialize(record)
                .map_err(|e| format!("Failed to write record: {}", e))?;
        }

        writer
            .flush()
            .map_err(|e| format!("Failed to flush: {}", e))?;

        Ok(())
    }

    pub fn export_to(&self, path: &PathBuf) -> Result<(), String> {
        let pomodoros = self.read_all()?;
        let file =
            File::create(path).map_err(|e| format!("Failed to create export file: {}", e))?;
        let mut writer = csv::Writer::from_writer(BufWriter::new(file));

        for pomodoro in &pomodoros {
            let record = CsvRecord::from(pomodoro);
            writer
                .serialize(record)
                .map_err(|e| format!("Failed to write record: {}", e))?;
        }

        writer
            .flush()
            .map_err(|e| format!("Failed to flush: {}", e))?;

        Ok(())
    }
}
