// Handles the translation form on /multilingual.

document.getElementById("translate-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = document.getElementById("source-text").value.trim();
  const targetLanguage = document.getElementById("target-language").value;
  const resultBox = document.getElementById("translate-result");

  resultBox.textContent = "Translating...";

  try {
    const response = await fetch("/multilingual/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, target_language: targetLanguage }),
    });
    const data = await response.json();

    if (!response.ok) {
      resultBox.textContent = data.error || "Translation failed.";
      return;
    }

    resultBox.textContent = data.translated;
  } catch (error) {
    resultBox.textContent = "Network error. Please try again.";
  }
});
