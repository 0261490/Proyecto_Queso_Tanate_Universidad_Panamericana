import assert from "node:assert/strict";
import test from "node:test";

import { QUESTION_CATALOG } from "../../inference-engine/src/index.ts";
import {
  formatProbability,
  interpretProbability,
  renderQuestion,
} from "../src/presentation.ts";

test("renders a natural-language, accessible question without model identifiers", () => {
  const question = QUESTION_CATALOG[0];
  const markup = renderQuestion(question, 0, 7);

  assert.match(markup, /<fieldset/);
  assert.match(markup, /<legend>/);
  assert.ok(markup.includes(question.prompt));
  assert.match(markup, /type="radio"/);
  assert.match(markup, />Sí</);
  assert.match(markup, />No</);
  assert.doesNotMatch(markup, /Q[1-8](?:_|\b)/);
  assert.doesNotMatch(markup, new RegExp(question.variable));
});

test("formats probabilities for Spanish readers", () => {
  assert.equal(formatProbability(0), "0 %");
  assert.equal(formatProbability(0.597633), "59.8 %");
  assert.equal(formatProbability(1), "100 %");
});

test("uses stable, non-diagnostic interpretation bands", () => {
  assert.match(interpretProbability(0.1), /baja/);
  assert.match(interpretProbability(0.25), /moderada/);
  assert.match(interpretProbability(0.5), /favorable/);
  assert.match(interpretProbability(0.75), /alta/);
});
