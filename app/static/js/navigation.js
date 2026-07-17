// Handles the navigation guidance form on /navigation.

document.getElementById("nav-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const from = document.getElementById("from-zone").value.trim();
  const to = document.getElementById("to-zone").value.trim();
  const language = document.getElementById("nav-language").value;
  const resultBox = document.getElementById("nav-result");

  resultBox.textContent = "Getting directions...";

  try {
    const response = await fetch("/navigation/api/guide", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ from, to, language }),
    });
    const data = await response.json();

    if (!response.ok) {
      resultBox.textContent = data.error || "Something went wrong. Please try again.";
      return;
    }

    resultBox.textContent = data.guidance;
  } catch (error) {
    resultBox.textContent = "Network error. Please check your connection and try again.";
  }
});
