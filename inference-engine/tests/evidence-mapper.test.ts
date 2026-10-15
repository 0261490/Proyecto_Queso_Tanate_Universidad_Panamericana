import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  loadModelFromJson,
  QUESTION_CATALOG,
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
});

test("uses natural Spanish prompts backed by variables in the frozen model", () => {
  for (const question of QUESTION_CATALOG) {
    assert.ok(question.prompt.startsWith("¿"));
    assert.ok(question.prompt.endsWith("?"));
    assert.ok(model.nodes.some(({ id }) => id === question.variable));
  }
});
