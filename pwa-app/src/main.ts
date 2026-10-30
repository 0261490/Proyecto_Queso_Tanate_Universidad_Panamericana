import "./styles.css";

import modelData from "../../model-export/model.json";
import {
  ExactInferenceEngine,
  mapAnswersToEvidence,
  QUESTION_CATALOG,
  loadModel,
  type QuestionId,
  type UserAnswers,
} from "../../inference-engine/src/index.ts";
import {
  formatProbability,
  interpretProbability,
  renderQuestion,
} from "./presentation.ts";

interface InstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

function element<T extends HTMLElement>(id: string): T {
  const found = document.getElementById(id);
  if (!found) throw new Error(`Missing application element: ${id}`);
  return found as T;
}

const questions = QUESTION_CATALOG.filter(
  ({ id }) => id !== "purchaseIntention",
);
const engine = new ExactInferenceEngine(loadModel(modelData));

const form = element<HTMLFormElement>("assessment-form");
const list = element<HTMLDivElement>("question-list");
const progress = element<HTMLProgressElement>("question-progress");
const progressLabel = element<HTMLSpanElement>("progress-label");
const errorBox = element<HTMLDivElement>("form-error");
const results = element<HTMLElement>("results");
const resultSummary = element<HTMLParagraphElement>("result-summary");
const probabilityRing = element<HTMLDivElement>("probability-ring");
const probabilityValue = element<HTMLSpanElement>("probability-value");
const probabilityMeter = element<HTMLDivElement>("probability-meter");
const restartButton = element<HTMLButtonElement>("restart-button");
const connectionStatus = element<HTMLSpanElement>("connection-status");
const installButton = element<HTMLButtonElement>("install-button");

list.innerHTML = questions
  .map((question, index) => renderQuestion(question, index, questions.length))
  .join("");
progress.max = questions.length;

function answeredCount(): number {
  const data = new FormData(form);
  return questions.filter(({ id }) => data.has(id)).length;
}

function updateProgress(): void {
  const count = answeredCount();
  progress.value = count;
  progress.textContent = `${count} de ${questions.length}`;
  progressLabel.textContent = `${count} de ${questions.length} respondidas`;
}

function collectAnswers(): UserAnswers {
  const data = new FormData(form);
  const answers: Partial<Record<QuestionId, boolean>> = {};
  for (const question of questions) {
    const raw = data.get(question.id);
    if (raw === "true" || raw === "false") {
      answers[question.id] = raw === "true";
    }
  }
  return answers;
}

function showError(message: string): void {
  errorBox.textContent = message;
  errorBox.hidden = false;
  errorBox.focus();
}

form.addEventListener("change", () => {
  errorBox.hidden = true;
  updateProgress();
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const missing = questions.length - answeredCount();
  if (missing > 0) {
    showError(
      missing === 1
        ? "Falta responder una pregunta antes de continuar."
        : `Faltan ${missing} preguntas antes de continuar.`,
    );
    const firstMissing = questions.find(({ id }) => !new FormData(form).has(id));
    form.querySelector<HTMLInputElement>(`input[name="${firstMissing?.id}"]`)?.focus();
    return;
  }

  try {
    const evidence = mapAnswersToEvidence(collectAnswers());
    const probability = engine.probability("Q2_Purchase_Intention", "Yes", evidence);
    const percent = Math.round(probability * 1000) / 10;
    const formatted = formatProbability(probability);

    probabilityValue.textContent = formatted;
    probabilityRing.style.setProperty("--probability", `${percent * 3.6}deg`);
    probabilityMeter.setAttribute("aria-valuenow", String(percent));
    probabilityMeter.setAttribute("aria-valuetext", formatted);
    resultSummary.textContent = `${interpretProbability(probability)}: ${formatted}.`;
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
    element<HTMLElement>("results-title").focus({ preventScroll: true });
  } catch (error) {
    console.error(error);
    showError("No fue posible calcular el resultado. Revise sus respuestas e intente de nuevo.");
  }
});

restartButton.addEventListener("click", () => {
  form.reset();
  results.hidden = true;
  errorBox.hidden = true;
  updateProgress();
  element<HTMLElement>("assessment-title").focus();
  form.scrollIntoView({ behavior: "smooth", block: "start" });
});

function updateConnectionStatus(): void {
  const online = navigator.onLine;
  connectionStatus.classList.toggle("is-offline", !online);
  connectionStatus.querySelector("span:last-child")!.textContent = online
    ? "Con conexión"
    : "Disponible sin conexión";
}

window.addEventListener("online", updateConnectionStatus);
window.addEventListener("offline", updateConnectionStatus);
updateConnectionStatus();
updateProgress();

let installPrompt: InstallPromptEvent | undefined;
window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  installPrompt = event as InstallPromptEvent;
  installButton.hidden = false;
});

installButton.addEventListener("click", async () => {
  if (!installPrompt) return;
  await installPrompt.prompt();
  await installPrompt.userChoice;
  installPrompt = undefined;
  installButton.hidden = true;
});

window.addEventListener("appinstalled", () => {
  installPrompt = undefined;
  installButton.hidden = true;
});

if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch((error) => {
      console.error("Service worker registration failed", error);
    });
  });
}
