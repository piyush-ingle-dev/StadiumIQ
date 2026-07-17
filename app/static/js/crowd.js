// Handles the crowd report submission form on /crowd (staff/admin only).

const crowdForm = document.getElementById("crowd-form");

if (crowdForm) {
  crowdForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const zone = document.getElementById("zone").value.trim();
    const peopleEstimate = parseInt(document.getElementById("people-estimate").value, 10);
    const resultBox = document.getElementById("crowd-result");

    resultBox.textContent = "Submitting...";

    try {
      const response = await fetch("/crowd/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ zone, people_estimate: peopleEstimate }),
      });
      const data = await response.json();

      if (!response.ok) {
        resultBox.textContent = data.error || "Could not submit report.";
        return;
      }

      resultBox.textContent = `Recorded: ${data.zone} is now ${data.density_level} density.`;
      setTimeout(() => window.location.reload(), 1200);
    } catch (error) {
      resultBox.textContent = "Network error. Please try again.";
    }
  });
}
