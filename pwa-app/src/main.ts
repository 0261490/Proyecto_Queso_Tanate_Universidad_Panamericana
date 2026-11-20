import "./styles.css";

import modelData from "../../model-export/model.json";
import modelHash from "../../model-export/model.sha256?raw";
import { HistoryStore } from "./storage/history.ts";
import { createHistoryUI } from "./history-ui.ts";
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
const historyStore = new HistoryStore();
const modelSha256 = modelHash.trim().split(/\s+/)[0];
const historyUI = createHistoryUI(historyStore, modelSha256);
const saveStatus = element<HTMLParagraphElement>("save-status");
const submitButton = document.querySelector<HTMLButtonElement>('button[type="submit"]')!;
let saving = false;
let evaluationVersion = 0;

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
const offlineStatus = element<HTMLParagraphElement>("offline-status");

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
  evaluationVersion++;
  errorBox.hidden = true;
  results.hidden = true;
  updateProgress();
});

function scrollToSection(section: HTMLElement): void {
  section.scrollIntoView({
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth",
    block: "start",
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (saving) return;
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
    const answers = collectAnswers();
    const evidence = mapAnswersToEvidence(answers);
    const probability = engine.probability("Q2_Purchase_Intention", "Yes", evidence);
    const percent = Math.round(probability * 1000) / 10;
    const formatted = formatProbability(probability);

    probabilityValue.textContent = formatted;
    probabilityRing.style.setProperty("--probability", `${percent * 3.6}deg`);
    probabilityMeter.setAttribute("aria-valuenow", String(percent));
    probabilityMeter.setAttribute("aria-valuetext", formatted);
    resultSummary.textContent = `${interpretProbability(probability)}: ${formatted}.`;
    results.hidden = false;
    scrollToSection(results);
    element<HTMLElement>("results-title").focus({ preventScroll: true });
    saving = true;
    submitButton.disabled = true;
    const version = ++evaluationVersion;
    saveStatus.textContent = "Guardando evaluación en este navegador…";
    try {
      await historyStore.add({
        schemaVersion: 1,
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),
        model: { version: modelData.model_version, sha256: modelSha256 },
        answers,
        evidence,
        result: { variable: "Q2_Purchase_Intention", state: "Yes", probability },
      });
      if (version === evaluationVersion) saveStatus.textContent = "Evaluación guardada en el historial de este navegador.";
      await historyUI.reload();
    } catch {
      if (version === evaluationVersion) saveStatus.textContent = "El resultado es válido, pero no se pudo guardar. Compruebe el espacio o los permisos del navegador y vuelva a evaluar para reintentar.";
    } finally {
      saving = false;
      submitButton.disabled = false;
    }
  } catch (error) {
    console.error(error);
    showError("No fue posible calcular el resultado. Revise sus respuestas e intente de nuevo.");
  }
});

restartButton.addEventListener("click", () => {
  evaluationVersion++;
  form.reset();
  results.hidden = true;
  errorBox.hidden = true;
  updateProgress();
  element<HTMLElement>("assessment-title").focus();
  scrollToSection(form);
});

function updateConnectionStatus(): void {
  const online = navigator.onLine;
  connectionStatus.classList.toggle("is-offline", !online);
  connectionStatus.querySelector("span:last-child")!.textContent = online
    ? "Con conexión"
    : "Sin conexión";
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
    const updateOfflineStatus = (): void => {
      if (navigator.serviceWorker.controller) {
        offlineStatus.textContent = "Lista para usar sin conexión en este navegador.";
      }
    };
    navigator.serviceWorker.addEventListener("controllerchange", updateOfflineStatus);
    updateOfflineStatus();
    navigator.serviceWorker.register("./sw.js").then(async () => {
      await navigator.serviceWorker.ready;
      updateOfflineStatus();
    }).catch((error) => {
      console.error("Service worker registration failed", error);
      offlineStatus.textContent = "No se pudo preparar el uso sin conexión. Recargue con conexión para reintentar.";
    });
  });
} else {
  offlineStatus.textContent = import.meta.env.PROD
    ? "Este navegador no permite preparar el uso sin conexión. Abra la aplicación en Chrome o Edge."
    : "El uso sin conexión se prepara en la versión de producción.";
}
