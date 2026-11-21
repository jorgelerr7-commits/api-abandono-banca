const form = document.getElementById("cliente-form");
const submitButton = document.getElementById("submit-button");
const resetButton = document.getElementById("reset-button");
const errorMessage = document.getElementById("error-message");
const emptyState = document.getElementById("empty-state");
const resultContent = document.getElementById("result-content");

const defaults = {
  id_cliente: "CLI-8492", edad: 42, ingresos_anuales: 52000,
  saldo_cuenta: 18500, antiguedad_meses: 36, num_productos: 3,
  nivel_estudios: "Grado", tipo_cuenta: "Nomina", nivel_satisfaccion: "Medio",
  canal_preferido: "App Movil", tiene_tarjeta: true,
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.textContent = "";
  submitButton.disabled = true;
  submitButton.innerHTML = "<span>Analizando cliente...</span>";

  const formData = new FormData(form);
  const payload = {};
  const numberFields = ["edad", "ingresos_anuales", "saldo_cuenta", "num_productos", "antiguedad_meses"];

  for (const [key, value] of formData.entries()) {
    if (key === "tiene_tarjeta") payload[key] = true;
    else if (value !== "") payload[key] = numberFields.includes(key) ? Number(value) : value;
  }
  payload.tiene_tarjeta = formData.has("tiene_tarjeta");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(Array.isArray(error.detail) ? "Revisa los datos introducidos." : (error.detail || "No se pudo calcular la predicción"));
    }
    showResult(await response.json(), payload.id_cliente);
  } catch (error) {
    emptyState.classList.remove("hidden");
    resultContent.classList.add("hidden");
    errorMessage.textContent = error.message;
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = '<span>Calcular probabilidad</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  }
});

resetButton.addEventListener("click", () => {
  for (const [key, value] of Object.entries(defaults)) {
    const field = form.elements[key];
    if (!field) continue;
    if (field.type === "checkbox") field.checked = value;
    else field.value = value;
  }
  document.getElementById("analysis-id").textContent = "ID —";
  emptyState.classList.remove("hidden");
  resultContent.classList.add("hidden");
  errorMessage.textContent = "";
});

function showResult(data, idCliente) {
  emptyState.classList.add("hidden");
  resultContent.classList.remove("hidden");

  const percentage = Math.round(data.probabilidad_abandono * 100);
  const risk = data.nivel_riesgo.toLowerCase();
  const badge = document.getElementById("risk-badge");
  const ring = document.getElementById("score-ring");
  const marker = document.getElementById("risk-bar");

  document.getElementById("analysis-id").textContent = `ID ${idCliente}`;
  badge.textContent = `Riesgo ${data.nivel_riesgo}`;
  badge.className = `risk-badge${risk === "medio" ? " medium" : risk === "alto" ? " high" : ""}`;
  document.getElementById("prediction-label").textContent = data.abandono === 1 ? "Posible abandono" : "Cliente estable";
  document.getElementById("probability-value").textContent = `${percentage}%`;
  document.getElementById("recommendation").textContent = data.accion_recomendada;

  const color = risk === "alto" ? "#df5b65" : risk === "medio" ? "#dfa22a" : "#1da981";
  ring.style.setProperty("--score", `${percentage * 3.6}deg`);
  ring.style.setProperty("--risk-color", color);
  marker.style.left = `${percentage}%`;
  marker.style.background = color;
}
