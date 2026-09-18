import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  loadModel,
  loadModelFromJson,
  ModelValidationError,
} from "../src/index.ts";

const MODEL_URL = new URL("../../model-export/model.json", import.meta.url);
const MODEL_JSON = readFileSync(MODEL_URL, "utf8");

test("loads the frozen Section 2 model", () => {
  const model = loadModelFromJson(MODEL_JSON);
  assert.equal(model.modelVersion, "1.0.0");
  assert.equal(model.nodes.length, 11);
  assert.equal(model.edges.length, 7);
  assert.equal(model.cpts.length, 11);
  assert.equal(model.topologicalOrder.length, 11);
});

test("rejects a cyclic model", () => {
  const raw = JSON.parse(MODEL_JSON);
  raw.edges.push({
    source: "Q4_Gastronomic_Heritage",
    target: "Q1_Traditional_Mexican",
  });
  assert.throws(() => loadModel(raw), ModelValidationError);
});

test("rejects duplicate edges", () => {
  const raw = JSON.parse(MODEL_JSON);
  raw.edges.push({ ...raw.edges[0] });
  assert.throws(() => loadModel(raw), /Duplicate edge/);
});

test("rejects a non-normalized CPT", () => {
  const raw = JSON.parse(MODEL_JSON);
  raw.cpts[0].values[0][0] = 0.9;
  assert.throws(() => loadModel(raw), /not normalized/);
});
