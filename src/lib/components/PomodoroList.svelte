<script lang="ts">
  import { pomodoros, loadPomodoros, removePomodoro, editPomodoro } from "../stores/pomodoros";
  import { POMODORO_TYPES, TYPE_COLORS, type Pomodoro, type PomodoroType } from "../types";
  import { addManualPomodoro } from "../api/commands";
  import { addToStore } from "../stores/pomodoros";

  let editingId: string | null = $state(null);
  let editForm = $state({ name: "", pomodoro_type: "Product" as PomodoroType, notes: "" });
  let showAddForm = $state(false);
  let addForm = $state({
    name: "",
    pomodoro_type: "Product" as PomodoroType,
    date: new Date().toISOString().split("T")[0],
    startTime: "09:00",
    duration: 25,
    notes: "",
  });

  function formatDate(isoString: string): string {
    return new Date(isoString).toLocaleDateString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  }

  function formatTime(isoString: string): string {
    return new Date(isoString).toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function startEdit(pomodoro: Pomodoro) {
    editingId = pomodoro.id;
    editForm = {
      name: pomodoro.name,
      pomodoro_type: pomodoro.pomodoro_type,
      notes: pomodoro.notes || "",
    };
  }

  async function saveEdit(pomodoro: Pomodoro) {
    await editPomodoro({
      ...pomodoro,
      name: editForm.name,
      pomodoro_type: editForm.pomodoro_type,
      notes: editForm.notes || undefined,
    });
    editingId = null;
  }

  function cancelEdit() {
    editingId = null;
  }

  async function handleDelete(id: string) {
    if (confirm("Delete this pomodoro?")) {
      await removePomodoro(id);
    }
  }

  async function handleAddManual() {
    if (!addForm.name.trim()) return;

    const startDateTime = new Date(`${addForm.date}T${addForm.startTime}`);
    const endDateTime = new Date(startDateTime.getTime() + addForm.duration * 60000);

    const pomodoro = await addManualPomodoro(
      addForm.name.trim(),
      addForm.pomodoro_type,
      startDateTime.toISOString(),
      endDateTime.toISOString(),
      addForm.duration,
      addForm.notes.trim() || undefined
    );

    addToStore(pomodoro);
    showAddForm = false;
    addForm = {
      name: "",
      pomodoro_type: "Product",
      date: new Date().toISOString().split("T")[0],
      startTime: "09:00",
      duration: 25,
      notes: "",
    };
  }

  // Group pomodoros by date
  function groupByDate(items: Pomodoro[]): Map<string, Pomodoro[]> {
    const groups = new Map<string, Pomodoro[]>();
    for (const item of items) {
      const date = formatDate(item.start_time);
      const existing = groups.get(date) || [];
      groups.set(date, [...existing, item]);
    }
    return groups;
  }

  let grouped = $derived(groupByDate($pomodoros));
</script>

<div class="container">
  <div class="header">
    <h2>History</h2>
    <button class="secondary" onclick={() => (showAddForm = !showAddForm)}>
      {showAddForm ? "Cancel" : "+ Add Manual"}
    </button>
  </div>

  {#if showAddForm}
    <div class="card add-form">
      <div class="form-row">
        <div class="form-group">
          <label for="add-name">Description</label>
          <input id="add-name" type="text" bind:value={addForm.name} placeholder="What did you work on?" />
        </div>
        <div class="form-group">
          <label for="add-type">Type</label>
          <select id="add-type" bind:value={addForm.pomodoro_type}>
            {#each POMODORO_TYPES as type}
              <option value={type}>{type}</option>
            {/each}
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="add-date">Date</label>
          <input id="add-date" type="date" bind:value={addForm.date} />
        </div>
        <div class="form-group">
          <label for="add-time">Start Time</label>
          <input id="add-time" type="time" bind:value={addForm.startTime} />
        </div>
        <div class="form-group">
          <label for="add-duration">Duration (min)</label>
          <input id="add-duration" type="number" bind:value={addForm.duration} min="1" max="120" />
        </div>
      </div>
      <div class="form-group">
        <label for="add-notes">Notes</label>
        <input id="add-notes" type="text" bind:value={addForm.notes} placeholder="Optional notes..." />
      </div>
      <button class="primary" onclick={handleAddManual} disabled={!addForm.name.trim()}>
        Add Pomodoro
      </button>
    </div>
  {/if}

  {#if $pomodoros.length === 0}
    <div class="empty">
      <p>No pomodoros yet. Start your first timer!</p>
    </div>
  {:else}
    {#each [...grouped.entries()] as [date, items]}
      <div class="date-group">
        <h3>{date}</h3>
        {#each items as pomodoro}
          <div class="pomodoro-item card">
            {#if editingId === pomodoro.id}
              <div class="edit-form">
                <input type="text" bind:value={editForm.name} />
                <select bind:value={editForm.pomodoro_type}>
                  {#each POMODORO_TYPES as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
                <input type="text" bind:value={editForm.notes} placeholder="Notes..." />
                <div class="edit-actions">
                  <button class="secondary small" onclick={cancelEdit}>Cancel</button>
                  <button class="primary small" onclick={() => saveEdit(pomodoro)}>Save</button>
                </div>
              </div>
            {:else}
              <div class="pomodoro-content">
                <div class="pomodoro-main">
                  <span class="pomodoro-name">{pomodoro.name}</span>
                  <span
                    class="pomodoro-type"
                    style="background-color: {TYPE_COLORS[pomodoro.pomodoro_type]}20; color: {TYPE_COLORS[pomodoro.pomodoro_type]}"
                  >
                    {pomodoro.pomodoro_type}
                  </span>
                </div>
                <div class="pomodoro-meta">
                  <span>{formatTime(pomodoro.start_time)} - {formatTime(pomodoro.end_time)}</span>
                  <span>{pomodoro.duration_minutes} min</span>
                </div>
                {#if pomodoro.notes}
                  <div class="pomodoro-notes">{pomodoro.notes}</div>
                {/if}
              </div>
              <div class="pomodoro-actions">
                <button class="icon-btn" onclick={() => startEdit(pomodoro)} title="Edit">
                  &#9998;
                </button>
                <button class="icon-btn delete" onclick={() => handleDelete(pomodoro.id)} title="Delete">
                  &#10005;
                </button>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/each}
  {/if}
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  h2 {
    font-size: 1.25rem;
  }

  h3 {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
  }

  .add-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .form-row {
    display: flex;
    gap: 0.75rem;
  }

  .form-group {
    flex: 1;
  }

  .form-group label {
    display: block;
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
  }

  .date-group {
    margin-bottom: 1rem;
  }

  .pomodoro-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 1rem;
    margin-bottom: 0.5rem;
  }

  .pomodoro-content {
    flex: 1;
  }

  .pomodoro-main {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .pomodoro-name {
    font-weight: 500;
  }

  .pomodoro-type {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .pomodoro-meta {
    font-size: 0.875rem;
    color: var(--text-secondary);
    display: flex;
    gap: 1rem;
  }

  .pomodoro-notes {
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-style: italic;
    margin-top: 0.5rem;
  }

  .pomodoro-actions {
    display: flex;
    gap: 0.5rem;
  }

  .icon-btn {
    background: none;
    padding: 0.5rem;
    color: var(--text-secondary);
    font-size: 1rem;
  }

  .icon-btn:hover {
    color: var(--text-primary);
    transform: none;
  }

  .icon-btn.delete:hover {
    color: var(--accent);
  }

  .edit-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }

  .edit-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
  }

  button.small {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }

  .empty {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
  }
</style>
