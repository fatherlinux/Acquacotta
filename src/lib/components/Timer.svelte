<script lang="ts">
  import {
    timer,
    formattedTime,
    progress,
    startTimer,
    pauseTimer,
    resumeTimer,
    stopTimer,
    skipBreak,
  } from "../stores/timer";
  import PomodoroForm from "./PomodoroForm.svelte";

  let showForm = $state(false);

  async function handleStart() {
    await startTimer();
  }

  async function handlePause() {
    await pauseTimer();
  }

  async function handleResume() {
    await resumeTimer();
  }

  async function handleStop() {
    await stopTimer();
    if (!$timer.isBreak && $timer.state === "idle") {
      showForm = true;
    }
  }

  async function handleSkipBreak() {
    await skipBreak();
  }

  function handleFormClose() {
    showForm = false;
  }

  // Calculate SVG circle properties
  const radius = 120;
  const circumference = 2 * Math.PI * radius;

  $effect(() => {
    // When timer completes (reaches 0 while running), show the form
    if ($timer.remainingSeconds === 0 && $timer.state === "running") {
      if (!$timer.isBreak) {
        showForm = true;
      }
    }
  });
</script>

<div class="timer-container">
  <div class="timer-display">
    <svg viewBox="0 0 280 280" class="progress-ring">
      <circle
        class="progress-ring-bg"
        cx="140"
        cy="140"
        r={radius}
        fill="none"
        stroke-width="8"
      />
      <circle
        class="progress-ring-progress"
        class:break={$timer.isBreak}
        cx="140"
        cy="140"
        r={radius}
        fill="none"
        stroke-width="8"
        stroke-dasharray={circumference}
        stroke-dashoffset={circumference - ($progress / 100) * circumference}
        transform="rotate(-90 140 140)"
      />
    </svg>
    <div class="time-text">
      <span class="time">{$formattedTime}</span>
      <span class="status">
        {#if $timer.isBreak}
          Break Time
        {:else if $timer.state === "idle"}
          Ready
        {:else if $timer.state === "paused"}
          Paused
        {:else}
          Focus
        {/if}
      </span>
    </div>
  </div>

  <div class="session-info">
    <span>Session {$timer.completedCount + 1}</span>
  </div>

  <div class="controls">
    {#if $timer.state === "idle"}
      <button class="primary large" onclick={handleStart}>Start</button>
    {:else if $timer.state === "running"}
      <button class="secondary" onclick={handlePause}>Pause</button>
      <button class="secondary" onclick={handleStop}>Stop</button>
    {:else if $timer.state === "paused"}
      <button class="primary" onclick={handleResume}>Resume</button>
      <button class="secondary" onclick={handleStop}>Stop</button>
    {:else if $timer.state === "break"}
      {#if $timer.remainingSeconds > 0}
        <button class="secondary" onclick={handleSkipBreak}>Skip Break</button>
      {:else}
        <button class="primary large" onclick={handleStart}>Start Next</button>
      {/if}
    {/if}
  </div>
</div>

{#if showForm}
  <PomodoroForm onclose={handleFormClose} />
{/if}

<style>
  .timer-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    padding: 2rem;
  }

  .timer-display {
    position: relative;
    width: 280px;
    height: 280px;
  }

  .progress-ring {
    width: 100%;
    height: 100%;
  }

  .progress-ring-bg {
    stroke: var(--bg-tertiary);
  }

  .progress-ring-progress {
    stroke: var(--accent);
    stroke-linecap: round;
    transition: stroke-dashoffset 0.5s ease;
  }

  .progress-ring-progress.break {
    stroke: var(--success);
  }

  .time-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
  }

  .time {
    display: block;
    font-size: 3.5rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
  }

  .status {
    display: block;
    font-size: 1rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .session-info {
    color: var(--text-secondary);
    font-size: 0.875rem;
  }

  .controls {
    display: flex;
    gap: 1rem;
  }

  button.large {
    padding: 1rem 3rem;
    font-size: 1.25rem;
  }
</style>
