import assert from "node:assert/strict";
import test from "node:test";
import { IDBFactory } from "fake-indexeddb";
import { QUESTION_CATALOG, mapAnswersToEvidence } from "../../inference-engine/src/index.ts";
import { HistoryStore, type AssessmentRecord } from "../src/storage/history.ts";

function record(id = "first", createdAt = "2026-11-17T12:00:00.000Z"): AssessmentRecord {
  const answers = Object.fromEntries(QUESTION_CATALOG.filter(q => q.id !== "purchaseIntention").map(q => [q.id, true]));
  return { schemaVersion: 1, id, createdAt, model: { version: "1.0.0", sha256: "a".repeat(64) }, answers,
    evidence: mapAnswersToEvidence(answers), result: { variable: "Q2_Purchase_Intention", state: "Yes", probability: 96 / 118 } };
}

test("persists independent snapshots and reads newest first after reopening", async () => {
  const factory = new IDBFactory();
  const store = new HistoryStore(factory);
  assert.deepEqual(await store.list(), []);
  const original = record();
  const save = store.add(original);
  original.result.probability = 0;
  await save;
  await store.add(record("second", "2026-11-17T13:00:00.000Z"));
  const reopened = new HistoryStore(factory);
  const records = await reopened.list();
  assert.deepEqual(records.map(r => r.id), ["second", "first"]);
  assert.equal(records[1].result.probability, 96 / 118);
  assert.deepEqual(records[1].answers, record().answers);
  assert.deepEqual(records[1].evidence, record().evidence);
  records[1].answers.recommendation = false;
  assert.equal((await reopened.list())[1].answers.recommendation, true);
});

test("rejects duplicate IDs without overwriting and deletes only selected records", async () => {
  const store = new HistoryStore(new IDBFactory());
  await store.add(record());
  const duplicate = record();
  duplicate.result.probability = 0.5;
  await assert.rejects(store.add(duplicate));
  assert.equal((await store.list())[0].result.probability, 96 / 118);
  await store.add(record("second"));
  await store.delete("first");
  assert.deepEqual((await store.list()).map(r => r.id), ["second"]);
  await store.clear();
  assert.deepEqual(await store.list(), []);
});

test("invalid snapshots never reach storage", async () => {
  const store = new HistoryStore(new IDBFactory());
  for (const alter of [
    (r: AssessmentRecord) => { r.result.probability = NaN; },
    (r: AssessmentRecord) => { r.result.probability = 1.1; },
    (r: AssessmentRecord) => { delete r.answers.recommendation; },
    (r: AssessmentRecord) => { r.evidence.Q3_Recommendation = "No"; },
    (r: AssessmentRecord) => { r.createdAt = "invalid"; },
    (r: AssessmentRecord) => { r.model.sha256 = "unknown"; },
  ]) {
    const input = record();
    alter(input);
    await assert.rejects(store.add(input));
  }
  assert.deepEqual(await store.list(), []);
});

test("unavailable storage rejects cleanly", async () => {
  const store = new HistoryStore(undefined);
  await assert.rejects(store.list(), /unavailable/);
  await assert.rejects(store.add(record()), /unavailable/);
});

test("an aborted write is never reported as saved", async () => {
  const factory = new IDBFactory();
  const realOpen = factory.open.bind(factory);
  factory.open = (...args) => {
    const request = realOpen(...args);
    request.addEventListener("success", () => {
      const db = request.result;
      const original = db.transaction.bind(db);
      db.transaction = (...txArgs) => {
        const tx = original(...txArgs);
        if (txArgs[1] === "readwrite") queueMicrotask(() => tx.abort());
        return tx;
      };
    });
    return request;
  };
  const store = new HistoryStore(factory);
  await assert.rejects(store.add(record()), /aborted/);
  assert.deepEqual(await store.list(), []);
});

test("clearing history does not remove other stores or databases", async () => {
  const factory = new IDBFactory();
  const first = new HistoryStore(factory, "first-db");
  const second = new HistoryStore(factory, "second-db");
  await first.add(record());
  await second.add(record());
  await first.clear();
  assert.equal((await second.list()).length, 1);
});
