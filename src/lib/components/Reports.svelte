<script lang="ts">
  import { onMount } from "svelte";
  import { getReportData, exportPomodoros } from "../api/commands";
  import { TYPE_COLORS, type ReportData, type PomodoroType } from "../types";
  import Chart from "./Chart.svelte";

  type Period = "day" | "week" | "month";

  let period: Period = $state("week");
  let currentDate = $state(new Date().toISOString().split("T")[0]);
  let reportData: ReportData | null = $state(null);
  let loading = $state(false);
  let error: string | null = $state(null);

  async function loadReport() {
    loading = true;
    error = null;
    try {
      reportData = await getReportData(period, currentDate);
    } catch (e) {
      error = "Failed to load report data";
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function navigatePeriod(direction: -1 | 1) {
    const date = new Date(currentDate);
    if (period === "day") {
      date.setDate(date.getDate() + direction);
    } else if (period === "week") {
      date.setDate(date.getDate() + direction * 7);
    } else {
      date.setMonth(date.getMonth() + direction);
    }
    currentDate = date.toISOString().split("T")[0];
  }

  async function handleExport() {
    try {
      const path = await exportPomodoros();
      alert(`Exported to: ${path}`);
    } catch (e) {
      console.error("Export failed:", e);
    }
  }

  function formatPeriodLabel(): string {
    const date = new Date(currentDate);
    if (period === "day") {
      return date.toLocaleDateString(undefined, {
        weekday: "long",
        month: "long",
        day: "numeric",
      });
    } else if (period === "week") {
      const start = new Date(date);
      start.setDate(date.getDate() - date.getDay());
      const end = new Date(start);
      end.setDate(start.getDate() + 6);
      return `${start.toLocaleDateString(undefined, { month: "short", day: "numeric" })} - ${end.toLocaleDateString(undefined, { month: "short", day: "numeric" })}`;
    } else {
      return date.toLocaleDateString(undefined, { month: "long", year: "numeric" });
    }
  }

  function formatDuration(minutes: number): string {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  }

  // Prepare chart data
  let pieChartData = $derived(
    reportData
      ? {
          labels: Object.keys(reportData.by_type).filter(
            (k) => reportData!.by_type[k as PomodoroType] > 0
          ),
          datasets: [
            {
              data: Object.entries(reportData.by_type)
                .filter(([_, v]) => v > 0)
                .map(([_, v]) => v),
              backgroundColor: Object.entries(reportData.by_type)
                .filter(([_, v]) => v > 0)
                .map(([k]) => TYPE_COLORS[k as PomodoroType]),
            },
          ],
        }
      : null
  );

  let barChartData = $derived(
    reportData
      ? {
          labels: reportData.daily_totals.map((d) =>
            new Date(d.date).toLocaleDateString(undefined, {
              weekday: "short",
            })
          ),
          datasets: [
            {
              label: "Minutes",
              data: reportData.daily_totals.map((d) => d.minutes),
              backgroundColor: "rgba(233, 69, 96, 0.7)",
            },
          ],
        }
      : null
  );

  onMount(() => {
    loadReport();
  });

  $effect(() => {
    // Reload when period or date changes
    period;
    currentDate;
    loadReport();
  });
</script>

<div class="container">
  <div class="header">
    <h2>Reports</h2>
    <button class="secondary" onclick={handleExport}>Export CSV</button>
  </div>

  <div class="period-selector">
    {#each ["day", "week", "month"] as p}
      <button
        class:active={period === p}
        onclick={() => (period = p as Period)}
      >
        {p.charAt(0).toUpperCase() + p.slice(1)}
      </button>
    {/each}
  </div>

  <div class="date-nav">
    <button class="nav-btn" onclick={() => navigatePeriod(-1)}>&larr;</button>
    <span class="date-label">{formatPeriodLabel()}</span>
    <button class="nav-btn" onclick={() => navigatePeriod(1)}>&rarr;</button>
  </div>

  {#if loading}
    <div class="loading">Loading...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if reportData}
    <div class="summary-cards">
      <div class="card summary-card">
        <span class="summary-value">{reportData.total_pomodoros}</span>
        <span class="summary-label">Pomodoros</span>
      </div>
      <div class="card summary-card">
        <span class="summary-value">{formatDuration(reportData.total_minutes)}</span>
        <span class="summary-label">Total Time</span>
      </div>
      <div class="card summary-card">
        <span class="summary-value">
          {reportData.total_pomodoros > 0
            ? Math.round(reportData.total_minutes / reportData.total_pomodoros)
            : 0}m
        </span>
        <span class="summary-label">Avg Duration</span>
      </div>
    </div>

    <div class="charts">
      {#if pieChartData && pieChartData.labels.length > 0}
        <div class="card chart-card">
          <h3>By Type</h3>
          <Chart type="pie" data={pieChartData} />
        </div>
      {/if}

      {#if barChartData && barChartData.labels.length > 0}
        <div class="card chart-card">
          <h3>Daily Activity</h3>
          <Chart type="bar" data={barChartData} />
        </div>
      {/if}
    </div>

    {#if reportData.total_pomodoros === 0}
      <div class="empty">No pomodoros recorded for this period.</div>
    {/if}
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
    font-size: 1rem;
    margin-bottom: 1rem;
  }

  .period-selector {
    display: flex;
    gap: 0.5rem;
    background-color: var(--bg-secondary);
    padding: 0.25rem;
    border-radius: var(--border-radius);
  }

  .period-selector button {
    flex: 1;
    padding: 0.5rem;
    background: transparent;
    color: var(--text-secondary);
  }

  .period-selector button:hover {
    transform: none;
  }

  .period-selector button.active {
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .date-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }

  .nav-btn {
    background: var(--bg-secondary);
    padding: 0.5rem 1rem;
  }

  .date-label {
    font-weight: 500;
    min-width: 200px;
    text-align: center;
  }

  .summary-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .summary-card {
    text-align: center;
    padding: 1.5rem 1rem;
  }

  .summary-value {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
  }

  .summary-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
  }

  .charts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
  }

  .chart-card {
    min-height: 300px;
  }

  .loading,
  .error,
  .empty {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary);
  }

  .error {
    color: var(--accent);
  }
</style>
