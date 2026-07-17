// Live operational intelligence dashboard: streams snapshots via
// Server-Sent Events and refreshes the AI briefing periodically.

function renderSnapshot(snapshot) {
  document.getElementById("snapshot-zones").textContent =
    snapshot.zones_at_risk_count === 0
      ? "None"
      : snapshot.zones_at_risk.map((z) => z.zone).join(", ");
  document.getElementById("snapshot-tasks").textContent = snapshot.open_task_count;
  document.getElementById("snapshot-emissions").textContent = snapshot.total_emissions_kg;
  document.getElementById("snapshot-updated").textContent = new Date(
    snapshot.generated_at
  ).toLocaleTimeString();
}

async function refreshBriefing() {
  try {
    const response = await fetch("/insights/api/briefing");
    if (!response.ok) return;
    const data = await response.json();
    document.getElementById("briefing-text").textContent = data.briefing;
  } catch (error) {
    // Silently retry on the next interval; the snapshot stream still
    // keeps the page usable even if the briefing call fails once.
  }
}

function connectStream() {
  const statusEl = document.getElementById("connection-status");
  const source = new EventSource("/insights/api/stream");

  source.onopen = () => {
    statusEl.textContent = "Connected — live updates active.";
  };

  source.onmessage = (event) => {
    const snapshot = JSON.parse(event.data);
    renderSnapshot(snapshot);
  };

  source.onerror = () => {
    statusEl.textContent = "Reconnecting to live feed…";
  };
}

document.addEventListener("DOMContentLoaded", () => {
  connectStream();
  refreshBriefing();
  setInterval(refreshBriefing, 30000);
});
