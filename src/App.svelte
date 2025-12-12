<script lang="ts">
  import { onMount } from "svelte";
  import Navigation from "./lib/components/Navigation.svelte";
  import Timer from "./lib/components/Timer.svelte";
  import PomodoroList from "./lib/components/PomodoroList.svelte";
  import Reports from "./lib/components/Reports.svelte";
  import Settings from "./lib/components/Settings.svelte";
  import { loadSettings } from "./lib/stores/settings";
  import { syncTimerStatus } from "./lib/stores/timer";
  import { loadPomodoros } from "./lib/stores/pomodoros";

  type View = "timer" | "history" | "reports" | "settings";
  let currentView: View = $state("timer");

  onMount(async () => {
    await loadSettings();
    await syncTimerStatus();
    await loadPomodoros();
  });
</script>

<main>
  <Navigation bind:currentView />

  <div class="content">
    {#if currentView === "timer"}
      <Timer />
    {:else if currentView === "history"}
      <PomodoroList />
    {:else if currentView === "reports"}
      <Reports />
    {:else if currentView === "settings"}
      <Settings />
    {/if}
  </div>
</main>

<style>
  main {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
  }

  .content {
    flex: 1;
    overflow-y: auto;
    padding-top: 1rem;
  }
</style>
