# Acquacotta

A Pomodoro time tracking desktop application built with Rust, Tauri, and Svelte.

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
- Desktop notifications with sound alerts

## Building as Flatpak

### Prerequisites

Install the required Flatpak SDK and extensions:

```bash
flatpak install flathub org.freedesktop.Platform//24.08
flatpak install flathub org.freedesktop.Sdk//24.08
flatpak install flathub org.freedesktop.Sdk.Extension.rust-stable//24.08
flatpak install flathub org.freedesktop.Sdk.Extension.node20//24.08
```

### Build

```bash
flatpak-builder --force-clean build-dir com.github.fatherlinux.Acquacotta.yml
```

### Install locally

```bash
flatpak-builder --user --install --force-clean build-dir com.github.fatherlinux.Acquacotta.yml
```

### Run

```bash
flatpak run com.github.fatherlinux.Acquacotta
```

## Development (without Flatpak)

If you want to develop locally without Flatpak, you'll need:

- Node.js 20+
- Rust (via rustup)
- Tauri CLI: `cargo install tauri-cli`
- System dependencies for Tauri (webkit2gtk, etc.)

```bash
npm install
npm run tauri dev
```

## License

MIT
