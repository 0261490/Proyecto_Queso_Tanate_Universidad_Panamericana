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

test("rejects malformed JSON and unsupported model contracts", () => {
  assert.throws(() => loadModelFromJson("{broken"), /Invalid model JSON/);
  assert.throws(() => loadModelFromJson("null"), ModelValidationError);
  for (const change of [
    raw => { raw.format = "other"; },
    raw => { raw.schema_version = 2; },
    raw => { raw.model_version = ""; },
    raw => { raw.metadata = null; },
    raw => { raw.nodes = []; },
    raw => { raw.edges = null; },
  ]) {
    const raw = JSON.parse(MODEL_JSON);
    change(raw);
    assert.throws(() => loadModel(raw), ModelValidationError);
  }
});

test("rejects ambiguous states, duplicate nodes and unknown dependencies", () => {
  for (const change of [
    raw => { raw.nodes.push(raw.nodes[0]); },
    raw => { raw.nodes[0].states = []; },
    raw => { raw.nodes[0].states.push(raw.nodes[0].states[0]); },
    raw => { raw.edges[0].source = "unknown"; },
    raw => { raw.cpts.pop(); },
    raw => { raw.cpts[1] = raw.cpts[0]; },
  ]) {
    const raw = JSON.parse(MODEL_JSON);
    change(raw);
    assert.throws(() => loadModel(raw), ModelValidationError);
  }
});

test("rejects CPT axes inconsistent with the scientific graph and state order", () => {
  for (const change of [
    cpt => { cpt.parents = null; },
    cpt => { cpt.parents.push(cpt.parents[0]); },
    cpt => { cpt.parents = []; },
    cpt => { cpt.state_names[cpt.node].reverse(); },
    cpt => { cpt.state_names[cpt.parents[0]].reverse(); },
    cpt => { cpt.values.pop(); },
    cpt => { cpt.values[0].pop(); },
  ]) {
    const raw = JSON.parse(MODEL_JSON);
    change(raw.cpts.find(c => c.parents.length > 0));
    assert.throws(() => loadModel(raw), ModelValidationError);
  }
});

test("rejects out-of-range, nonnumeric and nonfinite probabilities", () => {
  for (const value of [-0.01, 1.01, "0.5", null, NaN, Infinity]) {
    const raw = JSON.parse(MODEL_JSON);
    raw.cpts[0].values[0][0] = value;
    assert.throws(() => loadModel(raw), /not a probability/);
  }
});
