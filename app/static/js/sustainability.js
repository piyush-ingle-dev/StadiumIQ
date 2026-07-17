// Handles the sustainability metric logging form on /sustainability (admin only).

const sustainForm = document.getElementById("sustain-form");

if (sustainForm) {
  sustainForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const category = document.getElementById("category").value;
    const quantity = document.getElementById("quantity").value;
    const resultBox = document.getElementById("sustain-result");

    resultBox.textContent = "Logging...";

    try {
      const response = await fetch("/sustainability/api/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category, quantity: parseFloat(quantity) }),
      });
      const data = await response.json();

      if (!response.ok) {
        resultBox.textContent = data.error || "Could not log metric.";
        return;
      }

      resultBox.textContent = `Logged ${data.quantity} for ${data.category} (${data.estimated_co2e_kg} kg CO2e).`;
      setTimeout(() => window.location.reload(), 1200);
    } catch (error) {
      resultBox.textContent = "Network error. Please try again.";
    }
  });
}
