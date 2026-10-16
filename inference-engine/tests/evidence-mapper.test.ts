import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  ExactInferenceEngine,
  EvidenceMapperError,
  loadModelFromJson,
  mapAnswersToEvidence,
  normalizeUserAnswers,
  QUESTION_CATALOG,
  validateUserAnswers,
} from "../src/index.ts";

const model = loadModelFromJson(
  readFileSync(new URL("../../model-export/model.json", import.meta.url), "utf8"),
);

test("publishes one unique mapping for every Q1-Q8 model variable", () => {
  assert.equal(QUESTION_CATALOG.length, 8);
  assert.equal(new Set(QUESTION_CATALOG.map(({ id }) => id)).size, 8);
  assert.equal(new Set(QUESTION_CATALOG.map(({ variable }) => variable)).size, 8);
  assert.deepEqual(
    QUESTION_CATALOG.map(({ variable }) => variable),
    [
      "Q1_Traditional_Mexican",
      "Q2_Purchase_Intention",
      "Q3_Recommendation",
      "Q4_Gastronomic_Heritage",
      "Q5_Authenticity_Elaboration",
      "Q6_Commercial_Potential",
      "Q7_Culture_Preservation",
      "Q8_Sensory_Uniqueness",
    ],
  );
  for (const question of QUESTION_CATALOG) {
    assert.ok(question.prompt.startsWith("¿"));
    assert.ok(question.prompt.endsWith("?"));
    assert.ok(model.nodes.some(({ id }) => id === question.variable));
  }
});

test("maps yes and no UI answers to canonical model states", () => {
  assert.deepEqual(
    mapAnswersToEvidence({
      traditionalMexican: true,
      authenticElaboration: false,
      sensoryUniqueness: true,
    }),
    {
      Q1_Traditional_Mexican: "Yes",
      Q5_Authenticity_Elaboration: "No",
      Q8_Sensory_Uniqueness: "Yes",
    },
  );
});

test("allows partial and empty answer sets", () => {
  assert.deepEqual(mapAnswersToEvidence({}), {});
  assert.deepEqual(mapAnswersToEvidence({ commercialPotential: false }), {
    Q6_Commercial_Potential: "No",
  });
});

test("rejects non-object input", () => {
  for (const value of [null, undefined, true, "yes", [], 1]) {
    assert.throws(() => mapAnswersToEvidence(value), EvidenceMapperError);
  }
});

test("rejects unknown question identifiers", () => {
  assert.throws(
    () => mapAnswersToEvidence({ q8: true }),
    (error: unknown) => {
      assert.ok(error instanceof EvidenceMapperError);
      assert.equal(error.questionId, "q8");
      assert.match(error.message, /Unknown question identifier/);
      return true;
    },
  );
});

test("rejects missing and unsupported answers", () => {
  for (const answer of [undefined, null, "Yes", "", "quizá", "true", "false", {}, [], 1, 0]) {
    assert.throws(
      () => mapAnswersToEvidence({ recommendation: answer }),
      /must be boolean/,
    );
  }
});

test("normalizes Spanish text including case, whitespace and Unicode accents", () => {
  for (const answer of ["sí", "si", "Sí", " SI ", "SÍ", "si\u0301"]) {
    assert.deepEqual(normalizeUserAnswers({ recommendation: answer }), { recommendation: true });
    assert.deepEqual(mapAnswersToEvidence({ recommendation: answer }), { Q3_Recommendation: "Yes" });
  }
  for (const answer of ["no", "No", " NO "]) {
    assert.deepEqual(normalizeUserAnswers({ recommendation: answer }), { recommendation: false });
    assert.deepEqual(mapAnswersToEvidence({ recommendation: answer }), { Q3_Recommendation: "No" });
  }
});

test("normalization preserves booleans and does not mutate input", () => {
  const input = Object.freeze({ recommendation: "sí", authenticElaboration: false });
  assert.deepEqual(normalizeUserAnswers(input), { recommendation: true, authenticElaboration: false });
  assert.equal(input.recommendation, "sí");
  assert.deepEqual(normalizeUserAnswers({}), {});
  assert.throws(() => normalizeUserAnswers({ recommendation: "quizá" }), (error: unknown) => {
    assert.ok(error instanceof EvidenceMapperError);
    assert.equal(error.questionId, "recommendation");
    return true;
  });
});

test("exposes validation independently from mapping", () => {
  const input: unknown = { purchaseIntention: true };
  assert.doesNotThrow(() => validateUserAnswers(input));
  assert.throws(
    () => validateUserAnswers({ purchaseIntention: "yes" }),
    EvidenceMapperError,
  );
});

test("produces evidence accepted directly by the inference engine", () => {
  const engine = new ExactInferenceEngine(model);
  const evidence = mapAnswersToEvidence({
    recommendation: true,
    authenticElaboration: false,
  });

  assert.doesNotThrow(() => engine.query("Q2_Purchase_Intention", evidence));
});
