import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";

import { ExactInferenceEngine, loadModelFromJson } from "../src/index.ts";
import type { Evidence } from "../src/index.ts";

interface ReferenceCase {
  readonly id: string;
  readonly variable: string;
  readonly evidence: Evidence;
  readonly states: readonly string[];
  readonly probabilities: readonly number[];
}

interface ReferenceFixture {
  readonly generator: string;
  readonly model_sha256: string;
  readonly cases: readonly ReferenceCase[];
}

const modelBytes = readFileSync(new URL("../../model-export/model.json", import.meta.url));
const model = loadModelFromJson(modelBytes.toString("utf8"));
const engine = new ExactInferenceEngine(model);
const fixture = JSON.parse(
  readFileSync(new URL("./fixtures/python-reference.json", import.meta.url), "utf8"),
) as ReferenceFixture;

test("fixture is tied to the frozen Section 2 model", () => {
  assert.equal(
    fixture.model_sha256,
    createHash("sha256").update(modelBytes).digest("hex"),
  );
  assert.equal(fixture.generator, "pgmpy VariableElimination");
});

for (const reference of fixture.cases) {
  test(`matches Python reference: ${reference.id}`, () => {
    const actual = engine.query(reference.variable, reference.evidence);
    assert.deepEqual(actual.states, reference.states);
    assert.equal(actual.probabilities.length, reference.probabilities.length);
    for (let index = 0; index < reference.probabilities.length; index += 1) {
      assert.ok(
        Math.abs(actual.probabilities[index] - reference.probabilities[index]) < 1e-12,
        `${reference.id} state ${reference.states[index]}: ` +
          `${actual.probabilities[index]} != ${reference.probabilities[index]}`,
      );
    }
  });
}
