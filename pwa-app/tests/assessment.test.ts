import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { ExactInferenceEngine, loadModel, QUESTION_CATALOG, mapAnswersToEvidence } from "../../inference-engine/src/index.ts";

const model = loadModel(JSON.parse(readFileSync(new URL("../../model-export/model.json", import.meta.url), "utf8")));
const engine = new ExactInferenceEngine(model);

test("preserves the seven-question process and its documented two-value limitation", () => {
  const questions = QUESTION_CATALOG.filter(q => q.id !== "purchaseIntention");
  assert.equal(questions.length, 7);
  const counts = { yes: 0, no: 0 };
  for (let mask = 0; mask < 128; mask++) {
    const answers = Object.fromEntries(questions.map((q, i) => [q.id, Boolean(mask & (1 << i))]));
    const evidence = mapAnswersToEvidence(answers);
    assert.equal(Object.keys(evidence).length, 7);
    assert.ok(!Object.hasOwn(evidence, "Q2_Purchase_Intention"));
    const result = engine.probability("Q2_Purchase_Intention", "Yes", evidence);
    // Independent empirical conditionals from the frozen dataset, not UI constants.
    assert.ok(Math.abs(result - (answers.recommendation ? 96 / 118 : 5 / 51)) < 1e-12);
    counts[answers.recommendation ? "yes" : "no"]++;
  }
  assert.deepEqual(counts, { yes: 64, no: 64 });
});
