import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  ExactInferenceEngine,
  InferenceError,
  loadModelFromJson,
} from "../src/index.ts";

const model = loadModelFromJson(
  readFileSync(new URL("../../model-export/model.json", import.meta.url), "utf8"),
);
const engine = new ExactInferenceEngine(model);

test("computes the exact Q2 marginal", () => {
  const result = engine.query("Q2_Purchase_Intention");
  assert.deepEqual(result.states, ["No", "Yes"]);
  assert.ok(Math.abs(result.probabilities[1] - 101 / 169) < 1e-15);
  assert.ok(Math.abs(result.probabilities.reduce((a, b) => a + b, 0) - 1) < 1e-15);
});

test("isolated Q8 evidence does not change Q2", () => {
  const prior = engine.probability("Q2_Purchase_Intention", "Yes");
  const posterior = engine.probability(
    "Q2_Purchase_Intention",
    "Yes",
    { Q8_Sensory_Uniqueness: "Yes" },
  );
  assert.ok(Math.abs(prior - posterior) < 1e-15);
});

test("observed query variable produces a degenerate posterior", () => {
  const result = engine.query("Q2_Purchase_Intention", {
    Q2_Purchase_Intention: "Yes",
  });
  assert.deepEqual(result.probabilities, [0, 1]);
});

test("computes a valid probability of evidence", () => {
  const probability = engine.probabilityOfEvidence({
    Q3_Recommendation: "Yes",
    Q5_Authenticity_Elaboration: "Yes",
  });
  assert.ok(probability > 0 && probability <= 1);
});

test("rejects unknown variables and states", () => {
  assert.throws(() => engine.query("Unknown"), InferenceError);
  assert.throws(
    () => engine.query("Q2_Purchase_Intention", { Q8_Sensory_Uniqueness: "Maybe" }),
    /Unknown state/,
  );
});

test("rejects impossible evidence even when the query variable is observed", () => {
  const deterministic = loadModelFromJson(JSON.stringify({
    format: "proyecto-tenate-bayesian-model",
    schema_version: 1,
    model_version: "test",
    metadata: {},
    nodes: [{ id: "A", states: ["No", "Yes"] }],
    edges: [],
    cpts: [{
      node: "A",
      parents: [],
      state_names: { A: ["No", "Yes"] },
      values: [[1], [0]],
    }],
  }));
  const deterministicEngine = new ExactInferenceEngine(deterministic);

  assert.throws(
    () => deterministicEngine.query("A", { A: "Yes" }),
    /zero or invalid probability/,
  );
});
