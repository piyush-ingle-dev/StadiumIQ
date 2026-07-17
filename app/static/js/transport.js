// Handles the transport recommendation form on /transport.

document.getElementById("transport-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const distanceKm = document.getElementById("distance").value;
  const resultBox = document.getElementById("transport-result");

  resultBox.textContent = "Loading recommendations...";

  try {
    const response = await fetch(`/transport/api/recommend?distance_km=${encodeURIComponent(distanceKm)}`);
    const data = await response.json();

    if (!response.ok) {
      resultBox.textContent = data.error || "Could not load recommendations.";
      return;
    }

    resultBox.innerHTML = "";
    const list = document.createElement("ul");
    data.forEach((option) => {
      const item = document.createElement("li");
      const recommendedTag = option.recommended ? " (recommended)" : "";
      item.textContent = `${option.label}${recommendedTag} — approx. ${option.estimated_co2e_kg} kg CO2e`;
      list.appendChild(item);
    });
    resultBox.appendChild(list);
  } catch (error) {
    resultBox.textContent = "Network error. Please try again.";
  }
});
