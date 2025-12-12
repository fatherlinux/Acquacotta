<script lang="ts">
  import { POMODORO_TYPES, type PomodoroType } from "../types";
  import { savePomodoro } from "../api/commands";
  import { addToStore } from "../stores/pomodoros";
  import { timer, resetToIdle } from "../stores/timer";
  import { settings } from "../stores/settings";

  interface Props {
    onclose: () => void;
  }

  let { onclose }: Props = $props();

  let name = $state("");
  let selectedType: PomodoroType = $state("Product");
  let notes = $state("");
  let saving = $state(false);

  async function handleSave() {
    if (!name.trim()) return;

    saving = true;
    try {
      const pomodoro = await savePomodoro(
        name.trim(),
        selectedType,
        $settings.work_duration_minutes,
        notes.trim() || undefined
      );
      addToStore(pomodoro);
      resetToIdle();
      onclose();
    } catch (error) {
      console.error("Failed to save pomodoro:", error);
    } finally {
      saving = false;
    }
  }

  function handleDiscard() {
    resetToIdle();
    onclose();
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape") {
      handleDiscard();
    } else if (event.key === "Enter" && event.ctrlKey) {
      handleSave();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="overlay" role="dialog" aria-modal="true">
  <div class="modal card">
    <h2>Save Pomodoro</h2>

    <div class="form-group">
      <label for="name">What did you work on?</label>
      <input
        id="name"
        type="text"
        bind:value={name}
        placeholder="Enter a description..."
        autofocus
      />
    </div>

    <div class="form-group">
      <label for="type">Type</label>
      <select id="type" bind:value={selectedType}>
        {#each POMODORO_TYPES as type}
          <option value={type}>{type}</option>
        {/each}
      </select>
    </div>

    <div class="form-group">
      <label for="notes">Notes (optional)</label>
      <textarea
        id="notes"
        bind:value={notes}
        placeholder="Any additional notes..."
        rows="3"
      ></textarea>
    </div>

    <div class="actions">
      <button class="secondary" onclick={handleDiscard} disabled={saving}>
        Discard
      </button>
      <button
        class="primary"
        onclick={handleSave}
        disabled={!name.trim() || saving}
      >
        {saving ? "Saving..." : "Save"}
      </button>
    </div>
  </div>
</div>

<style>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .modal {
    width: 100%;
    max-width: 400px;
    margin: 1rem;
  }

  h2 {
    margin-bottom: 1.5rem;
    font-size: 1.25rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  textarea {
    resize: vertical;
    min-height: 80px;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 1.5rem;
  }
</style>
