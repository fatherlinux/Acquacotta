<script lang="ts">
  type View = "timer" | "history" | "reports" | "settings";

  interface Props {
    currentView: View;
  }

  let { currentView = $bindable() }: Props = $props();

  const tabs: { id: View; label: string }[] = [
    { id: "timer", label: "Timer" },
    { id: "history", label: "History" },
    { id: "reports", label: "Reports" },
    { id: "settings", label: "Settings" },
  ];
</script>

<nav>
  {#each tabs as tab}
    <button
      class:active={currentView === tab.id}
      onclick={() => (currentView = tab.id)}
    >
      {tab.label}
    </button>
  {/each}
</nav>

<style>
  nav {
    display: flex;
    gap: 0.5rem;
    background-color: var(--bg-secondary);
    padding: 0.5rem;
    border-radius: var(--border-radius);
  }

  button {
    flex: 1;
    padding: 0.75rem 1rem;
    background-color: transparent;
    color: var(--text-secondary);
    font-weight: 500;
  }

  button:hover {
    background-color: var(--bg-tertiary);
    color: var(--text-primary);
    transform: none;
  }

  button.active {
    background-color: var(--accent);
    color: white;
  }
</style>
