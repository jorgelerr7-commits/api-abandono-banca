const form = document.getElementById("cliente-form");
const submitButton = document.getElementById("submit-button");
const errorMessage = document.getElementById("error-message");
const emptyState = document.getElementById("empty-state");
const resultContent = document.getElementById("result-content");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.textContent = "";
  submitButton.disabled = true;
  submitButton.textContent = "Calculando...";

  const formData = new FormData(form);
  const payload = {};
  const numberFields = ["edad", "ingresos_anuales", "saldo_cuenta", "num_productos", "antiguedad_meses"];

  for (const [key, value] of formData.entries()) {
    if (key === "tiene_tarjeta") payload[key] = true;
    else if (value !== "") payload[key] = numberFields.includes(key) ? Number(value) : value;
  }
  if (!formData.has("tiene_tarjeta")) payload.tiene_tarjeta = false;

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "No se pudo calcular la predicción");
    }
    showResult(await response.json());
  } catch (error) {
    errorMessage.textContent = error.message;
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Calcular riesgo";
  }
});

function showResult(data) {
  emptyState.classList.add("hidden");
  resultContent.classList.remove("hidden");

  const percentage = Math.round(data.probabilidad_abandono * 100);
  const badge = document.getElementById("risk-badge");
  const riskBar = document.getElementById("risk-bar");

  badge.textContent = `Riesgo ${data.nivel_riesgo}`;
  badge.className = `badge risk-${data.nivel_riesgo.toLowerCase()}`;
  document.getElementById("prediction-title").textContent = data.abandono === 1 ? "Alta probabilidad de fuga" : "Cliente estable";
  document.getElementById("probability-value").textContent = `${percentage}%`;
  document.getElementById("recommendation").textContent = data.accion_recomendada;
  riskBar.style.width = `${percentage}%`;
  riskBar.className = `risk-fill-${data.nivel_riesgo.toLowerCase()}`;
}
