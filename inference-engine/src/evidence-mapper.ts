import type { Evidence } from "./types.ts";

export const QUESTION_CATALOG = [
  {
    id: "traditionalMexican",
    prompt: "¿Considera que el Queso Tenate es un producto tradicional mexicano?",
    variable: "Q1_Traditional_Mexican",
  },
  {
    id: "purchaseIntention",
    prompt: "¿Compraría Queso Tenate?",
    variable: "Q2_Purchase_Intention",
  },
  {
    id: "recommendation",
    prompt: "¿Recomendaría el Queso Tenate?",
    variable: "Q3_Recommendation",
  },
  {
    id: "gastronomicHeritage",
    prompt: "¿Considera que el Queso Tenate forma parte del patrimonio gastronómico?",
    variable: "Q4_Gastronomic_Heritage",
  },
  {
    id: "authenticElaboration",
    prompt: "¿Considera auténtico el proceso de elaboración del Queso Tenate?",
    variable: "Q5_Authenticity_Elaboration",
  },
  {
    id: "commercialPotential",
    prompt: "¿Considera que el Queso Tenate tiene potencial comercial?",
    variable: "Q6_Commercial_Potential",
  },
  {
    id: "culturePreservation",
    prompt: "¿Considera que el Queso Tenate contribuye a preservar la cultura y la tradición?",
    variable: "Q7_Culture_Preservation",
  },
  {
    id: "sensoryUniqueness",
    prompt: "¿Considera que el Queso Tenate posee características sensoriales únicas?",
    variable: "Q8_Sensory_Uniqueness",
  },
] as const;

export type Question = (typeof QUESTION_CATALOG)[number];
export type QuestionId = Question["id"];
export type UserAnswers = Readonly<Partial<Record<QuestionId, boolean>>>;

export class EvidenceMapperError extends Error {
  readonly questionId?: string;

  constructor(message: string, questionId?: string) {
    super(message);
    this.name = "EvidenceMapperError";
    this.questionId = questionId;
  }
}

const QUESTIONS_BY_ID: ReadonlyMap<string, Question> = new Map(
  QUESTION_CATALOG.map((question) => [question.id, question]),
);

/**
 * Validates the runtime boundary used by forms and persisted UI state.
 * Unanswered questions are omitted; every supplied answer must be boolean.
 */
export function validateUserAnswers(input: unknown): asserts input is UserAnswers {
  if (typeof input !== "object" || input === null || Array.isArray(input)) {
    throw new EvidenceMapperError("User answers must be an object.");
  }

  for (const [questionId, answer] of Object.entries(input)) {
    if (!QUESTIONS_BY_ID.has(questionId)) {
      throw new EvidenceMapperError(
        `Unknown question identifier: ${JSON.stringify(questionId)}.`,
        questionId,
      );
    }
    if (typeof answer !== "boolean") {
      throw new EvidenceMapperError(
        `Answer for ${JSON.stringify(questionId)} must be boolean.`,
        questionId,
      );
    }
  }
}

/** Accepts Spanish yes/no text at the boundary and returns boolean UI answers. */
export function normalizeUserAnswers(input: unknown): UserAnswers {
  if (typeof input !== "object" || input === null || Array.isArray(input)) {
    throw new EvidenceMapperError("User answers must be an object.");
  }

  const answers: Partial<Record<QuestionId, boolean>> = {};
  for (const [questionId, value] of Object.entries(input)) {
    if (!QUESTIONS_BY_ID.has(questionId)) {
      throw new EvidenceMapperError(
        `Unknown question identifier: ${JSON.stringify(questionId)}.`,
        questionId,
      );
    }
    let answer = value;
    if (typeof answer === "string") {
      const text = answer.normalize("NFC").trim().toLowerCase();
      if (text === "sí" || text === "si") answer = true;
      else if (text === "no") answer = false;
    }
    if (typeof answer !== "boolean") {
      throw new EvidenceMapperError(
        `Answer for ${JSON.stringify(questionId)} must be boolean or Spanish sí/si/no text.`,
        questionId,
      );
    }
    answers[questionId as QuestionId] = answer;
  }
  return answers;
}

/** Normalizes UI answers into evidence accepted by the inference engine. */
export function mapAnswersToEvidence(input: unknown): Evidence {
  const answers = normalizeUserAnswers(input);

  const evidence: Record<string, string> = {};
  for (const [questionId, answer] of Object.entries(answers)) {
    const question = QUESTIONS_BY_ID.get(questionId)!;
    evidence[question.variable] = answer ? "Yes" : "No";
  }
  return evidence;
}
