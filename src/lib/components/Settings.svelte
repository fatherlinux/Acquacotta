<script lang="ts">
  import { settings, updateSettings } from "../stores/settings";
  import type { Settings as SettingsType } from "../types";

  let localSettings: SettingsType = $state({ ...$settings });
  let saving = $state(false);
  let saved = $state(false);

  // Sync local state when store changes
  $effect(() => {
    localSettings = { ...$settings };
  });

  async function handleSave() {
    saving = true;
    try {
      await updateSettings(localSettings);
      saved = true;
      setTimeout(() => (saved = false), 2000);
    } catch (error) {
      console.error("Failed to save settings:", error);
    } finally {
      saving = false;
    }
  }

  function handleReset() {
    localSettings = {
      work_duration_minutes: 25,
      short_break_minutes: 5,
      long_break_minutes: 15,
      pomodoros_until_long_break: 4,
      sound_enabled: true,
      notifications_enabled: true,
    };
  }
</script>

<div class="container">
  <h2>Settings</h2>

  <div class="card settings-section">
    <h3>Timer Durations</h3>

    <div class="setting-row">
      <label for="work-duration">
        <span class="setting-label">Work Duration</span>
        <span class="setting-value">{localSettings.work_duration_minutes} minutes</span>
      </label>
      <input
        id="work-duration"
        type="range"
        min="1"
        max="60"
        bind:value={localSettings.work_duration_minutes}
      />
    </div>

    <div class="setting-row">
      <label for="short-break">
        <span class="setting-label">Short Break</span>
        <span class="setting-value">{localSettings.short_break_minutes} minutes</span>
      </label>
      <input
        id="short-break"
        type="range"
        min="1"
        max="30"
        bind:value={localSettings.short_break_minutes}
      />
    </div>

    <div class="setting-row">
      <label for="long-break">
        <span class="setting-label">Long Break</span>
        <span class="setting-value">{localSettings.long_break_minutes} minutes</span>
      </label>
      <input
        id="long-break"
        type="range"
        min="1"
        max="60"
        bind:value={localSettings.long_break_minutes}
      />
    </div>

    <div class="setting-row">
      <label for="pomodoros-until-break">
        <span class="setting-label">Pomodoros Until Long Break</span>
        <span class="setting-value">{localSettings.pomodoros_until_long_break}</span>
      </label>
      <input
        id="pomodoros-until-break"
        type="range"
        min="1"
        max="10"
        bind:value={localSettings.pomodoros_until_long_break}
      />
    </div>
  </div>

  <div class="card settings-section">
    <h3>Notifications</h3>

    <div class="setting-row toggle">
      <label for="sound-enabled">
        <span class="setting-label">Sound Alerts</span>
        <span class="setting-description">Play a sound when timer completes</span>
      </label>
      <input
        id="sound-enabled"
        type="checkbox"
        bind:checked={localSettings.sound_enabled}
      />
    </div>

    <div class="setting-row toggle">
      <label for="notifications-enabled">
        <span class="setting-label">Desktop Notifications</span>
        <span class="setting-description">Show system notifications</span>
      </label>
      <input
        id="notifications-enabled"
        type="checkbox"
        bind:checked={localSettings.notifications_enabled}
      />
    </div>
  </div>

  <div class="actions">
    <button class="secondary" onclick={handleReset}>Reset to Defaults</button>
    <button class="primary" onclick={handleSave} disabled={saving}>
      {#if saving}
        Saving...
      {:else if saved}
        Saved!
      {:else}
        Save Settings
      {/if}
    </button>
  </div>
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  h2 {
    font-size: 1.25rem;
  }

  h3 {
    font-size: 1rem;
    margin-bottom: 1rem;
    color: var(--text-secondary);
  }

  .settings-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .setting-row {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .setting-row.toggle {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .setting-row.toggle label {
    flex: 1;
  }

  .setting-label {
    display: block;
    font-weight: 500;
  }

  .setting-value {
    font-size: 0.875rem;
    color: var(--accent);
  }

  .setting-description {
    display: block;
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  input[type="range"] {
    width: 100%;
    height: 8px;
    padding: 0;
    background: var(--bg-tertiary);
    border-radius: 4px;
    cursor: pointer;
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
  }

  input[type="checkbox"] {
    width: 24px;
    height: 24px;
    cursor: pointer;
    accent-color: var(--accent);
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }
</style>
