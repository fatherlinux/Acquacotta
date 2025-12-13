# Acquacotta

A Pomodoro time tracking web application built with Python and Flask.

## Features

- Configurable work and break durations
- Pause and resume timer functionality
- Categorize pomodoros by type:
  - Product
  - Customer/Partner/Community
  - Content
  - Team
  - Social Media
  - Unqueued
  - Queued
  - Learn/Train
  - Travel
  - PTO
- View daily, weekly, and monthly reports with charts
- Export data to CSV
- Desktop notifications

## Running Locally

```bash
pip install flask
python app.py
```

Then open http://localhost:5000 in your browser.

## Building as Flatpak

```bash
flatpak-builder --force-clean build-dir com.github.fatherlinux.Acquacotta.yml
flatpak-builder --user --install --force-clean build-dir com.github.fatherlinux.Acquacotta.yml
flatpak run com.github.fatherlinux.Acquacotta
```

## License

MIT
