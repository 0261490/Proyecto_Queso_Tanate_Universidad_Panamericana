import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { IDBFactory } from "fake-indexeddb";
import { ExactInferenceEngine, loadModelFromJson, mapAnswersToEvidence } from "../../inference-engine/src/index.ts";
import { HistoryStore } from "../src/storage/history.ts";
import { formatProbability } from "../src/presentation.ts";

const bytes = readFileSync(new URL("../../model-export/model.json", import.meta.url));
const fixture = JSON.parse(readFileSync(new URL("../../inference-engine/tests/fixtures/assessment-reference.json", import.meta.url), "utf8"));
const engine = new ExactInferenceEngine(loadModelFromJson(bytes.toString("utf8")));

test("golden questionnaire corpus is complete, independent and tied to the frozen model", () => {
  assert.equal(fixture.generator, "pgmpy VariableElimination");
  assert.equal(fixture.model_sha256, createHash("sha256").update(bytes).digest("hex"));
  assert.equal(fixture.tolerance, 1e-12);
  assert.equal(fixture.cases.length, 128);
  assert.equal(new Set(fixture.cases.map(c => c.id)).size, 128);
  assert.equal(new Set(fixture.cases.map(c => JSON.stringify(c.answers))).size, 128);
  for (const c of fixture.cases) {
    assert.equal(Object.keys(c.answers).length, 7);
    assert.ok(Object.values(c.answers).every(v => typeof v === "boolean"));
  }
});

test("all 128 Python golden cases survive translator, inference and persistent history", async t => {
  const factory = new IDBFactory();
  const store = new HistoryStore(factory);
  let maximumError = 0;
  for (const c of fixture.cases) {
    const evidence = mapAnswersToEvidence(c.answers);
    assert.deepEqual(evidence, c.evidence, c.id);
    const probability = engine.probability("Q2_Purchase_Intention", "Yes", evidence);
    const error = Math.abs(probability - c.probability);
    maximumError = Math.max(error, maximumError);
    assert.ok(error < fixture.tolerance, `${c.id}: error ${error}`);
    await store.add({ schemaVersion: 1, id: c.id, createdAt: "2026-11-20T12:00:00.000Z",
      model: { version: fixture.model_version, sha256: fixture.model_sha256 },
      answers: c.answers, evidence, result: { variable: "Q2_Purchase_Intention", state: "Yes", probability } });
  }
  const saved = await new HistoryStore(factory).list();
  assert.equal(saved.length, 128);
  for (const actual of saved) {
    const c = fixture.cases.find(c => c.id === actual.id);
    assert.deepEqual(actual.answers, c.answers);
    assert.deepEqual(actual.evidence, c.evidence);
    assert.ok(Math.abs(actual.result.probability - c.probability) < fixture.tolerance);
    assert.equal(formatProbability(actual.result.probability), formatProbability(c.probability));
  }
  t.diagnostic(`128 cases; maximum absolute Python/TypeScript error: ${maximumError}`);
});

test("publication reference 62.6% is reported as a scientific difference, not forced", t => {
  const reference = fixture.scientific_reference;
  const actual = engine.probability("Q2_Purchase_Intention", "Yes", { Q8_Sensory_Uniqueness: "Yes" });
  assert.equal(reference.published_probability, 0.626);
  assert.equal(reference.status, "documented_difference_not_exact_recovery");
  assert.ok(Math.abs(actual - reference.reconstructed_probability) < fixture.tolerance);
  assert.ok(Math.abs(actual - 101 / 169) < fixture.tolerance);
  assert.ok(Math.abs(actual - reference.published_probability) > 0.02);
  t.diagnostic(`Published: 62.6%; reconstructed: ${actual * 100}%; delta: ${(actual - 0.626) * 100} percentage points`);
});
