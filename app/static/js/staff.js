// Handles task filtering and creation on /staff.

function renderTasks(tasks) {
  const container = document.getElementById("task-list");
  container.innerHTML = "";

  if (tasks.length === 0) {
    container.textContent = "No tasks found for that zone.";
    return;
  }

  const list = document.createElement("ul");
  tasks.forEach((task) => {
    const item = document.createElement("li");
    item.textContent = `[${task.priority}] ${task.title} — ${task.status}`;
    list.appendChild(item);
  });
  container.appendChild(list);
}

document.getElementById("task-filter-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const zone = document.getElementById("filter-zone").value.trim();

  try {
    const response = await fetch(`/staff/api/tasks?zone=${encodeURIComponent(zone)}`);
    const data = await response.json();
    if (!response.ok) {
      document.getElementById("task-list").textContent = data.error || "Could not load tasks.";
      return;
    }
    renderTasks(data);
  } catch (error) {
    document.getElementById("task-list").textContent = "Network error. Please try again.";
  }
});

document.getElementById("create-task-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    title: document.getElementById("task-title").value.trim(),
    zone: document.getElementById("task-zone").value.trim(),
    priority: document.getElementById("task-priority").value,
    description: document.getElementById("task-description").value.trim(),
  };
  const resultBox = document.getElementById("create-task-result");
  resultBox.textContent = "Creating...";

  try {
    const response = await fetch("/staff/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();

    if (!response.ok) {
      resultBox.textContent = data.error || "Could not create task.";
      return;
    }

    resultBox.textContent = `Task "${data.title}" created for ${data.zone}.`;
    event.target.reset();
  } catch (error) {
    resultBox.textContent = "Network error. Please try again.";
  }
});
