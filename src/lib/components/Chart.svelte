<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import {
    Chart as ChartJS,
    ArcElement,
    BarElement,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Title,
    Tooltip,
    Legend,
    type ChartData,
    type ChartType,
  } from "chart.js";

  ChartJS.register(
    ArcElement,
    BarElement,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Title,
    Tooltip,
    Legend
  );

  interface Props {
    type: "pie" | "bar" | "line";
    data: ChartData;
  }

  let { type, data }: Props = $props();

  let canvas: HTMLCanvasElement;
  let chart: ChartJS | null = null;

  function createChart() {
    if (chart) {
      chart.destroy();
    }

    chart = new ChartJS(canvas, {
      type: type as ChartType,
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: type === "pie" ? "right" : "top",
            labels: {
              color: "#a0a0a0",
            },
          },
        },
        scales:
          type !== "pie"
            ? {
                x: {
                  ticks: { color: "#a0a0a0" },
                  grid: { color: "#1a1a2e" },
                },
                y: {
                  ticks: { color: "#a0a0a0" },
                  grid: { color: "#1a1a2e" },
                },
              }
            : undefined,
      },
    });
  }

  onMount(() => {
    createChart();
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
  });

  $effect(() => {
    // Recreate chart when data changes
    data;
    type;
    if (canvas) {
      createChart();
    }
  });
</script>

<div class="chart-container">
  <canvas bind:this={canvas}></canvas>
</div>

<style>
  .chart-container {
    position: relative;
    width: 100%;
    height: 250px;
  }
</style>
