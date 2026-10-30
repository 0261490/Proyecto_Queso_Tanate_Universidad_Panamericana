import type { Question, QuestionId } from "../../inference-engine/src/index.ts";

const ICONS: Readonly<Record<QuestionId, string>> = {
  traditionalMexican: "tradition",
  purchaseIntention: "growth",
  recommendation: "voice",
  gastronomicHeritage: "heritage",
  authenticElaboration: "craft",
  commercialPotential: "growth",
  culturePreservation: "culture",
  sensoryUniqueness: "senses",
};

export function renderQuestion(
  question: Question,
  index: number,
  total: number,
): string {
  const number = index + 1;
  return `
    <fieldset class="question-card" data-question="${question.id}">
      <legend>
        <span class="question-number">Pregunta ${number} de ${total}</span>
        <span class="question-title">
          <svg class="question-icon" aria-hidden="true"><use href="#icon-${ICONS[question.id]}"></use></svg>
          <span>${question.prompt}</span>
        </span>
      </legend>
      <div class="answer-options">
        <label>
          <input type="radio" name="${question.id}" value="true" required />
          <span><span class="choice-mark" aria-hidden="true">✓</span>Sí</span>
        </label>
        <label>
          <input type="radio" name="${question.id}" value="false" required />
          <span><span class="choice-mark" aria-hidden="true">—</span>No</span>
        </label>
      </div>
    </fieldset>`;
}

export function formatProbability(probability: number): string {
  const parts = new Intl.NumberFormat("es-MX", {
    style: "percent",
    maximumFractionDigits: 1,
  }).formatToParts(probability);

  return parts
    .map((part) => (part.type === "percentSign" ? `\u00a0${part.value}` : part.value))
    .join("");
}

export function interpretProbability(probability: number): string {
  if (probability >= 0.75) return "La señal de intención de compra es alta";
  if (probability >= 0.5) return "La señal de intención de compra es favorable";
  if (probability >= 0.25) return "La señal de intención de compra es moderada";
  return "La señal de intención de compra es baja";
}
